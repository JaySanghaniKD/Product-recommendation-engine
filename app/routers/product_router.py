from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from app.models.schemas import ProductStored
from app.db.database import get_products_collection
from fastapi.concurrency import run_in_threadpool
from app.services.product_service import get_product_by_id, list_products
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/{product_id}", response_model=ProductStored)
async def get_product(
    product_id: int = Path(..., description="The ID of the product to retrieve")
):
    """Get detailed information about a specific product."""
    try:
        product = await get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while retrieving product")

@router.get("/", response_model=Dict[str, Any])
async def list_products_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    sort: Optional[str] = Query(None, description="Sort by: price_asc, price_desc, rating_desc")
):
    """
    Get paginated list of products with optional filtering and sorting.
    """
    try:
        result = await list_products(
            page=page,
            limit=limit,
            category=category,
            min_price=min_price,
            max_price=max_price,
            brand=brand,
            sort=sort
        )
        return result
    except Exception as e:
        logger.error(f"Error listing products: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while listing products")

@router.get("/featured/", response_model=List[ProductStored])
async def get_featured_products(limit: int = Query(6, ge=1, le=20)):
    """
    Get a selection of random products to display on the homepage.
    Much faster than the AI recommendations.
    """
    try:
        products_col = get_products_collection()
        
        # Use MongoDB's aggregation framework to get random documents
        # This is more efficient than fetching all and then sampling
        pipeline = [
            {"$sample": {"size": limit}},  # Get random documents
        ]
        
        cursor = products_col.aggregate(pipeline)
        random_products = await run_in_threadpool(list, cursor)
        
        # Convert to Pydantic models
        result = []
        for product in random_products:
            try:
                result.append(ProductStored.model_validate(product))
            except Exception as e:
                logger.warning(f"Error parsing product: {e}")
                
        return result
    except Exception as e:
        logger.error(f"Error retrieving featured products: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while retrieving featured products")
