from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.schemas import SearchApiResponseProduct
from app.services.recommendation_service import get_personalized_recommendations
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/{user_id}", response_model=List[SearchApiResponseProduct])
async def get_recommendations(
    user_id: str,
    count: int = Query(5, ge=1, le=20, description="Number of recommendations to return")
):
    """
    Get personalized product recommendations for a user based on their history and cart.
    """
    try:
        recommendations = await get_personalized_recommendations(
            user_id=user_id,
            count=count
        )
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="No suitable recommendations found")
            
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while generating recommendations")
