# app/services/cart_service.py
import os
import sys
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

# Add project root to Python path when running directly
if __name__ == "__main__":
    # Add project root to Python path for imports
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.insert(0, project_root)

from pymongo import ReturnDocument, errors
from pymongo.collection import Collection
from fastapi.concurrency import run_in_threadpool

from app.models.schemas import UserCartStored, CartItem, ProductStored
from app.db.database import get_carts_collection, get_products_collection


async def add_to_cart(
    user_id: str,
    product_id: int,
    quantity: int = 1
) -> Optional[UserCartStored]:
    """
    Adds a specified quantity of a product to a user's cart.
    Updates quantity if the product exists, or creates a new cart/item.
    Returns the updated UserCartStored or None on failure.
    """
    try:
        # Input validation
        if not user_id or not isinstance(user_id, str):
            print("Invalid user_id provided")
            return None
            
        if not isinstance(product_id, int) or product_id <= 0:
            print(f"Invalid product_id: {product_id}")
            return None
            
        if not isinstance(quantity, int) or quantity <= 0:
            print(f"Invalid quantity: {quantity}")
            return None
            
        carts_col: Collection = get_carts_collection()
        products_col: Collection = get_products_collection()

        # Wrap blocking MongoDB operations in run_in_threadpool
        prod_doc = await run_in_threadpool(
            products_col.find_one, 
            {"id": product_id}, 
            {"_id": 0, "id": 1, "title": 1, "price": 1, "thumbnail": 1}
        )
        
        if not prod_doc:
            print(f"Product {product_id} not found.")
            return None
            
        # Build cart item data dict
        cart_item = CartItem(
            product_id=prod_doc["id"],
            title=prod_doc.get("title", ""),
            price=prod_doc.get("price", 0.0),
            thumbnail=prod_doc.get("thumbnail"),
            quantity=quantity
        ).model_dump()

        current_time = datetime.now(timezone.utc)

        # Check if the user already has a cart
        existing_cart = await run_in_threadpool(carts_col.find_one, {"user_id": user_id})

        if existing_cart:
            # User has a cart, check if item exists in cart
            item_exists = False
            for item in existing_cart.get("items", []):
                if item.get("product_id") == product_id:
                    item_exists = True
                    break

            if item_exists:
                # Item exists, update quantity
                updated_doc = await run_in_threadpool(
                    carts_col.find_one_and_update,
                    {"user_id": user_id, "items.product_id": product_id},
                    {"$inc": {"items.$.quantity": quantity},
                     "$set": {"last_updated": current_time}},
                    return_document=ReturnDocument.AFTER
                )
            else:
                # Item doesn't exist, add it to the cart
                updated_doc = await run_in_threadpool(
                    carts_col.find_one_and_update,
                    {"user_id": user_id},
                    {"$push": {"items": cart_item},
                     "$set": {"last_updated": current_time}},
                    return_document=ReturnDocument.AFTER
                )
        else:
            # Create a new cart with the item
            result = await run_in_threadpool(
                carts_col.insert_one,
                {
                    "user_id": user_id,
                    "items": [cart_item],
                    "last_updated": current_time
                }
            )
            if result.inserted_id:
                updated_doc = await run_in_threadpool(carts_col.find_one, {"_id": result.inserted_id})
            else:
                updated_doc = None

        if not updated_doc:
            return None

        # Parse into Pydantic model
        return UserCartStored.model_validate(updated_doc)

    except errors.PyMongoError as e:
        print(f"MongoDB error in add_to_cart: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in add_to_cart: {e}")
        return None


async def get_cart(user_id: str) -> Optional[UserCartStored]:
    """
    Retrieves the current shopping cart for a given user.
    Returns None if no cart exists or on error.
    """
    try:
        # Input validation
        if not user_id or not isinstance(user_id, str):
            print("Invalid user_id provided")
            return None
            
        carts_col: Collection = get_carts_collection()
        cart_doc = await run_in_threadpool(carts_col.find_one, {"user_id": user_id})
        if not cart_doc:
            return None
        return UserCartStored.model_validate(cart_doc)
    except errors.PyMongoError as e:
        print(f"MongoDB error in get_cart: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_cart: {e}")
        return None


async def remove_from_cart(user_id: str, product_id: int) -> Optional[UserCartStored]:
    """
    Removes a specific product entirely from a user's cart.
    Returns the updated UserCartStored or None on failure.
    """
    try:
        # Input validation
        if not user_id or not isinstance(user_id, str):
            print("Invalid user_id provided")
            return None
            
        if not isinstance(product_id, int) or product_id <= 0:
            print(f"Invalid product_id: {product_id}")
            return None
            
        carts_col: Collection = get_carts_collection()
        current_time = datetime.now(timezone.utc)
        
        # First check if the cart and item exist
        cart = await run_in_threadpool(carts_col.find_one, {
            "user_id": user_id,
            "items.product_id": product_id
        })
        
        if not cart:
            print(f"No cart found for user {user_id} or product {product_id} not in cart")
            return None
        
        # Remove the item
        updated_doc = await run_in_threadpool(
            carts_col.find_one_and_update,
            {"user_id": user_id},
            {"$pull": {"items": {"product_id": product_id}},
             "$set": {"last_updated": current_time}},
            return_document=ReturnDocument.AFTER
        )
        
        if not updated_doc:
            return None
            
        return UserCartStored.model_validate(updated_doc)
    except errors.PyMongoError as e:
        print(f"MongoDB error in remove_from_cart: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in remove_from_cart: {e}")
        return None


async def clear_cart(user_id: str) -> Optional[UserCartStored]:
    """
    Removes all items from a user's cart but keeps the cart document.
    Returns the updated empty UserCartStored or None on failure.
    """
    try:
        if not user_id or not isinstance(user_id, str):
            print("Invalid user_id provided")
            return None
            
        carts_col: Collection = get_carts_collection()
        current_time = datetime.now(timezone.utc)
        
        # Empty the items array and update timestamp
        updated_doc = await run_in_threadpool(
            carts_col.find_one_and_update,
            {"user_id": user_id},
            {"$set": {"items": [], "last_updated": current_time}},
            return_document=ReturnDocument.AFTER
        )
        
        if not updated_doc:
            print(f"No cart found for user {user_id}")
            return None
            
        return UserCartStored.model_validate(updated_doc)
    except errors.PyMongoError as e:
        print(f"MongoDB error in clear_cart: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in clear_cart: {e}")
        return None


async def delete_cart(user_id: str) -> bool:
    """
    Completely removes a user's cart document from the database.
    Returns True if successful, False otherwise.
    """
    try:
        if not user_id or not isinstance(user_id, str):
            print("Invalid user_id provided")
            return False
            
        carts_col: Collection = get_carts_collection()
        
        # Check if cart exists
        cart_exists = await run_in_threadpool(
            lambda: carts_col.count_documents({"user_id": user_id}) > 0
        )
        
        if not cart_exists:
            print(f"No cart found for user {user_id}")
            return False
        
        # Delete the cart
        result = await run_in_threadpool(
            carts_col.delete_one,
            {"user_id": user_id}
        )
        
        if result.deleted_count == 1:
            print(f"Cart for user {user_id} successfully deleted")
            return True
        else:
            print(f"Failed to delete cart for user {user_id}")
            return False
            
    except errors.PyMongoError as e:
        print(f"MongoDB error in delete_cart: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error in delete_cart: {e}")
        return False


async def get_cart_details_for_llm_context(user_id: str) -> str:
    """
    Fetches the user's cart and returns a concise string summary for LLM prompts.
    """
    try:
        cart = await get_cart(user_id)
        if not cart or not cart.items:
            return "User's cart is empty."

        summary_items: List[str] = []
        for item in cart.items:
            summary_items.append(f"{item.title} (Qty: {item.quantity})")

        return f"User's cart contains: {', '.join(summary_items)}."
    except Exception as e:
        print(f"Error generating cart summary for user {user_id}: {e}")
        return ""

# Example usage
if __name__ == "__main__":
    print("Running cart service example...")
    
    # Test with a product ID that should exist in your database
    # First try to get an existing product ID from the database
    try:
        products_col = get_products_collection()
        sample_product = products_col.find_one({})
        if sample_product and "id" in sample_product:
            product_id = sample_product["id"]
            print(f"Found product ID: {product_id}")
        else:
            product_id = 1  # Use a default ID if no products found
            print(f"No products found, using default ID: {product_id}")
    except Exception as e:
        print(f"Error looking up product: {e}")
        product_id = 1  # Use a default ID
    
    user_id = "test_user"
    quantity = 2
    
    # Test 1: Add to cart
    print("\n=== Test 1: Add to Cart ===")
    print(f"Adding product {product_id} to cart for user {user_id}...")
    cart = add_to_cart(user_id, product_id, quantity)
    
    if cart:
        print(f"Cart updated successfully!")
        print(f"User: {cart.user_id}")
        print(f"Items: {len(cart.items)}")
        for item in cart.items:
            print(f"  - {item.title} (ID: {item.product_id}, Qty: {item.quantity}, Price: ${item.price})")
    else:
        print("Failed to update cart.")
    
    # Test 2: Get cart
    print("\n=== Test 2: Get Cart ===")
    print(f"Getting cart for user {user_id}...")
    retrieved_cart = get_cart(user_id)
    
    if retrieved_cart:
        print(f"Cart retrieved successfully!")
        print(f"User: {retrieved_cart.user_id}")
        print(f"Items: {len(retrieved_cart.items)}")
        print(f"Last updated: {retrieved_cart.last_updated}")
        for item in retrieved_cart.items:
            print(f"  - {item.title} (ID: {item.product_id}, Qty: {item.quantity}, Price: ${item.price})")
    else:
        print("No cart found or error retrieving cart.")
    
    # Get cart summary for LLM
    cart_summary = get_cart_details_for_llm_context(user_id)
    print(f"\nCart summary for LLM: {cart_summary}")
    
    # Test 3: Remove from cart
    if retrieved_cart and retrieved_cart.items:
        print("\n=== Test 3: Remove from Cart ===")
        # Get the first product ID from the cart
        product_to_remove = retrieved_cart.items[0].product_id
        print(f"Removing product {product_to_remove} from cart...")
        
        updated_cart = remove_from_cart(user_id, product_to_remove)
        
        if updated_cart:
            print(f"Product removed successfully!")
            print(f"Updated cart has {len(updated_cart.items)} items")
            if updated_cart.items:
                for item in updated_cart.items:
                    print(f"  - {item.title} (ID: {item.product_id}, Qty: {item.quantity})")
            else:
                print("Cart is now empty.")
        else:
            print("Failed to remove product from cart.")
        
        # Check cart summary after removal
        updated_summary = get_cart_details_for_llm_context(user_id)
        print(f"\nUpdated cart summary for LLM: {updated_summary}")
    
    print("\nCart service test completed.")