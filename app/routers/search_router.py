# app/routers/search_router.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchApiRequest, SearchApiResponse
from app.core.search_agent import run_search_pipeline

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=SearchApiResponse)
async def perform_search_endpoint(request: SearchApiRequest) -> SearchApiResponse:
    """
    Endpoint to perform search by orchestrating the search pipeline.
    """
    try:
        print(f"Received search request for user {request.user_id} with query: {request.query}")
        pipeline_output = await run_search_pipeline(
            user_id=request.user_id,
            raw_query=request.query
        )
        return SearchApiResponse(
            query_received=request.query,
            user_id=request.user_id,
            search_results=pipeline_output.get("search_results", []),
            message=pipeline_output.get("message", "Search initiated.")
        )
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal search error.")


# app/core/search_agent.py
from typing import List, Optional, Dict, Any
from app.services.history_service import get_recent_history_summary
from app.services.cart_service import get_cart_details_for_llm_context


async def run_search_pipeline(
    user_id: str,
    raw_query: str
) -> Dict[str, Any]:
    """
    Orchestrates the search pipeline: gathers context, then will refine query,
    match categories, retrieve and rank products.

    Part 6.A: Initial user input and context gathering.
    """
    print(f"Starting search pipeline for user {user_id} and query '{raw_query}'")

    # Step 6.1: Gather user history context
    user_history_summary: str = await get_recent_history_summary(
        user_id=user_id,
        num_interactions=3
    )
    print(f"Retrieved user history summary: {user_history_summary}")

    # Step 6.1: Gather cart context
    user_cart_summary: str = await get_cart_details_for_llm_context(user_id=user_id)
    print(f"Retrieved user cart summary: {user_cart_summary}")

    # Placeholder for subsequent steps
    # Step 6.2: LLM Query Refinement & Feature Extraction - To be implemented
    # Step 6.3: Semantic Category Matching - To be implemented
    # Step 6.4: MongoDB Candidate Retrieval - To be implemented
    # Step 6.5: Automated Fallback (Conditional) - To be implemented
    # Step 6.6: LLM Product-Level Re-ranking & Response Generation - To be implemented
    # Step 6.7: Logging Interaction - To be implemented

    return {
        "search_results": [],
        "message": (
            f"Context for user '{user_id}': History='{user_history_summary}'; "
            f"Cart='{user_cart_summary}'. Query: '{raw_query}'. Subsequent steps pending."
        )
    }


