import logging
from typing import List, Dict, Any, Optional
from fastapi.concurrency import run_in_threadpool
from app.db.database import get_products_collection
from app.models.schemas import ProductStored

logger = logging.getLogger(__name__)

async def get_product_by_id(product_id: int) -> Optional[ProductStored]:
    """
    Retrieve a product by its ID.
    Returns None if the product is not found.
    """
    try:
        products_col = get_products_collection()
        product = await run_in_threadpool(products_col.find_one, {"id": product_id})
        if not product:
            return None
        return ProductStored.model_validate(product)
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {e}", exc_info=True)
        raise

async def list_products(
    page: int,
    limit: int,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    brand: Optional[str] = None,
    sort: Optional[str] = None
) -> Dict[str, Any]:
    """
    List products with pagination, filtering, and sorting.
    Returns a dictionary with items, pagination info, and metadata.
    """
    try:
        products_col = get_products_collection()
        
        # Build query filters
        query = {}
        if category:
            query["category"] = category
        if brand:
            query["brand"] = brand
        
        # Price range filter
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            if price_filter:
                query["price"] = price_filter
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        # Determine sort order
        sort_config = None
        if sort:
            if sort == "price_asc":
                sort_config = [("price", 1)]
            elif sort == "price_desc":
                sort_config = [("price", -1)]
            elif sort == "rating_desc":
                sort_config = [("rating", -1)]
        
        # Get total count for pagination info
        total_count = await run_in_threadpool(
            lambda: products_col.count_documents(query)
        )
        
        # Execute query with pagination and sorting
        cursor = products_col.find(query).skip(skip).limit(limit)
        if sort_config:
            cursor = cursor.sort(sort_config)
        
        # Convert to list of products
        products = await run_in_threadpool(list, cursor)
        
        # Convert MongoDB documents to Pydantic models
        result = []
        for product in products:
            try:
                result.append(ProductStored.model_validate(product))
            except Exception as e:
                logger.warning(f"Error parsing product: {e}")
        
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        return {
            "items": result,
            "page": page,
            "limit": limit,
            "total_items": total_count,
            "total_pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Error listing products: {e}", exc_info=True)
        raise
