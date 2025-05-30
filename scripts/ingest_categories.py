# scripts/ingest_categories.py
import os
import ssl
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from pymongo.database import Database
from pinecone import Pinecone
from langchain_openai.embeddings import OpenAIEmbeddings
from typing import Optional, List

load_dotenv()


def get_mongo_db_connection() -> Database:
    """
    Connects to MongoDB and returns the Database object.
    """
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")
    if not uri or not db_name:
        raise ValueError("MONGO_URI and MONGO_DB_NAME must be set in environment variables.")
    try:
        # Configure SSL context for MongoDB connection
        ssl_settings = {
            'tls': True,
            'tlsAllowInvalidCertificates': True  # Only use in development
        }
        
        client = MongoClient(uri, **ssl_settings)
        # quick check
        client.admin.command('ping')
        print(f"Connected to MongoDB at {uri}, database: {db_name}")
        return client[db_name]
    except errors.PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}")
        raise


def get_pinecone_category_index():
    """
    Initializes Pinecone client and returns the category embeddings index.
    """
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_CATEGORY_INDEX_NAME") or os.getenv("PINECONE_INDEX_NAME")

    if not api_key or not index_name:
        raise ValueError("PINECONE_API_KEY and PINECONE_CATEGORY_INDEX_NAME or PINECONE_INDEX_NAME must be set in environment variables.")

    try:
        # Initialize Pinecone with the new API
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
        
        # verify index
        stats = index.describe_index_stats()
        vector_count = stats.get('total_vector_count', 0)
        print(f"Pinecone index '{index_name}' ready, contains {vector_count} vectors.")
        return index
    except Exception as e:
        print(f"Error initializing Pinecone index: {e}")
        raise


def get_openai_embedding_model() -> OpenAIEmbeddings:
    """
    Initializes and returns the OpenAIEmbeddings model.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set in environment variables.")
    try:
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        embed = OpenAIEmbeddings(openai_api_key=api_key, model=model)
        print(f"Initialized OpenAI embedding model '{model}'.")
        return embed
    except Exception as e:
        print(f"Error initializing OpenAIEmbeddings: {e}")
        raise


def ingest_unique_categories() -> None:
    """
    Extract unique categories from MongoDB, generate embeddings, and upsert into Pinecone.
    Also maintain a master list in MongoDB.
    """
    # Initialize clients
    db = get_mongo_db_connection()
    
    # Debug: List all collections in the database
    collections = db.list_collection_names()
    print(f"Available collections in the database: {collections}")
    
    products_col = db["products"]
    master_col = db["categories_master_list"]
    # ensure uniqueness
    master_col.create_index("category_name", unique=True)
    
    # Debug: Count documents in the products collection
    count = products_col.count_documents({})
    print(f"Found {count} products in the collection.")
    
    # Debug: Print a sample document if any exist
    if count > 0:
        sample = products_col.find_one()
        print(f"Sample product: {sample}")
        # Check if the document has a category field
        if 'category' in sample:
            print(f"Sample category: {sample['category']}")
        else:
            print("Warning: Sample product doesn't have a 'category' field.")
    
    pinecone_index = get_pinecone_category_index()
    embed_model = get_openai_embedding_model()

    # Extract unique categories with more explicit check
    unique_categories = []
    try:
        unique_categories = products_col.distinct("category")
        print(f"Found {len(unique_categories)} unique categories: {unique_categories}")
        
        # If no categories found, check if using wrong field name
        if len(unique_categories) == 0:
            # Check if there might be alternative field names
            sample = products_col.find_one()
            if sample:
                print(f"Available fields in sample document: {list(sample.keys())}")
                # Check if categories might be in a different field or capitalization
                for field in sample.keys():
                    if field.lower().startswith('cat'):
                        alt_categories = products_col.distinct(field)
                        print(f"Found potential categories in field '{field}': {alt_categories}")
    except Exception as e:
        print(f"Error retrieving distinct categories: {e}")
    
    processed = 0
    for category_name in unique_categories:
        try:
            # Generate embedding
            vector = embed_model.embed_query(category_name)

            # Prepare Pinecone upsert item
            vector_id = category_name  # direct use; ensure <=512 bytes
            
            # Upsert vector using the new Pinecone API format
            pinecone_index.upsert([
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": {"category_name": category_name}
                }
            ])
            print(f"Upserted category '{category_name}' into Pinecone.")

            # Upsert into master list with timestamp
            master_col.update_one(
                {"category_name": category_name},
                {"$set": {"last_embedded_at": datetime.utcnow()}},
                upsert=True
            )
            processed += 1
        except Exception as e:
            print(f"Error processing category '{category_name}': {e}")

    print(f"Processed {processed}/{len(unique_categories)} categories.")


if __name__ == "__main__":
    ingest_unique_categories()
