import logging
from typing import List, Optional
from app.models.schemas import SearchApiResponseProduct
from app.services.history_service import get_recent_history_summary
from app.services.cart_service import get_cart_details_for_llm_context
from app.core.search_agent import (
    refine_query_with_llm1, 
    match_semantic_categories, 
    retrieve_candidates_from_mongodb, 
    rerank_and_select_products_with_llm2
)

logger = logging.getLogger(__name__)

async def get_personalized_recommendations(
    user_id: str,
    count: int = 5
) -> List[SearchApiResponseProduct]:
    """
    Get personalized product recommendations for a user based on their history and cart.
    Utilizes the same AI pipeline as search but with an automatically generated query.
    """
    # Get user context
    user_history_summary = await get_recent_history_summary(user_id)
    user_cart_summary = await get_cart_details_for_llm_context(user_id)
    
    # Generate implicit query based on user context
    implicit_query = f"Recommend products for me based on my previous activity"
    if not user_history_summary and not user_cart_summary:
        implicit_query = "Recommend popular products"
    
    # Use the search pipeline components to generate recommendations
    llm_analysis = await refine_query_with_llm1(
        raw_query=implicit_query,
        user_history_summary=user_history_summary,
        user_cart_summary=user_cart_summary
    )
    
    if not llm_analysis:
        logger.error("Failed to analyze user preferences")
        return []
    
    # Match categories
    matched_categories = await match_semantic_categories(
        descriptive_category_phrases=llm_analysis.descriptive_category_phrases,
        top_k_categories=2  # Get more categories for diversity
    )
    
    # Retrieve candidates
    candidate_products = await retrieve_candidates_from_mongodb(
        matched_categories=matched_categories,
        filter_criteria=llm_analysis.filter_criteria,
        candidate_limit=30  # Get more candidates for better selection
    )
    
    if not candidate_products:
        logger.warning("No suitable recommendation candidates found")
        return []
    
    # Rank products
    selection_output = await rerank_and_select_products_with_llm2(
        raw_query=implicit_query,
        user_history_summary=user_history_summary,
        user_cart_summary=user_cart_summary,
        candidate_products=candidate_products,
        top_n_final=count
    )
    
    if not selection_output or not selection_output.ranked_products:
        logger.warning("Could not rank recommendations")
        return []
    
    # Convert to API response format
    recommendations = []
    for product in selection_output.ranked_products:
        recommendations.append(
            SearchApiResponseProduct(
                id=product.product_id,
                title=product.title,
                description="See product page for details.",  # Placeholder
                category="N/A",  # Will be filled from product details
                price=product.price,
                thumbnail=product.thumbnail,
                justification=product.justification
            )
        )
        
    return recommendations
