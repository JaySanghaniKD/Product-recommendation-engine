from fastapi import APIRouter, HTTPException
from typing import List
from app.services.category_service import list_all_categories
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=List[str])
async def list_categories():
    """
    Get a list of all product categories.
    """
    try:
        categories = await list_all_categories()
        return categories
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while retrieving categories")
