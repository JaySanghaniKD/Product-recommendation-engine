// Product related types
export interface Product {
  id: number;
  title: string;
  description: string;
  category: string;
  price: number;
  discountPercentage?: number;  // Added for discount pricing
  rating?: number;              // Added for product ratings
  stock?: number;               // Added for inventory status
  brand?: string;               // Added for brand information
  tags?: string[];              // Added for product tags
  images?: string[];            // Added for multiple product images
  thumbnail?: string;
  justification?: string;
}

export interface ProductListResponse {
  items: Product[];
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
}

// Cart related types
export interface CartItem {
  product_id: number;
  title: string;
  price: number;
  quantity: number;
  thumbnail?: string;
}

export interface Cart {
  user_id: string;
  items: CartItem[];
  last_updated: string;
}

// Search related types
export interface SearchResult {
  query_received: string;
  user_id: string;
  search_results: Product[];
  message: string;
}

// User history related types
export interface UserHistory {
  searches: any[];
  product_views: any[];
  cart_actions: any[];
  recent: any[];
}
