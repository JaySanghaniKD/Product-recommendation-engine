import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Box, TextField, Button, Grid, 
  Paper, CircularProgress, Divider, Chip,
  InputAdornment, IconButton, useTheme, useMediaQuery
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { getFeaturedProducts, getUserHistory } from '../services/api';
import ProductCard from '../components/ProductCard';
import { Product } from '../types/models';
import { 
  Search as SearchIcon, 
  Mic as MicIcon,
  LocalFireDepartment as TrendingIcon,
  HistoryOutlined as HistoryIcon
} from '@mui/icons-material';

const HeroSection = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(6),
  textAlign: 'center',
  color: theme.palette.text.primary,
  background: `linear-gradient(45deg, ${theme.palette.primary.light} 0%, ${theme.palette.secondary.light} 100%)`,
  marginBottom: theme.spacing(4),
  borderRadius: theme.spacing(2),
  boxShadow: theme.shadows[4],
}));

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isSearching, setIsSearching] = useState<boolean>(false);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Parallel API calls for better performance
        const [featuredData, historyData] = await Promise.all([
          getFeaturedProducts(8), // Increased to 8 since we removed categories
          getUserHistory()
        ]);
        
        setFeaturedProducts(featuredData);
        
        // Extract search queries from history
        const searches = historyData.searches || [];
        const searchQueries = searches
          .slice(0, 3)
          .map((s: any) => s.details?.query || '')
          .filter(Boolean);
        
        setRecentSearches(searchQueries);
      } catch (error) {
        console.error('Error fetching home page data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setIsSearching(true);
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };
  
  const handleRecentSearchClick = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };
  
  return (
    <Container maxWidth="lg">
      <HeroSection elevation={3}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
          Discover Products with AI
        </Typography>
        <Typography variant="h6" gutterBottom sx={{ mb: 4, maxWidth: '700px', mx: 'auto' }}>
          Find exactly what you're looking for using natural language search
        </Typography>
        
        <Box component="form" onSubmit={handleSearch} sx={{ maxWidth: '700px', mx: 'auto' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Try 'smartphone with good camera under $1000'"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            disabled={isSearching}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="primary" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  {isSearching ? (
                    <CircularProgress size={24} />
                  ) : (
                    <IconButton>
                      <MicIcon color="primary" />
                    </IconButton>
                  )}
                </InputAdornment>
              ),
              sx: { borderRadius: 3, py: 0.5 }
            }}
          />
          <Button 
            type="submit" 
            variant="contained" 
            color="primary" 
            size="large" 
            disabled={isSearching || !searchQuery.trim()}
            sx={{ 
              mt: 2, 
              px: 4, 
              py: 1.5, 
              borderRadius: 2,
              position: 'relative',
              minWidth: '200px'
            }}
          >
            {isSearching ? (
              <>
                <CircularProgress 
                  size={24} 
                  color="inherit" 
                  sx={{ 
                    position: 'absolute',
                    left: 'calc(50% - 12px)',
                  }} 
                />
                <span style={{ opacity: 0 }}>Search with AI</span>
              </>
            ) : (
              'Search with AI'
            )}
          </Button>
        </Box>
      </HeroSection>
      
      {loading ? (
        <Box display="flex" justifyContent="center" my={8}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {recentSearches.length > 0 && (
            <Box mb={5}>
              <Box display="flex" alignItems="center" mb={2}>
                <HistoryIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h5" fontWeight="bold">
                  Recent Searches
                </Typography>
              </Box>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {recentSearches.map((query, index) => (
                  <Chip
                    key={index}
                    label={query}
                    onClick={() => handleRecentSearchClick(query)}
                    color="primary"
                    variant="outlined"
                    clickable
                    sx={{ px: 1, py: 2.5, fontWeight: 'medium' }}
                  />
                ))}
              </Box>
            </Box>
          )}
          
          <Box mb={5}>
            <Box display="flex" alignItems="center" mb={2}>
              <TrendingIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h5" fontWeight="bold">
                Featured Products
              </Typography>
            </Box>
            <Grid container spacing={4}>
              {featuredProducts.map(product => (
                <Grid key={product.id} xs={12} sm={6} md={4} sx={{ p: 1 }}>
                  <ProductCard product={product} variant="standard" />
                </Grid>
              ))}
            </Grid>
          </Box>
        </>
      )}
    </Container>
  );
};

export default HomePage;
