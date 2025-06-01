import os
import logging
from dotenv import load_dotenv
from pinecone import Pinecone
from typing import Optional

# Initialize logger for this module
logger = logging.getLogger(__name__)

load_dotenv()

# Global Pinecone client and index instances
_pinecone_client: Optional[Pinecone] = None
_category_pinecone_index = None


def init_pinecone_client() -> None:
    """
    Initialize Pinecone client and category index.
    """
    global _pinecone_client, _category_pinecone_index
    if _pinecone_client is None:
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_CATEGORY_INDEX_NAME") or os.getenv("PINECONE_INDEX_NAME")
        
        if not api_key or not index_name:
            logger.error("PINECONE_API_KEY and PINECONE_CATEGORY_INDEX_NAME or PINECONE_INDEX_NAME must be set.")
            raise ValueError("PINECONE_API_KEY and PINECONE_CATEGORY_INDEX_NAME or PINECONE_INDEX_NAME must be set.")
        
        try:
            logger.info(f"Initializing Pinecone client with index {index_name}")
            # Create Pinecone client with the new API
            _pinecone_client = Pinecone(api_key=api_key)
            
            # Get the index
            _category_pinecone_index = _pinecone_client.Index(index_name)
            
            # Verify index readiness
            stats = _category_pinecone_index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            logger.info(f"Connected to Pinecone index '{index_name}' with {total_vectors} vectors")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client or index: {e}", exc_info=True)
            raise


def get_pinecone_category_index():
    """
    Returns the Pinecone Index for categories, initializing if necessary.
    """
    global _category_pinecone_index
    if _category_pinecone_index is None:
        init_pinecone_client()
    if _category_pinecone_index is None:
        raise RuntimeError("Pinecone category index is not initialized.")
    return _category_pinecone_index


# Example usage:
if __name__ == "__main__":
    try:
        init_pinecone_client()
        index = get_pinecone_category_index()
        print(f"Pinecone index is ready for use.")
    except Exception as e:
        print(f"Error initializing Pinecone client: {e}")