# app/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Import routers and services
from app.routers.search_router import router as search_router
from app.routers.product_router import router as product_router
from app.routers.category_router import router as category_router
from app.routers.history_router import router as history_router
from app.routers.recommendation_router import router as recommendation_router
from app.routers.cart_router import router as cart_router
from app.db.database import connect_to_mongo
from app.db.vector_store import init_pinecone_client
from app.db.llm_clients import get_llm_client, get_embedding_model
from app.core.logging_config import configure_logging
import logging

# Configure logging at the earliest point
configure_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GenAI Product Discovery Engine",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Application startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")
    try:
        connect_to_mongo()
        logger.info("MongoDB connection initialized.")
    except Exception as e:
        logger.error(f"MongoDB initialization error: {e}")
        raise

    # Create text indices if they don't exist
    try:
        from app.db.setup_db import create_text_index_async
        await create_text_index_async()
        logger.info("MongoDB text indices setup completed")
    except Exception as e:
        logger.error(f"Failed to create text index: {e}")
    
    try:
        init_pinecone_client()
        logger.info("Pinecone client initialized.")
    except Exception as e:
        logger.error(f"Pinecone initialization error: {e}")
        raise
    # Pre-warm LLM clients
    try:
        get_llm_client()
        get_embedding_model()
        logger.info("LLM clients initialized.")
    except Exception as e:
        logger.error(f"LLM client initialization error: {e}")
        raise

    logger.info("Application startup completed")

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down.")
    # Add explicit cleanup if necessary

# Include all routers
app.include_router(search_router)
app.include_router(product_router)
app.include_router(category_router)
app.include_router(history_router)
app.include_router(recommendation_router)
app.include_router(cart_router)

# Health check endpoint
@app.get("/", tags=["Health Check"])
async def read_root():
    return JSONResponse(content={"message": "Welcome to the GenAI Product Discovery Engine!"})
