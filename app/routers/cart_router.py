from fastapi import APIRouter, HTTPException
from app.models.schemas import CartActionRequest, UserCartApiResponse
from app.services.cart_service import add_to_cart, get_cart, remove_from_cart
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/{user_id}", response_model=UserCartApiResponse)
async def get_user_cart_endpoint(user_id: str):
    """
    Get the current cart for a user.
    """
    try:
        cart = await get_cart(user_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        return cart
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving cart for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while retrieving cart")

@router.post("/item", response_model=UserCartApiResponse)
async def add_item_to_cart_endpoint(request: CartActionRequest):
    """
    Add an item to the user's cart.
    """
    try:
        updated_cart = await add_to_cart(
            user_id=request.user_id,
            product_id=request.product_id,
            quantity=request.quantity or 1
        )
        if not updated_cart:
            raise HTTPException(status_code=400, detail="Failed to add item to cart")
        return updated_cart
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item to cart for user {request.user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while adding item to cart")

@router.delete("/item", response_model=UserCartApiResponse)
async def remove_item_from_cart_endpoint(request: CartActionRequest):
    """
    Remove an item from the user's cart.
    """
    try:
        updated_cart = await remove_from_cart(
            user_id=request.user_id,
            product_id=request.product_id
        )
        if not updated_cart:
            raise HTTPException(status_code=400, detail="Failed to remove item from cart")
        return updated_cart
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing item from cart for user {request.user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while removing item from cart")
