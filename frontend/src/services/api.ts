import axios from 'axios';

// Create an Axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// User ID - hardcoded for now
const USER_ID = 'user_1';

// Search API
export const searchProducts = async (query: string) => {
  const response = await api.post('/search/', {
    user_id: USER_ID,
    query,
  });
  return response.data;
};

// Product APIs
export const getProductById = async (productId: number) => {
  const response = await api.get(`/products/${productId}`);
  return response.data;
};

export const listProducts = async (params: {
  page?: number;
  limit?: number;
  category?: string;
  min_price?: number;
  max_price?: number;
  sort?: string;
}) => {
  const response = await api.get('/products/', { params });
  return response.data;
};

// Featured products (replacing recommendations)
export const getFeaturedProducts = async (count: number = 6) => {
  const response = await api.get('/products/featured/', {
    params: { limit: count }
  });
  return response.data;
};

// User History API
export const getUserHistory = async () => {
  const response = await api.get(`/history/${USER_ID}`);
  return response.data;
};

// Cart APIs
export const getCart = async () => {
  const response = await api.get(`/cart/${USER_ID}`);
  return response.data;
};

export const addToCart = async (productId: number, quantity: number = 1) => {
  const response = await api.post('/cart/item', {
    user_id: USER_ID,
    product_id: productId,
    quantity,
  });
  return response.data;
};

export const removeFromCart = async (productId: number) => {
  const response = await api.delete(`/cart/item`, {
    params: {
      user_id: USER_ID,
      product_id: productId,
    },
  });
  return response.data;
};

// Update the trackProductView function
export const trackProductView = async (productId: number, productTitle: string) => {
  try {
    // Create the payload with the EXACT interaction_type expected by the backend
    const payload = {
      user_id: USER_ID,
      interaction_type: 'view_product', // This must match exactly what the backend expects
      details: {
        product_id: productId,
        product_title: productTitle
      }
    };
    
    console.log('Tracking product view with payload:', payload);
    
    // Send the tracking request
    const response = await api.post('/history/track', payload);
    console.log('Product view tracking response:', response.data);
    
    if (response.data.status === 'success') {
      return response.data;
    } else {
      console.error('Error from tracking endpoint:', response.data.message);
      return null;
    }
  } catch (error) {
    console.error('Error tracking product view:', error);
    return null;
  }
};

export default api;
