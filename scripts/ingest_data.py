import os
import httpx
import motor.motor_asyncio
from pinecone import Pinecone
from dotenv import load_dotenv
import openai
from openai import OpenAI

load_dotenv()

# 1. Set up MongoDB
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_URI,
    tls=True,  # Enable TLS/SSL
    tlsAllowInvalidCertificates=True  # Disable certificate validation (use only for development)
)
db = mongo_client["product_discovery"]
products_col = db["products"]

# 2. Set up Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone = Pinecone(api_key=pinecone_api_key)
index = pinecone.Index("products")

# 3. Set up OpenAI API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed(docs: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of documents."""
    res = client.embeddings.create(
        input=docs,
        model="text-embedding-3-large"  
    )
    doc_embeds = [r.embedding for r in res.data]
    return doc_embeds

async def ingest_one(product: dict):
    # 3a. Store raw product in MongoDB
    await products_col.replace_one({"id": product["id"]}, product, upsert=True)

    # 3b. Build the text to embed
    text = f"Title: {product.get('title', '')}\nDescription: {product.get('description', '')}\nCategory: {product.get('category', '')}\nBrand: {product.get('brand', '')}\nTags: {', '.join(product.get('tags', []))}"

    # 3c. Generate embedding
    vector = embed([text])[0]
    
    # 3d. Build metadata dict - ensure all values are properly formatted for Pinecone
    # Convert any complex objects to strings
    dimensions_str = str(product.get("dimensions", {})) if product.get("dimensions") else ""
    
    metadata = {
        "title": product["title"],
        "category": product.get("category", ""),
        "price": product.get("price", 0),
        "discountPercentage": product.get("discountPercentage", 0),
        "rating": product.get("rating", 0),
        "stock": product.get("stock", 0),
        "tags": product.get("tags", []),  # List of strings is allowed
        "sku": product.get("sku", ""),
        "weight": product.get("weight", ""),
        "dimensions": dimensions_str,  # Convert dict to string
        "warrantyInformation": product.get("warrantyInformation", ""),
        "shippingInformation": product.get("shippingInformation", ""),
        "availabilityStatus": product.get("availabilityStatus", ""),
        "returnPolicy": product.get("returnPolicy", ""),
        "minimumOrderQuantity": product.get("minimumOrderQuantity", 0),
        "createdAt": product.get("meta", {}).get("createdAt", ""),
        "updatedAt": product.get("meta", {}).get("updatedAt", ""),
        "thumbnail": product.get("thumbnail", ""),
    }

    # 3e. Upsert into Pinecone
    index.upsert([
        {
            "id": str(product["id"]),
            "values": vector,
            "metadata": metadata
        }
    ])
    print(f"Ingested product {product['id']} into MongoDB & Pinecone.")

async def main():
    # fetch all products
    resp = httpx.get("https://dummyjson.com/products?limit=0")
    resp.raise_for_status()
    products = resp.json()["products"]

    for prod in products:
        await ingest_one(prod)

    # Query example
    query = "Tell me about a product in the electronics category"
    query_vector = embed([query])[0]

    results = index.query(
        namespace="",
        vector=query_vector,
        top_k=3,
        include_values=False,
        include_metadata=True
    )
    print("Query Results:", results)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())