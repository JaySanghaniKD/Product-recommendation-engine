from typing import List, Optional, Dict, Any, Set

from fastapi.concurrency import run_in_threadpool
from app.services.history_service import get_recent_history_summary
from app.services.cart_service import get_cart_details_for_llm_context
from app.models.schemas import (
    LLMQueryAnalysisOutput,
    LLMFinalProductSelectionOutput,
    SearchApiResponseProduct,
    ProductStored
)
from app.db.llm_clients import get_llm_client, get_embedding_model
from app.db.vector_store import get_pinecone_category_index
from app.db.database import get_products_collection
from pymongo.collection import Collection
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
import pinecone
import os

# Disable LangSmith if URL is not correctly formatted
if os.getenv("LANGCHAIN_ENDPOINT", "").startswith("https_"):
    os.environ["LANGCHAIN_TRACING_V2"] = "false"


async def refine_query_with_llm1(
    raw_query: str,
    user_history_summary: str,
    user_cart_summary: str
) -> Optional[LLMQueryAnalysisOutput]:
    """
    Uses an LLM to analyze the user's query and context, extracting descriptive category phrases,
    filter criteria, and a user intent summary as structured output.
    """
    try:
        llm = get_llm_client()
        output_parser = PydanticOutputParser(pydantic_object=LLMQueryAnalysisOutput)
        
        # Define format instructions manually to avoid potential issues with schema generation
        format_instructions = """
{
  "descriptive_category_phrases": ["phrase1", "phrase2", ...],
  "filter_criteria": {
    "price_min": 100,  // optional
    "price_max": 500,  // optional
    "brand": "BrandName" or ["Brand1", "Brand2"],  // optional
    "keywords_for_db_search": ["keyword1", "keyword2", ...]  // optional
  },
  "extracted_tags": ["tag1", "tag2", ...],  // optional
  "user_intent_summary": "A brief description of the user's shopping intent"
}
        """

        system_template = SystemMessagePromptTemplate.from_template(
            """
            You are an intelligent assistant helping users discover products. Your goal is to analyze the user's query,
            their recent interaction history, and current cart details to understand their needs comprehensively.
            Based on this analysis, you must:
            1. Generate 1 to 3 concise 'descriptive_category_phrases'. These phrases should capture the essence of the product types
               or categories the user is looking for. Examples: "comfortable running shoes for marathons",
               "modern kitchen appliances for a new home", "educational toys for toddlers".
            2. Identify specific 'filter_criteria' the user might have mentioned or implied. This should be a dictionary.
               Supported filter keys are: 'price_min' (float), 'price_max' (float), 'brand' (str or List[str]),
               'keywords_for_db_search' (List[str] of specific attributes or terms like "waterproof", "organic", "bluetooth").
               If no specific criteria are found for a key, omit it.
            3. Optionally provide 'extracted_tags' that might be useful for search.
            4. Provide a brief 'user_intent_summary' (1-2 sentences) summarizing what the user is trying to achieve.

            Respond ONLY with a JSON object formatted like this:
            {format_instructions}
            """
        ).format(format_instructions=format_instructions)
        
        human_template = HumanMessagePromptTemplate.from_template(
            """
            User's Raw Query: "{raw_query}"
            Recent User History: "{user_history_summary}"
            Current User Cart: "{user_cart_summary}"

            Please analyze and provide the structured JSON output.
            """
        )

        prompt = ChatPromptTemplate.from_messages([system_template, human_template])
        
        # Use modern pattern instead of deprecated LLMChain
        chain = prompt | llm | output_parser
        
        response = await chain.ainvoke({
            "raw_query": raw_query,
            "user_history_summary": user_history_summary,
            "user_cart_summary": user_cart_summary,
        })
        
        print(f"LLMQueryAnalysisOutput: {response.model_dump_json(indent=2)}")
        return response
    except Exception as e:
        print(f"Error in refine_query_with_llm1: {e}")
        # Provide a fallback response when LLM fails
        return LLMQueryAnalysisOutput(
            descriptive_category_phrases=[raw_query.strip()],
            filter_criteria={
                "keywords_for_db_search": [word for word in raw_query.split() if len(word) > 3]
            },
            user_intent_summary=f"User wants to find: {raw_query}"
        )


async def match_semantic_categories(
    descriptive_category_phrases: List[str],
    top_k_categories: int = 1
) -> List[str]:
    """
    Embeds descriptive phrases and queries the Pinecone category index to return matched categories.
    """
    try:
        embedding_model = get_embedding_model()
        category_index = get_pinecone_category_index()
        matched: Set[str] = set()
        for phrase in descriptive_category_phrases:
            phrase_embedding = await embedding_model.aembed_query(phrase)
            response = await run_in_threadpool(
                category_index.query,
                vector=phrase_embedding,
                top_k=top_k_categories,
                include_metadata=True
            )
            for match in response.matches:
                name = match.metadata.get("category_name")
                if name:
                    matched.add(name)
        return list(matched)
    except Exception as e:
        print(f"Error in match_semantic_categories: {e}")
        return []


async def _trigger_fallback_search(
    llm_analysis: LLMQueryAnalysisOutput,
    products_collection: Collection,
    fallback_candidate_limit: int = 20
) -> List[ProductStored]:
    """
    Performs a broader text search using keywords extracted by the LLM if initial search yields few results.
    Requires a text index on title, description, or tags in MongoDB for $text search to work.
    """
    try:
        print("Triggering fallback search...")
        criteria = llm_analysis.filter_criteria or {}
        keywords = criteria.get("keywords_for_db_search")
        if not keywords:
            print("No keywords available for fallback search.")
            return []
        # Construct text search query (requires pre-existing text index)
        search_string = " ".join(keywords)
        mongo_fallback_query = {"$text": {"$search": search_string}}
        cursor = products_collection.find(mongo_fallback_query).limit(fallback_candidate_limit)
        docs = await run_in_threadpool(list, cursor)
        fallback_results: List[ProductStored] = []
        for doc in docs:
            try:
                fallback_results.append(ProductStored.model_validate(doc))
            except Exception:
                continue
        print(f"Fallback search found {len(fallback_results)} candidates.")
        return fallback_results
    except Exception as e:
        print(f"Error in _trigger_fallback_search: {e}")
        return []



async def retrieve_candidates_from_mongodb(
    matched_categories: List[str],
    filter_criteria: Optional[Dict[str, Any]],
    candidate_limit: int = 20
) -> List[ProductStored]:
    """
    Retrieves candidate products from MongoDB based on category and filter criteria.
    """
    try:
        products_col = get_products_collection()
        mongo_query: Dict[str, Any] = {}
        if matched_categories:
            mongo_query["category"] = {"$in": matched_categories}
        if filter_criteria:
            price_cond: Dict[str, Any] = {}
            if filter_criteria.get("price_min") is not None:
                price_cond["$gte"] = float(filter_criteria["price_min"])
            if filter_criteria.get("price_max") is not None:
                price_cond["$lte"] = float(filter_criteria["price_max"])
            if price_cond:
                mongo_query["price"] = price_cond
            brand = filter_criteria.get("brand")
            if brand:
                if isinstance(brand, list):
                    mongo_query["brand"] = {"$in": brand}
                else:
                    mongo_query["brand"] = brand
            keywords = filter_criteria.get("keywords_for_db_search")
            if keywords:
                mongo_query["$text"] = {"$search": " ".join(keywords)}
        if not mongo_query:
            return []
        cursor = products_col.find(mongo_query).limit(candidate_limit)
        docs = await run_in_threadpool(list, cursor)
        results: List[ProductStored] = []
        for doc in docs:
            try:
                results.append(ProductStored.model_validate(doc))
            except Exception:
                continue
        return results
    except Exception as e:
        print(f"Error in retrieve_candidates_from_mongodb: {e}")
        return []

async def rerank_and_select_products_with_llm2(
    raw_query: str,
    user_history_summary: str,
    user_cart_summary: str,
    candidate_products: List[ProductStored],
    top_n_final: int = 3
) -> Optional[LLMFinalProductSelectionOutput]:
    """
    Uses an LLM to re-rank candidate products, select top N, and provide justifications.
    """
    if not candidate_products:
        print("No candidate products to re-rank.")
        return None
    try:
        llm = get_llm_client()
        output_parser = PydanticOutputParser(pydantic_object=LLMFinalProductSelectionOutput)

        # Prepare candidate product details for prompt
        max_candidates_for_llm = min(len(candidate_products), 10)
        product_details_for_prompt = []
        for i, p in enumerate(candidate_products[:max_candidates_for_llm]):
            tags_str = ", ".join(p.tags) if p.tags else "N/A"
            desc = p.description or ""
            desc_summary = (desc[:200] + "...") if len(desc) > 200 else desc
            info = f"Product {i+1} (ID: {p.id}):\n" \
                   f"  Title: {p.title}\n" \
                   f"  Category: {p.category}\n" \
                   f"  Brand: {getattr(p, 'brand', 'N/A')}\n" \
                   f"  Price: ${p.price:.2f}\n" \
                   f"  Description Summary: {desc_summary}\n" \
                   f"  Tags: {tags_str}\n" \
                   f"  Thumbnail: {p.thumbnail}\n"
            product_details_for_prompt.append(info)
        candidate_product_details_string = "".join(product_details_for_prompt) or "No candidate products provided."

        # Define format instructions manually to avoid potential issues with schema generation
        format_instructions = """
{
  "ranked_products": [
    {
      "product_id": 123,
      "title": "Product Name",
      "price": 99.99,
      "thumbnail": "http://example.com/image.jpg",
      "justification": "This product matches the user's needs because...",
      "rank": 1
    }
  ],
  "overall_summary": "These products were selected because they match the user's requirements for..."
}
        """

        # Build prompt
        system_msg = SystemMessagePromptTemplate.from_template(
            """
            You are an expert AI shopping assistant. Your task is to meticulously review a list of
            candidate products and select the few that BEST match the user's query and their provided
            context (history and cart). For each product you select, provide a concise justification
            explaining why it's an excellent match and assign a rank.
            """
        )
        human_msg = HumanMessagePromptTemplate.from_template(
            """
            User's Original Query: "{raw_query}"
            User's Recent Interaction History: "{user_history_summary}"
            User's Current Cart Contents: "{user_cart_summary}"

            Here is a list of candidate products:
            ---
            {candidate_product_details_string}
            ---

            Select the top {top_n_final} most relevant products. For each, provide:
            - product_id (integer)
            - title (string)
            - price (float)
            - thumbnail (string)
            - justification (1-2 sentences)
            - rank (1 for best)
            Optionally, provide an 'overall_summary' (1-2 sentences) for your recommendations.

            Respond ONLY with JSON formatted like this:
            {format_instructions}
            """
        )
        
        prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])
        
        # Use modern pattern instead of deprecated LLMChain
        chain = prompt | llm | output_parser
        
        response = await chain.ainvoke({
            "raw_query": raw_query,
            "user_history_summary": user_history_summary,
            "user_cart_summary": user_cart_summary,
            "candidate_product_details_string": candidate_product_details_string,
            "top_n_final": top_n_final,
            "format_instructions": format_instructions
        })
        
        print(f"LLMFinalProductSelectionOutput: {response.model_dump_json(indent=2)}")
        return response
    except Exception as e:
        print(f"Error in rerank_and_select_products_with_llm2: {e}")
        return None

async def run_search_pipeline(
    user_id: str,
    raw_query: str
) -> Dict[str, Any]:
    """
    Full search pipeline orchestration from context gathering through final response preparation.
    """
    print(f"Starting search pipeline for user {user_id} and query '{raw_query}'")

    # Step 6.1: Gather user context
    user_history_summary = await get_recent_history_summary(user_id=user_id, num_interactions=3)
    print(f"Retrieved user history summary: {user_history_summary}")
    user_cart_summary = await get_cart_details_for_llm_context(user_id=user_id)
    print(f"Retrieved user cart summary: {user_cart_summary}")

    # Step 6.2: LLM Query Refinement & Feature Extraction
    llm_analysis_output = await refine_query_with_llm1(
        raw_query=raw_query,
        user_history_summary=user_history_summary,
        user_cart_summary=user_cart_summary,
    )
    if not llm_analysis_output:
        return {"search_results": [], "message": "Failed to analyze query with LLM. Please try again."}
    print(f"LLM analysis output: {llm_analysis_output.model_dump_json(indent=2)}")

    # Step 6.3: Semantic Category Matching
    matched_categories = await match_semantic_categories(
        descriptive_category_phrases=llm_analysis_output.descriptive_category_phrases,
        top_k_categories=1
    )
    print(f"Matched categories: {matched_categories}")

    # Step 6.4: MongoDB Candidate Retrieval
    candidate_products = await retrieve_candidates_from_mongodb(
        matched_categories=matched_categories,
        filter_criteria=llm_analysis_output.filter_criteria,
        candidate_limit=20
    )
    print(f"Retrieved {len(candidate_products)} candidate products from MongoDB.")

    # Step 6.5: Automated Fallback Search Logic
    MIN_CANDIDATES_BEFORE_FALLBACK = 5
    if len(candidate_products) < MIN_CANDIDATES_BEFORE_FALLBACK:
        print(f"Initial candidate count ({len(candidate_products)}) is below threshold ({MIN_CANDIDATES_BEFORE_FALLBACK}). Triggering fallback search.")
        products_collection_instance = get_products_collection()
        fallback_candidates = await _trigger_fallback_search(
            llm_analysis=llm_analysis_output,
            products_collection=products_collection_instance,
            fallback_candidate_limit=20
        )
        if fallback_candidates:
            print(f"Fallback search found {len(fallback_candidates)} candidates. Using fallback results.")
            candidate_products = fallback_candidates
        else:
            print("Fallback search found no new candidates.")
    else:
        print(f"Initial candidate count ({len(candidate_products)}) is sufficient. No fallback triggered.")
    print(f"Proceeding with {len(candidate_products)} candidate products after fallback check.")

    # Step 6.6: LLM Product-Level Re-ranking & Response Generation
    final_selection_output = await rerank_and_select_products_with_llm2(
        raw_query=raw_query,
        user_history_summary=user_history_summary,
        user_cart_summary=user_cart_summary,
        candidate_products=candidate_products,
        top_n_final=3
    )
    if not final_selection_output or not final_selection_output.ranked_products:
        # Fallback response if re-ranking fails
        api_search_results = []
        message = "Could not refine product selection with LLM."
        return {"query_received": raw_query, "user_id": user_id, "search_results": api_search_results, "message": message}
    print(f"Final selection: {final_selection_output.model_dump_json(indent=2)}")

    # Step 6.7: Logging Search Interaction
    try:
        from app.services.history_service import log_interaction
        from app.models.schemas import SearchInteractionDetail

        interaction_details = SearchInteractionDetail(
            query=raw_query,
            llm_extracted_category_phrases=llm_analysis_output.descriptive_category_phrases,
            matched_pinecone_categories=matched_categories,
            llm_filter_criteria=llm_analysis_output.filter_criteria,
            retrieved_product_ids_from_db=[p.id for p in candidate_products],
            final_ranked_product_ids=[rp.product_id for rp in final_selection_output.ranked_products]
        )
        await log_interaction(
            user_id=user_id,
            interaction_type="search",
            details=interaction_details
        )
        print(f"Search interaction logged for user {user_id}")
    except Exception as e:
        print(f"Error logging search interaction for user {user_id}: {e}")

    # Step 6.8: Preparing Final API Response
    api_search_results: List[Dict[str, Any]] = []
    response_message = "No products found matching your criteria."

    # Build response from LLM ranked products
    for rp in final_selection_output.ranked_products:
        api_search_results.append(
            SearchApiResponseProduct(
                id=rp.product_id,
                title=rp.title,
                description="See product page for details.",  # Placeholder
                category="N/A",  # Placeholder
                price=rp.price,
                thumbnail=rp.thumbnail,
                justification=rp.justification
            ).model_dump()
        )
    response_message = final_selection_output.overall_summary or "Here are your personalized recommendations."

    return {
        "query_received": raw_query,
        "user_id": user_id,
        "search_results": api_search_results,
        "message": response_message
    }