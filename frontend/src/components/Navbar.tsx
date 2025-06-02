import React, { useState } from 'react';
import { 
  AppBar, Toolbar, Typography, Box, 
  IconButton, Badge, Button,
  useMediaQuery, useTheme,
  Drawer, List, ListItem, ListItemText, ListItemIcon
} from '@mui/material';
import { 
  Menu as MenuIcon,
  ShoppingCart as CartIcon,
  Home as HomeIcon,
  History as HistoryIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { cart } = useCart();
  
  // Calculate cart item count
  const itemCount = cart?.items.reduce((total, item) => total + item.quantity, 0);
  
  // Mobile menu state
  const [drawerOpen, setDrawerOpen] = useState(false);
  
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  return (
    <AppBar position="sticky">
      <Toolbar>
        {isMobile && (
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={toggleDrawer}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
        
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 1, 
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
          onClick={() => navigate('/')}
        >
          AI Shop
        </Typography>
        
        <Box sx={{ display: { xs: 'flex' } }}>
          {!isMobile && (
            <>
              <Button color="inherit" onClick={() => navigate('/')}>
                Home
              </Button>
              
              <Button color="inherit" onClick={() => navigate('/history')}>
                History
              </Button>
            </>
          )}
          
          <IconButton 
            size="large" 
            aria-label="show cart items" 
            color="inherit"
            onClick={() => navigate('/cart')}
          >
            <Badge badgeContent={itemCount} color="error">
              <CartIcon />
            </Badge>
          </IconButton>
        </Box>
      </Toolbar>
      
      {/* Mobile drawer */}
      <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer}>
        <Box
          sx={{ width: 250 }}
          role="presentation"
          onClick={toggleDrawer}
        >
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            p: 2,
            borderBottom: `1px solid ${theme.palette.divider}`
          }}>
            <Typography variant="h6">Menu</Typography>
            <IconButton onClick={toggleDrawer}>
              <CloseIcon />
            </IconButton>
          </Box>
          
          <List>
            <ListItem button onClick={() => navigate('/')}>
              <ListItemIcon><HomeIcon /></ListItemIcon>
              <ListItemText primary="Home" />
            </ListItem>
            
            <ListItem button onClick={() => navigate('/history')}>
              <ListItemIcon><HistoryIcon /></ListItemIcon>
              <ListItemText primary="History" />
            </ListItem>
            
            <ListItem button onClick={() => navigate('/cart')}>
              <ListItemIcon>
                <Badge badgeContent={itemCount} color="error">
                  <CartIcon />
                </Badge>
              </ListItemIcon>
              <ListItemText primary="Cart" />
            </ListItem>
          </List>
        </Box>
      </Drawer>
    </AppBar>
  );
};

export default Navbar;
