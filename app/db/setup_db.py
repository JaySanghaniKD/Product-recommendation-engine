from pymongo import MongoClient, ASCENDING, TEXT
import logging
from fastapi.concurrency import run_in_threadpool
from app.db.database import get_products_collection
import os

logger = logging.getLogger(__name__)

async def create_text_index_async():
    """
    Create text indices on MongoDB collections for text search capabilities.
    This async version can be called during FastAPI startup.
    """
    try:
        logger.info("Creating text index on products collection...")
        # Get the collection using your existing database connection
        products_collection = get_products_collection()
        
        # Run the index creation in a thread pool to avoid blocking
        await run_in_threadpool(
            products_collection.create_index,
            [
                ("title", "text"), 
                ("description", "text"),
                ("tags", "text")
            ]
        )
        
        logger.info("Text index created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating text index: {e}")
        return False

