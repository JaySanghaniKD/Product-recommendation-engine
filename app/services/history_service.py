from datetime import datetime
from typing import List, Optional, Union, Dict, Any
import os
import sys

# Handle imports when run directly
if __name__ == "__main__":
    # Add project root to Python path for imports
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.insert(0, project_root)

from pymongo import DESCENDING, errors
from pymongo.collection import Collection

from app.models.schemas import (
    UserInteractionStored,
    SearchInteractionDetail,
    ViewProductInteractionDetail,
    AddToCartInteractionDetail,
)
from app.db.database import get_user_history_collection

def log_interaction(
    user_id: str,
    interaction_type: str,
    details: Union[SearchInteractionDetail, ViewProductInteractionDetail, AddToCartInteractionDetail]
) -> bool:
    """
    Logs a user's interaction to the MongoDB user_history collection.

    Returns True if successful, False otherwise.
    """
    try:
        collection: Collection = get_user_history_collection()
        # Build the interaction record using Pydantic
        interaction = UserInteractionStored(
            user_id=user_id,
            interaction_type=interaction_type,
            details=details
        )
        # Convert to dict for insertion
        record: Dict[str, Any] = interaction.model_dump(mode="json")
        # Insert into MongoDB
        collection.insert_one(record)
        return True
    except errors.PyMongoError as e:
        print(f"Error logging interaction for user {user_id}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error in log_interaction: {e}")
        return False



def get_recent_history_summary(
    user_id: str,
    num_interactions: int = 3
) -> str:
    """
    Fetches the most recent interactions for a user and formats them into a concise summary string.

    Returns an empty string if no history is found or on error.
    """
    try:
        collection: Collection = get_user_history_collection()
        # Retrieve most recent documents
        cursor = (
            collection
            .find({"user_id": user_id})
            .sort("timestamp", DESCENDING)
            .limit(num_interactions)
        )
        docs: List[Dict[str, Any]] = list(cursor)
        if not docs:
            return ""

        formatted: List[str] = []
        for doc in docs:
            # Parse into Pydantic model (ignores extra fields)
            interaction = UserInteractionStored.model_validate(doc)
            itype = interaction.interaction_type
            detail = interaction.details
            try:
                if itype == "search" and isinstance(detail, SearchInteractionDetail):
                    formatted.append(f"Searched for '{detail.query}'")
                elif itype == "view_product" and isinstance(detail, ViewProductInteractionDetail):
                    formatted.append(
                        f"Viewed product '{detail.product_title}' (ID: {detail.product_id})"
                    )
                elif itype == "add_to_cart" and isinstance(detail, AddToCartInteractionDetail):
                    formatted.append(
                        f"Added '{detail.product_title}' (Qty: {detail.quantity}) to cart"
                    )
                else:
                    # Fallback for unknown interaction types
                    formatted.append(f"Performed '{itype}' action")
            except AttributeError:
                # Skip malformed detail
                continue

        # Reverse to have oldest first in summary
        summary_list = list(reversed(formatted))
        return "; ".join(summary_list)

    except errors.PyMongoError as e:
        print(f"Error retrieving history for user {user_id}: {e}")
        return ""
    except Exception as e:
        print(f"Unexpected error in get_recent_history_summary: {e}")
        return ""

# Example usage:
if __name__ == "__main__":
    print("Running history service example...")
    
    # Example interaction details
    search_detail = SearchInteractionDetail(query="laptop")
    view_detail = ViewProductInteractionDetail(product_id=123, product_title="Gaming Laptop")
    add_to_cart_detail = AddToCartInteractionDetail(product_id=123, product_title="Gaming Laptop", quantity=1)

    # Log interactions
    print("Logging user interactions...")
    search_success = log_interaction("user_1", "search", search_detail)
    view_success = log_interaction("user_1", "view_product", view_detail)
    cart_success = log_interaction("user_1", "add_to_cart", add_to_cart_detail)
    
    print(f"Search interaction logged: {search_success}")
    print(f"View product interaction logged: {view_success}")
    print(f"Add to cart interaction logged: {cart_success}")

    # Get recent history summary
    summary = get_recent_history_summary("user_1")
    print(f"Recent History Summary: {summary}")