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

