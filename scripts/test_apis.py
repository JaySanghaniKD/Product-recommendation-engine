import asyncio
import httpx
import json
from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Settings
API_HOST = "http://localhost:8000"
TEST_USER_ID = "test_user_123"

# Helper function to format JSON responses
def print_json(obj: Any) -> None:
    """Pretty print JSON data"""
    print(json.dumps(obj, indent=2))

async def test_all_apis():
    """Test all API endpoints with sample queries"""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        print("\n===== TESTING API ENDPOINTS =====\n")
        
        # Test 1: Health Check
        print("\n----- Test 1: Health Check -----")
        response = await client.get(f"{API_HOST}/")
        print(f"Status: {response.status_code}")
        print_json(response.json())
        
        # Test 2: Get Product Details
        print("\n----- Test 2: Get Product Details -----")
        product_id = 1  # Example product ID
        response = await client.get(f"{API_HOST}/products/{product_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            product = response.json()
            print(f"Found product: {product['title']} (${product['price']})")
            print(f"Description: {product['description'][:100]}...")
        else:
            print_json(response.json())
        
        # Test 3: List Products with Filters
        print("\n----- Test 3: List Products with Filters -----")
        # Test filtering by category and price range
        try:
            response = await client.get(
                f"{API_HOST}/products/",  # Added trailing slash to fix redirect issue
                params={
                    "page": 1,
                    "limit": 5,
                    "category": "smartphones",
                    "min_price": 500,
                    "sort": "price_desc"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Found {len(data['items'])} products, page {data['page']} of {data['total_pages']}")
                    for i, product in enumerate(data['items'], 1):
                        print(f"{i}. {product['title']} - ${product['price']}")
                except ValueError:
                    print("Warning: Could not parse response as JSON")
                    print(f"Response content: {response.text[:100]}...")
            else:
                print(f"Unexpected status code: {response.status_code}")
                print(f"Response content: {response.text[:100]}...")
        except Exception as e:
            print(f"Error during request: {e}")
        
        # Test 4: Get Categories
        print("\n----- Test 4: Get Categories -----")
        response = await client.get(f"{API_HOST}/categories")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"Found {len(categories)} categories:")
            for i, category in enumerate(categories[:10], 1):
                print(f"{i}. {category}")
            if len(categories) > 10:
                print(f"... and {len(categories) - 10} more")
        else:
            print_json(response.json())
        
        # Test 5: Search for Products
        print("\n----- Test 5: Search for Products -----")
        search_query = "smartphone with good camera under $1000"
        response = await client.post(
            f"{API_HOST}/search/",
            json={
                "user_id": TEST_USER_ID,
                "query": search_query
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"Search query: '{results['query_received']}'")
            print(f"Message: {results['message']}")
            print(f"Found {len(results['search_results'])} results:")
            for i, result in enumerate(results['search_results'], 1):
                print(f"{i}. {result['title']} - ${result['price']}")
                print(f"   Justification: {result['justification']}")
        else:
            print_json(response.json())
        
        # Test 6: Get User History
        print("\n----- Test 6: Get User History -----")
        response = await client.get(f"{API_HOST}/history/{TEST_USER_ID}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            history = response.json()
            print(f"Recent interactions: {len(history['recent'])}")
            print(f"Searches: {len(history['searches'])}")
            print(f"Product views: {len(history['product_views'])}")
            print(f"Cart actions: {len(history['cart_actions'])}")
        else:
            print_json(response.json())
        
        # Test 7: Get Recommendations
        print("\n----- Test 7: Get Recommendations -----")
        response = await client.get(
            f"{API_HOST}/recommendations/{TEST_USER_ID}",
            params={"count": 3}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            recommendations = response.json()
            print(f"Found {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['title']} - ${rec['price']}")
                print(f"   Justification: {rec['justification']}")
        else:
            print_json(response.json())
        
        # Test 8: Cart Operations
        print("\n----- Test 8: Cart Operations -----")
        
        # 8.1: Add item to cart
        product_id_to_add = 1  # Example product ID
        print(f"\n8.1: Adding product {product_id_to_add} to cart")
        response = await client.post(
            f"{API_HOST}/cart/item",
            json={
                "user_id": TEST_USER_ID,
                "product_id": product_id_to_add,
                "quantity": 2
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            cart = response.json()
            print(f"Cart updated, contains {len(cart['items'])} items")
        else:
            print_json(response.json())
        
        # 8.2: Get cart
        print("\n8.2: Getting cart")
        response = await client.get(f"{API_HOST}/cart/{TEST_USER_ID}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            cart = response.json()
            print(f"Cart contains {len(cart['items'])} items:")
            for i, item in enumerate(cart['items'], 1):
                print(f"{i}. {item['title']} - ${item['price']} x {item['quantity']}")
        else:
            print_json(response.json())
        
        # 8.3: Remove item from cart
        if response.status_code == 200 and cart['items']:
            item_to_remove = cart['items'][0]['product_id']
            print(f"\n8.3: Removing product {item_to_remove} from cart")
            delete_data = {
                "user_id": TEST_USER_ID,
                "product_id": item_to_remove
            }
            
            # Try different approaches for different httpx versions
            try:
                # Method 1: Using query parameters instead of body
                delete_url = f"{API_HOST}/cart/item?user_id={TEST_USER_ID}&product_id={item_to_remove}"
                response = await client.delete(delete_url)
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    cart = response.json()
                    print(f"Item removed, cart now contains {len(cart['items'])} items")
                else:
                    try:
                        print_json(response.json())
                    except:
                        print(f"Response content: {response.text[:100]}...")
            except Exception as e:
                print(f"Error removing item from cart: {e}")
        
        print("\n===== API TESTING COMPLETE =====")

if __name__ == "__main__":
    asyncio.run(test_all_apis())
