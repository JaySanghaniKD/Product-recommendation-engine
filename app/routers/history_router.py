from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from app.db.database import get_user_history_collection
from fastapi.concurrency import run_in_threadpool
from pymongo import DESCENDING
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["User History"])

@router.get("/{user_id}", response_model=Dict[str, Any])
async def get_user_history(
    user_id: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of history items to return")
):
    """
    Get a user's recent interaction history.
    Returns the most recent user interactions (searches, product views, cart actions)
    """
    try:
        history_col = get_user_history_collection()
        
        # Query for the user's interactions, sorted by most recent first
        cursor = history_col.find(
            {"user_id": user_id}
        ).sort("timestamp", DESCENDING).limit(limit)
        
        # Convert to list
        interactions = await run_in_threadpool(list, cursor)
        
        # Group by interaction type for a more structured response
        grouped_interactions = {
            "searches": [],
            "product_views": [],
            "cart_actions": [],
            "recent": interactions  # Include the full list for convenience
        }
        
        for interaction in interactions:
            interaction_type = interaction.get("interaction_type")
            # Remove internal MongoDB _id field
            if "_id" in interaction:
                del interaction["_id"]
                
            if interaction_type == "search":
                grouped_interactions["searches"].append(interaction)
            elif interaction_type == "view_product":
                grouped_interactions["product_views"].append(interaction)
            elif interaction_type == "add_to_cart":
                grouped_interactions["cart_actions"].append(interaction)
        
        return grouped_interactions
        
    except Exception as e:
        logger.error(f"Error retrieving history for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error while retrieving user history")
