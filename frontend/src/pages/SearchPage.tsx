import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Box, Grid, CircularProgress, 
  Paper, Button, Chip, Skeleton
} from '@mui/material';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { searchProducts } from '../services/api';
import ProductCard from '../components/ProductCard';
import { Product } from '../types/models';
import { Home as HomeIcon } from '@mui/icons-material';

const SearchPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const query = searchParams.get('q') || '';
  
  const [loading, setLoading] = useState<boolean>(true);
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [message, setMessage] = useState<string>('');
  const [searchStartTime, setSearchStartTime] = useState<number>(Date.now());
  
  useEffect(() => {
    const fetchData = async () => {
      if (!query) {
        navigate('/');
        return;
      }
      
      // Record search start time to calculate duration
      const startTime = Date.now();
      setSearchStartTime(startTime);
      setLoading(true);
      
      try {
        // Perform the search
        const searchData = await searchProducts(query);
        setSearchResults(searchData.search_results || []);
        setMessage(searchData.message || '');
        
        // Calculate and log search duration
        const duration = Date.now() - startTime;
        console.log(`Search completed in ${duration}ms`);
        
      } catch (error) {
        console.error('Error fetching search results:', error);
        setMessage('An error occurred while searching. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [query, navigate]);
  
  // Calculate search duration for display
  const searchDuration = loading ? null : ((Date.now() - searchStartTime) / 1000).toFixed(1);
  
  return (
    <Container maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" my={4}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Search Results for: "{query}"
          </Typography>
          {message && (
            <Typography variant="body1" color="text.secondary">
              {message}
            </Typography>
          )}
          {!loading && searchDuration && (
            <Typography variant="caption" color="text.secondary">
              Found {searchResults.length} results in {searchDuration} seconds
            </Typography>
          )}
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<HomeIcon />}
          onClick={() => navigate('/')}
        >
          Back to Home
        </Button>
      </Box>
      
      {loading ? (
        <Box sx={{ my: 6 }}>
          {/* Skeleton loading state */}
          <Grid container spacing={4}>
            {Array.from(new Array(6)).map((_, index) => (
              <Grid key={index} xs={12} sm={6} md={4}>
                <Paper 
                  sx={{ 
                    p: 2, 
                    mb: 2, 
                    borderRadius: 2,
                    height: 350,
                    display: 'flex',
                    flexDirection: 'column'
                  }}
                >
                  <Skeleton variant="rectangular" height={200} animation="wave" sx={{ mb: 2, borderRadius: 1 }} />
                  <Skeleton variant="text" width="30%" height={24} animation="wave" />
                  <Skeleton variant="text" width="90%" height={32} animation="wave" />
                  <Skeleton variant="text" width="60%" height={24} animation="wave" />
                  <Box display="flex" justifyContent="space-between" mt="auto">
                    <Skeleton variant="text" width="30%" height={32} animation="wave" />
                    <Skeleton variant="rectangular" width="40%" height={36} animation="wave" sx={{ borderRadius: 1 }} />
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
          
          <Box textAlign="center" mt={4} p={2} borderRadius={1} bgcolor="rgba(25, 118, 210, 0.05)">
            <Typography variant="body1">
              Searching for "{query}"... This may take a few seconds
            </Typography>
            <Box display="flex" alignItems="center" justifyContent="center" my={2}>
              <CircularProgress size={24} sx={{ mr: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Our AI is searching for the best matches
              </Typography>
            </Box>
          </Box>
        </Box>
      ) : searchResults.length > 0 ? (
        <Grid container spacing={4}>
          {searchResults.map(product => (
            <Grid key={product.id} xs={12} sm={6} md={4} lg={3}>
              <ProductCard product={product} variant="detailed" />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper sx={{ p: 5, textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            No products found
          </Typography>
          <Typography variant="body1" paragraph>
            Try searching for something else.
          </Typography>
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => navigate('/')}
          >
            Return to Home
          </Button>
        </Paper>
      )}
    </Container>
  );
};

export default SearchPage;
