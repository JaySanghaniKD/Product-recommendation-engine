import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Box, Paper, Divider, Grid,
  CircularProgress, List, ListItem, ListItemText,
  Chip, ListItemIcon, styled, Button
} from '@mui/material';
import { 
  Search as SearchIcon,
  Visibility as ViewIcon, 
  History as HistoryIcon
} from '@mui/icons-material';
import { getUserHistory } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

// Add the StyledListItem component
const StyledListItem = styled(ListItem)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(1.5),
  backgroundColor: theme.palette.background.paper,
  boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
    boxShadow: '0 3px 6px rgba(0,0,0,0.12)',
    transform: 'translateY(-2px)',
  },
  transition: 'background-color 0.3s ease, transform 0.2s ease, box-shadow 0.2s ease',
  cursor: 'pointer',
}));

// Add the formatTimestamp function
const formatTimestamp = (timestamp: string) => {
  try {
    return format(new Date(timestamp), 'MMM d, yyyy h:mm a');
  } catch (e) {
    return 'Unknown date';
  }
};

const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [debugInfo, setDebugInfo] = useState<string>('');
  
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        console.log('Fetching history data...');
        const historyData = await getUserHistory();
        console.log('History data received:', historyData);
        
        // Set debug info
        setDebugInfo(JSON.stringify(historyData, null, 2));
        
        // Check if we have product views
        if (historyData.product_views) {
          console.log(`Found ${historyData.product_views.length} product views`);
        } else {
          console.log('No product views found in history data');
        }
        
        setHistory(historyData);
      } catch (error) {
        console.error('Error fetching user history:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchHistory();
  }, []);
  
  const handleSearchClick = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };
  
  const handleProductClick = (productId: number) => {
    navigate(`/products/${productId}`);
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
  
  // Use a safe default for history data
  const historyData = history || { searches: [], product_views: [] };
  
  // Development-only debug information
  const showDebugInfo = process.env.NODE_ENV === 'development';
  
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" sx={{ my: 4 }}>
        Your Activity History
      </Typography>
      
      <Grid container spacing={4}>
        {/* Recent Searches */}
        <Grid xs={12} sx={{ p: 1 }}>  {/* Changed from md={6} to xs={12} to take full width */}
          <Paper elevation={3} sx={{ 
            p: 3, 
            height: '100%', 
            borderRadius: 2,
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            transition: 'box-shadow 0.3s ease',
            '&:hover': {
              boxShadow: '0 8px 24px rgba(0,0,0,0.12)'
            }
          }}>
            <Typography variant="h6" display="flex" alignItems="center" gutterBottom>
              <SearchIcon sx={{ mr: 1 }} />
              Recent Searches
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {historyData.searches && historyData.searches.length > 0 ? (
              <List sx={{ width: '100%', p: 1 }}>
                {historyData.searches.map((search: any, index: number) => (
                  <StyledListItem 
                    key={index}
                    onClick={() => handleSearchClick(search.details?.query || '')}
                    divider={false}
                  >
                    <ListItemText
                      primary={
                        <Typography variant="subtitle1" fontWeight="medium">
                          {search.details?.query || 'Unknown search'}
                        </Typography>
                      }
                      secondary={formatTimestamp(search.timestamp)}
                    />
                  </StyledListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 3 }}>
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  No search history yet
                </Typography>
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => navigate('/')}
                  sx={{ mt: 1 }}
                >
                  Start Searching
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>
        
        {/* Removed Product Views Section */}
      </Grid>
    </Container>
  );
};

export default HistoryPage;
