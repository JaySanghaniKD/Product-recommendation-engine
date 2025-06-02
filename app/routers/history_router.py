from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any
from app.db.database import get_user_history_collection
from fastapi.concurrency import run_in_threadpool
from pymongo import DESCENDING
import logging
from datetime import datetime

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
        logger.info(f"Getting history for user: {user_id}")
        history_col = get_user_history_collection()
        
        # Query for the user's interactions, sorted by most recent first
        cursor = history_col.find(
            {"user_id": user_id}
        ).sort("timestamp", DESCENDING).limit(limit)
        
        # Convert to list
        interactions = await run_in_threadpool(list, cursor)
        logger.info(f"Found {len(interactions)} total interactions for user {user_id}")
        
        # Group by interaction type for a more structured response
        grouped_interactions = {
            "searches": [],
            "product_views": [],
            "cart_actions": [],
            "recent": []  # Include the full list for convenience
        }
        
        for interaction in interactions:
            # Make a copy to avoid modifying the original
            interaction_copy = dict(interaction)
            
            # Convert ObjectId to string for JSON serialization
            if "_id" in interaction_copy:
                interaction_copy["_id"] = str(interaction_copy["_id"])
                
            interaction_type = interaction_copy.get("interaction_type")
            logger.debug(f"Processing interaction type: {interaction_type}")
            
            # Add to recent list
            grouped_interactions["recent"].append(interaction_copy)
            
            # Add to specific type list
            if interaction_type == "search":
                grouped_interactions["searches"].append(interaction_copy)
            elif interaction_type == "view_product":
                logger.info(f"Adding product view to history: {interaction_copy}")
                grouped_interactions["product_views"].append(interaction_copy)
            elif interaction_type == "add_to_cart":
                grouped_interactions["cart_actions"].append(interaction_copy)
        
        logger.info(f"Grouped interactions: searches={len(grouped_interactions['searches'])}, "
                  f"product_views={len(grouped_interactions['product_views'])}, "
                  f"cart_actions={len(grouped_interactions['cart_actions'])}")
        
        return grouped_interactions
        
    except Exception as e:
        logger.error(f"Error retrieving history for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error while retrieving user history")

@router.post("/track", response_model=Dict[str, Any])
async def track_user_interaction(
    interaction: Dict[str, Any] = Body(...)
):
    """
    Track a user interaction (search, product view, etc.)
    """
    try:
        logger.info(f"Received interaction tracking request: {interaction}")
        history_col = get_user_history_collection()
        
        # Ensure required fields exist
        if "user_id" not in interaction:
            logger.error("Missing user_id in interaction")
            return {"status": "error", "message": "user_id is required"}
            
        if "interaction_type" not in interaction:
            logger.error("Missing interaction_type in interaction")
            return {"status": "error", "message": "interaction_type is required"}
        
        # Add timestamp if not provided
        if "timestamp" not in interaction:
            interaction["timestamp"] = datetime.utcnow().isoformat()
        
        # Log before insertion    
        logger.info(f"Inserting interaction into MongoDB: {interaction}")
            
        # Insert the interaction
        result = await run_in_threadpool(history_col.insert_one, interaction)
        logger.info(f"Insertion result: {result.inserted_id}")
        
        # Return success response with the inserted ID
        return {
            "status": "success", 
            "message": "Interaction tracked successfully",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        logger.error(f"Error tracking user interaction: {e}", exc_info=True)
        # Return error status
        return {"status": "error", "message": f"Failed to track interaction: {str(e)}"}
