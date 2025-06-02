import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Cart, CartItem } from '../types/models';
import { getCart, addToCart, removeFromCart } from '../services/api';
import { toast } from 'react-toastify';

interface CartContextType {
  cart: Cart | null;
  loading: boolean;
  error: string | null;
  addItemToCart: (productId: number, quantity?: number) => Promise<void>;
  removeItemFromCart: (productId: number) => Promise<void>;
  clearCart: () => void;
  itemCount: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Calculate total items in cart
  const itemCount = cart?.items.reduce((sum, item) => sum + item.quantity, 0) || 0;

  // Fetch cart on component mount
  useEffect(() => {
    const fetchCart = async () => {
      try {
        setLoading(true);
        const cartData = await getCart();
        setCart(cartData);
        setError(null);
      } catch (err) {
        console.error('Error fetching cart:', err);
        setError('Failed to load cart. Please try again later.');
        // Don't set cart to null here, as it might be a temporary error
      } finally {
        setLoading(false);
      }
    };

    fetchCart();
  }, []);

  // Add item to cart
  const addItemToCart = async (productId: number, quantity: number = 1) => {
    try {
      setLoading(true);
      const updatedCart = await addToCart(productId, quantity);
      setCart(updatedCart);
      toast.success('Item added to cart!');
    } catch (err) {
      console.error('Error adding item to cart:', err);
      setError('Failed to add item to cart. Please try again.');
      toast.error('Failed to add item to cart');
    } finally {
      setLoading(false);
    }
  };

  // Remove item from cart
  const removeItemFromCart = async (productId: number) => {
    try {
      setLoading(true);
      const updatedCart = await removeFromCart(productId);
      setCart(updatedCart);
      toast.success('Item removed from cart!');
    } catch (err) {
      console.error('Error removing item from cart:', err);
      setError('Failed to remove item from cart. Please try again.');
      toast.error('Failed to remove item from cart');
    } finally {
      setLoading(false);
    }
  };

  // Clear cart (client-side only)
  const clearCart = () => {
    setCart(prev => ({
      ...prev!,
      items: []
    } as Cart));
  };

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        error,
        addItemToCart,
        removeItemFromCart,
        clearCart,
        itemCount
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

// Custom hook for using the cart context
export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
