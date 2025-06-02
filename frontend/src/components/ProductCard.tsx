import React from 'react';
import { Card, CardContent, CardMedia, Typography, Button, Box, Chip, Rating, Skeleton } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Product } from '../types/models';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { AddShoppingCart as CartIcon } from '@mui/icons-material';

interface ProductCardProps {
  product: Product;
  variant?: 'compact' | 'standard' | 'detailed';
  loading?: boolean;
}

const StyledCard = styled(Card)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  overflow: 'hidden',
  borderRadius: theme.shape.borderRadius * 1.5,
  margin: theme.spacing(1), // Add margin around the cards
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: theme.shadows[10],
  },
}));

const CardContentNoPadding = styled(CardContent)({
  padding: '16px',
  '&:last-child': {
    paddingBottom: '16px',
  },
});

const TruncatedTypography = styled(Typography)({
  display: '-webkit-box',
  WebkitLineClamp: 2,
  WebkitBoxOrient: 'vertical',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  minHeight: '3em',
});

const JustificationBox = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(1),
  padding: theme.spacing(1.5),
  backgroundColor: theme.palette.primary.light + '20', // 20% opacity
  borderRadius: theme.shape.borderRadius,
  border: `1px solid ${theme.palette.primary.light}30`, // 30% opacity
}));

const discountPrice = (price: number, discount?: number): number => {
  if (!discount) return price;
  return price * (1 - discount / 100);
};

const ProductCard: React.FC<ProductCardProps> = ({ product, variant = 'standard', loading = false }) => {
  const navigate = useNavigate();
  const { addItemToCart } = useCart();
  
  if (loading) {
    return (
      <StyledCard>
        <Skeleton variant="rectangular" height={200} animation="wave" />
        <CardContentNoPadding>
          <Skeleton variant="text" width="30%" height={24} animation="wave" />
          <Skeleton variant="text" width="90%" height={32} animation="wave" />
          <Skeleton variant="text" width="60%" height={24} animation="wave" />
          <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
            <Skeleton variant="text" width="30%" height={32} animation="wave" />
            <Skeleton variant="rectangular" width="40%" height={36} animation="wave" />
          </Box>
        </CardContentNoPadding>
      </StyledCard>
    );
  }
  
  const { id, title, description, price, category, thumbnail, justification, discountPercentage, rating } = product;
  
  const fallbackImageUrl = 'https://via.placeholder.com/300x200?text=No+Image';
  
  const handleAddToCart = (e: React.MouseEvent) => {
    e.stopPropagation();
    addItemToCart(id, 1);
  };
  
  const handleCardClick = () => {
    navigate(`/products/${id}`);
  };

  return (
    <StyledCard onClick={handleCardClick}>
      <CardMedia
        component="img"
        height={variant === 'compact' ? '140' : '200'}
        image={thumbnail || fallbackImageUrl}
        alt={title}
        sx={{ objectFit: 'contain', bgcolor: '#f9f9f9', pt: 1 }}
      />
      <CardContentNoPadding>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
          <Chip 
            label={category} 
            size="small" 
            color="primary" 
            variant="outlined"
          />
          {rating && <Rating value={rating} precision={0.5} size="small" readOnly />}
        </Box>
        
        <TruncatedTypography gutterBottom variant="h6">
          {title}
        </TruncatedTypography>
        
        {variant !== 'compact' && (
          <TruncatedTypography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {description}
          </TruncatedTypography>
        )}
        
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
          <Box>
            {discountPercentage ? (
              <>
                <Typography variant="body2" color="text.secondary" sx={{ textDecoration: 'line-through' }}>
                  ${price.toFixed(2)}
                </Typography>
                <Typography variant="h6" color="error" fontWeight="bold">
                  ${discountPrice(price, discountPercentage).toFixed(2)}
                </Typography>
              </>
            ) : (
              <Typography variant="h6" color="primary" fontWeight="bold">
                ${price.toFixed(2)}
              </Typography>
            )}
          </Box>
          <Button 
            variant="contained" 
            size="small" 
            onClick={handleAddToCart}
            color="primary"
            startIcon={<CartIcon />}
            sx={{ borderRadius: 4 }}
          >
            Add
          </Button>
        </Box>
        
        {variant === 'detailed' && justification && (
          <JustificationBox>
            <Typography variant="subtitle2" fontWeight="bold" color="primary">
              AI Recommendation:
            </Typography>
            <Typography variant="body2">
              {justification}
            </Typography>
          </JustificationBox>
        )}
      </CardContentNoPadding>
    </StyledCard>
  );
};

export default ProductCard;
