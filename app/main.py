# app/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Import routers and services
from app.routers.search_router import router as search_router
from app.services.cart_service import add_to_cart, get_cart, remove_from_cart
from app.models.schemas import CartActionRequest, UserCartApiResponse
from app.db.database import connect_to_mongo
from app.db.vector_store import init_pinecone_client
from app.db.llm_clients import get_llm_client, get_embedding_model

# Initialize FastAPI app
app = FastAPI(
    title="GenAI Product Discovery Engine",
    version="1.0.0"
)

# Application startup event
@app.on_event("startup")
async def startup_event():
    try:
        connect_to_mongo()
        print("MongoDB connection initialized.")
    except Exception as e:
        print(f"MongoDB initialization error: {e}")
        raise
    try:
        init_pinecone_client()
        print("Pinecone client initialized.")
    except Exception as e:
        print(f"Pinecone initialization error: {e}")
        raise
    # Pre-warm LLM clients
    try:
        get_llm_client()
        get_embedding_model()
        print("LLM clients initialized.")
    except Exception as e:
        print(f"LLM client initialization error: {e}")
        raise

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutting down.")
    # Add explicit cleanup if necessary

# Include search router
app.include_router(search_router)

# Cart endpoints
cart_router = APIRouter(prefix="/cart", tags=["Cart"])

@cart_router.get("/{user_id}", response_model=UserCartApiResponse)
async def get_user_cart_endpoint(user_id: str):
    cart = await get_cart(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@cart_router.post("/item", response_model=UserCartApiResponse)
async def add_item_to_cart_endpoint(request: CartActionRequest):
    updated_cart = await add_to_cart(
        user_id=request.user_id,
        product_id=request.product_id,
        quantity=request.quantity or 1
    )
    if not updated_cart:
        raise HTTPException(status_code=400, detail="Failed to add item to cart")
    return updated_cart

@cart_router.delete("/item", response_model=UserCartApiResponse)
async def remove_item_from_cart_endpoint(request: CartActionRequest):
    updated_cart = await remove_from_cart(
        user_id=request.user_id,
        product_id=request.product_id
    )
    if not updated_cart:
        raise HTTPException(status_code=400, detail="Failed to remove item from cart")
    return updated_cart

# Include cart router
app.include_router(cart_router)

# Health check endpoint
@app.get("/", tags=["Health Check"])
async def read_root():
    return JSONResponse(content={"message": "Welcome to the GenAI Product Discovery Engine!"})
