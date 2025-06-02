import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Box, Grid, Paper, Button, 
  CircularProgress, Divider, Breadcrumbs, Link,
  IconButton, Chip, Rating
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { getProductById, getFeaturedProducts, trackProductView } from '../services/api';
import { Product } from '../types/models';
import { useCart } from '../context/CartContext';
import ProductCard from '../components/ProductCard';
import { 
  Add as AddIcon, 
  Remove as RemoveIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';

const ProductDetailPage: React.FC = () => {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const { addItemToCart } = useCart();
  
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [quantity, setQuantity] = useState<number>(1);
  const [similarProducts, setSimilarProducts] = useState<Product[]>([]);
  
  useEffect(() => {
    const fetchData = async () => {
      if (!productId) return;
      
      try {
        setLoading(true);
        
        // Fetch product details
        const productData = await getProductById(parseInt(productId));
        setProduct(productData);
        
        // Track this product view (only after successful product fetch)
        if (productData) {
          console.log('About to track product view for:', productData.id, productData.title);
          
          // For more reliable tracking, use await directly in a try/catch block
          try {
            const trackingResult = await trackProductView(productData.id, productData.title);
            console.log('Product view tracking result:', trackingResult);
          } catch (err) {
            console.error('Failed to track product view:', err);
          }
        }
        
        // Use featured products instead of recommendations
        const featuredData = await getFeaturedProducts(4);
        // Filter out the current product
        const filtered = featuredData.filter((p: Product) => p.id !== parseInt(productId));
        setSimilarProducts(filtered);
        
      } catch (error) {
        console.error('Error fetching product details:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [productId]);
  
  const handleQuantityChange = (value: number) => {
    const newQuantity = quantity + value;
    if (newQuantity >= 1) {
      setQuantity(newQuantity);
    }
  };
  
  const handleAddToCart = () => {
    if (product) {
      addItemToCart(product.id, quantity);
    }
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" my={8}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  
  if (!product) {
    return (
      <Container maxWidth="lg">
        <Paper sx={{ p: 4, my: 4, textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom>
            Product Not Found
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/')}
          >
            Back to Home
          </Button>
        </Paper>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Box my={3}>
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link underline="hover" color="inherit" onClick={() => navigate('/')} sx={{ cursor: 'pointer' }}>
            Home
          </Link>
          <Typography color="text.primary">{product.title}</Typography>
        </Breadcrumbs>
        
        <Paper elevation={3} sx={{ 
          p: { xs: 3, md: 5 },  // Increased padding, responsive for different screen sizes
          borderRadius: 2, 
          mb: 5,  // Increased bottom margin
          mt: 2,  // Added top margin
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
        }}>
          <Grid container spacing={5}>  {/* Increased grid spacing from 4 to 5 */}
            {/* Product Image */}
            <Grid xs={12} md={6}>
              <Box 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  overflow: 'hidden',
                  borderRadius: 2,
                  backgroundColor: '#f9fafb',
                  p: 3,  // Increased padding from 2 to 3
                  m: { xs: 1, md: 2 },  // Added margin, responsive
                  border: '1px solid #eee',
                }}
              >
                <img 
                  src={product.thumbnail || 'https://via.placeholder.com/500x500?text=No+Image'} 
                  alt={product.title}
                  style={{ 
                    maxWidth: '100%', 
                    maxHeight: '400px', 
                    objectFit: 'contain',
                    transition: 'transform 0.3s ease',
                  }}
                  onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                  onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                />
              </Box>
            </Grid>
            
            {/* Product Info */}
            <Grid xs={12} md={6}>
              <Box sx={{ p: { xs: 1, md: 2 } }}>  {/* Added padding to the info box */}
                <Chip 
                  label={product.category} 
                  color="primary" 
                  variant="outlined" 
                  size="small"
                  sx={{ mb: 1 }}
                />
                <Typography variant="h4" gutterBottom fontWeight="bold">
                  {product.title}
                </Typography>
                
                {product.discountPercentage ? (
                  <Box display="flex" alignItems="center" mb={2}>
                    <Typography variant="body1" color="text.secondary" sx={{ textDecoration: 'line-through', mr: 2 }}>
                      ${product.price.toFixed(2)}
                    </Typography>
                    <Typography variant="h5" color="error" fontWeight="bold">
                      ${(product.price * (1 - product.discountPercentage/100)).toFixed(2)}
                    </Typography>
                    <Chip 
                      label={`${product.discountPercentage}% OFF`} 
                      color="error" 
                      size="small" 
                      sx={{ ml: 2 }}
                    />
                  </Box>
                ) : (
                  <Typography variant="h5" color="primary" gutterBottom fontWeight="bold">
                    ${product.price.toFixed(2)}
                  </Typography>
                )}
                
                {product.rating && (
                  <Box display="flex" alignItems="center" mb={2}>
                    <Rating value={product.rating} precision={0.5} readOnly />
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                      ({product.rating.toFixed(1)})
                    </Typography>
                  </Box>
                )}
                
                <Divider sx={{ my: 3 }} />
                
                <Typography variant="h6" gutterBottom>
                  Description
                </Typography>
                <Typography variant="body1" paragraph sx={{ mb: 3 }}>
                  {product.description}
                </Typography>
                
                {product.brand && (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    <strong>Brand:</strong> {product.brand}
                  </Typography>
                )}
                
                {product.stock !== undefined && (
                  <Box mb={2}>
                    <Typography variant="body2" color={product.stock > 0 ? "success.main" : "error.main"}>
                      {product.stock > 0 ? `In Stock (${product.stock} available)` : "Out of Stock"}
                    </Typography>
                  </Box>
                )}
                
                <Divider sx={{ my: 3 }} />
                
                <Box display="flex" alignItems="center" mb={3}>
                  <Typography variant="subtitle1" mr={2}>
                    Quantity:
                  </Typography>
                  <IconButton 
                    size="small" 
                    onClick={() => handleQuantityChange(-1)}
                    disabled={quantity <= 1}
                    sx={{ border: '1px solid #e0e0e0' }}
                  >
                    <RemoveIcon />
                  </IconButton>
                  <Typography variant="body1" sx={{ mx: 2, minWidth: '30px', textAlign: 'center' }}>
                    {quantity}
                  </Typography>
                  <IconButton 
                    size="small" 
                    onClick={() => handleQuantityChange(1)}
                    sx={{ border: '1px solid #e0e0e0' }}
                  >
                    <AddIcon />
                  </IconButton>
                </Box>
                
                <Button 
                  variant="contained" 
                  color="primary" 
                  size="large" 
                  fullWidth
                  onClick={handleAddToCart}
                  startIcon={<AddIcon />}
                  sx={{ py: 1.5, borderRadius: 2 }}
                >
                  Add to Cart
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>
        
        {/* Similar Products Section */}
        {similarProducts.length > 0 && (
          <Box mt={8} mb={4}>
            <Typography variant="h5" gutterBottom fontWeight="bold">
              You Might Also Like
            </Typography>
            <Divider sx={{ mb: 4 }} />
            <Grid container spacing={4}>
              {similarProducts.map(product => (
                <Grid key={product.id} xs={12} sm={6} md={3}>
                  <ProductCard product={product} variant="compact" />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default ProductDetailPage;
