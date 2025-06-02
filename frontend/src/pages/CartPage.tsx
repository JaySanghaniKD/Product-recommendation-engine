import React from 'react';
import { 
  Container, Typography, Box, Paper, Button, Divider,
  Grid, CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import CartItem from '../components/CartItem';
import { ShoppingBag as ShoppingBagIcon } from '@mui/icons-material';

const CartPage: React.FC = () => {
  const { cart, loading, clearCart } = useCart();
  const navigate = useNavigate();
  
  // Calculate subtotal
  const subtotal = cart?.items.reduce((sum, item) => sum + (item.price * item.quantity), 0) || 0;
  const taxRate = 0.07; // 7% tax rate
  const tax = subtotal * taxRate;
  const total = subtotal + tax;
  
  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" my={8}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  
  if (!cart || cart.items.length === 0) {
    return (
      <Container maxWidth="md">
        <Paper sx={{ p: 4, my: 4, textAlign: 'center' }}>
          <ShoppingBagIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Your cart is empty
          </Typography>
          <Typography variant="body1" paragraph>
            Looks like you haven't added any products to your cart yet.
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => navigate('/')}
            size="large"
          >
            Start Shopping
          </Button>
        </Paper>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" sx={{ my: 4 }}>
        Your Shopping Cart
      </Typography>
      
      <Grid container spacing={4}>
        {/* Cart Items */}
        <Grid xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cart Items ({cart.items.length})
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {cart.items.map(item => (
              <CartItem key={item.product_id} item={item} />
            ))}
            
            <Box display="flex" justifyContent="space-between" mt={3}>
              <Button 
                variant="outlined" 
                color="primary"
                onClick={() => navigate('/')}
              >
                Continue Shopping
              </Button>
              <Button 
                variant="outlined" 
                color="error"
                onClick={() => clearCart()}
              >
                Clear Cart
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        {/* Order Summary */}
        <Grid xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Order Summary
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body1">Subtotal:</Typography>
              <Typography variant="body1">${subtotal.toFixed(2)}</Typography>
            </Box>
            
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body1">Tax (7%):</Typography>
              <Typography variant="body1">${tax.toFixed(2)}</Typography>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Box display="flex" justifyContent="space-between" mb={3}>
              <Typography variant="h6">Total:</Typography>
              <Typography variant="h6" color="primary">${total.toFixed(2)}</Typography>
            </Box>
            
            <Button 
              variant="contained" 
              color="primary" 
              fullWidth
              size="large"
              onClick={() => alert('Checkout functionality would go here!')}
            >
              Proceed to Checkout
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default CartPage;
