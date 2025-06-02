import logging
from typing import List
from fastapi.concurrency import run_in_threadpool
from app.db.database import get_products_collection, get_categories_master_list_collection

logger = logging.getLogger(__name__)

async def list_all_categories() -> List[str]:
    """
    Get a list of all product categories.
    First tries to get from the categories master list collection,
    falls back to distinct categories from products if needed.
    """
    try:
        # Try to get from categories_master_list first
        categories_col = get_categories_master_list_collection()
        categories_docs = await run_in_threadpool(
            lambda: list(categories_col.find({}, {"category_name": 1, "_id": 0}))
        )
        
        if categories_docs:
            # Extract category names from documents
            categories = [doc.get("category_name") for doc in categories_docs if doc.get("category_name")]
            if categories:
                return sorted(categories)
        
        # Fallback: Get distinct categories from products collection
        products_col = get_products_collection()
        categories = await run_in_threadpool(
            lambda: products_col.distinct("category")
        )
        
        # Filter out None values and sort alphabetically
        categories = sorted([c for c in categories if c])
        return categories
        
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}", exc_info=True)
        raise
