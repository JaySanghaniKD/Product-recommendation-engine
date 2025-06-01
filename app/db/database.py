import os
import ssl
import logging
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from pymongo.database import Database, Collection
from typing import Optional

# Initialize logger for this module
logger = logging.getLogger(__name__)

load_dotenv()

# Global MongoDB client and database instances
_db_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def connect_to_mongo() -> None:
    """
    Initialize the MongoDB client and set the database instance.
    """
    global _db_client, _database
    if _db_client is None:
        mongo_uri = os.getenv("MONGO_URI")
        db_name = os.getenv("MONGO_DB_NAME")
        if not mongo_uri or not db_name:
            logger.error("MONGO_URI and MONGO_DB_NAME must be set in environment variables.")
            raise ValueError("MONGO_URI and MONGO_DB_NAME must be set in environment variables.")
        try:
            # Configure SSL context for MongoDB connection
            ssl_settings = {
                'tls': True,
                'tlsAllowInvalidCertificates': True  
            }
            
            logger.info(f"Connecting to MongoDB at {mongo_uri}, database: {db_name}")
            _db_client = MongoClient(mongo_uri, **ssl_settings)
            # The ismaster command is cheap and does not require auth.
            _db_client.admin.command('ismaster')
            _database = _db_client[db_name]
            logger.info(f"Successfully connected to MongoDB")
        except errors.ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
            raise


def get_mongo_db() -> Database:
    """
    Returns the MongoDB Database instance, connecting if necessary.
    """
    global _database
    if _database is None:
        connect_to_mongo()
    if _database is None:
        raise RuntimeError("Failed to initialize MongoDB database instance.")
    return _database


def get_products_collection() -> Collection:
    return get_mongo_db()["products"]


def get_carts_collection() -> Collection:
    return get_mongo_db()["carts"]


def get_user_history_collection() -> Collection:
    return get_mongo_db()["user_history"]


def get_categories_master_list_collection() -> Collection:
    return get_mongo_db()["categories_master_list"]

# main entry point for testing the connection
if __name__ == "__main__":
    try:
        connect_to_mongo()
        print("MongoDB connection established successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")