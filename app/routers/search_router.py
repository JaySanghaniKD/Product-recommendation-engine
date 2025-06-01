# app/routers/search_router.py
import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchApiRequest, SearchApiResponse
from app.core.search_agent import run_search_pipeline

# Initialize logger for this module
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=SearchApiResponse)
async def perform_search_endpoint(request: SearchApiRequest) -> SearchApiResponse:
    """
    Endpoint to perform search by orchestrating the search pipeline.
    """
    try:
        logger.info(f"Received search request for user {request.user_id} with query: {request.query}")
        pipeline_output = await run_search_pipeline(
            user_id=request.user_id,
            raw_query=request.query
        )
        logger.debug(f"Search pipeline completed successfully for query: {request.query}")
        return SearchApiResponse(
            query_received=request.query,
            user_id=request.user_id,
            search_results=pipeline_output.get("search_results", []),
            message=pipeline_output.get("message", "Search initiated.")
        )
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal search error.")

