import React, { useState } from 'react';
import { Box, Card, CardMedia, Typography, IconButton, TextField, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Delete, Add, Remove } from '@mui/icons-material';
import { CartItem as CartItemType } from '../types/models';
import { useCart } from '../context/CartContext';

interface CartItemProps {
  item: CartItemType;
}

const StyledCard = styled(Card)(({ theme }) => ({
  display: 'flex',
  marginBottom: theme.spacing(2),
  padding: theme.spacing(2),
  transition: 'background-color 0.3s ease',
}));

const ImageContainer = styled(Box)(({ theme }) => ({
  width: 100,
  height: 100,
  marginRight: theme.spacing(2),
  [theme.breakpoints.down('sm')]: {
    width: 80,
    height: 80,
  },
}));

const QuantityContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginTop: theme.spacing(1),
}));

const CartItem: React.FC<CartItemProps> = ({ item }) => {
  const { addItemToCart, removeItemFromCart } = useCart();
  const { product_id, title, price, quantity, thumbnail } = item;
  const fallbackImageUrl = 'https://via.placeholder.com/100x100?text=No+Image';
  
  const handleIncreaseQuantity = () => {
    addItemToCart(product_id, 1);
  };
  
  const handleDecreaseQuantity = () => {
    if (quantity > 1) {
      addItemToCart(product_id, -1);
    }
  };
  
  const handleRemoveItem = () => {
    removeItemFromCart(product_id);
  };
  
  return (
    <StyledCard>
      <ImageContainer>
        <CardMedia
          component="img"
          height="100%"
          image={thumbnail || fallbackImageUrl}
          alt={title}
        />
      </ImageContainer>
      
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="subtitle1" component="div">
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          ${price.toFixed(2)} each
        </Typography>
        
        <QuantityContainer>
          <IconButton 
            size="small" 
            onClick={handleDecreaseQuantity}
            disabled={quantity <= 1}
          >
            <Remove fontSize="small" />
          </IconButton>
          <Typography sx={{ mx: 1 }}>
            {quantity}
          </Typography>
          <IconButton 
            size="small" 
            onClick={handleIncreaseQuantity}
          >
            <Add fontSize="small" />
          </IconButton>
        </QuantityContainer>
      </Box>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <Typography variant="subtitle1" fontWeight="bold">
          ${(price * quantity).toFixed(2)}
        </Typography>
        <IconButton 
          color="error" 
          onClick={handleRemoveItem}
        >
          <Delete />
        </IconButton>
      </Box>
    </StyledCard>
  );
};

export default CartItem;
