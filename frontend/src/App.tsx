import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Import contexts
import { CartProvider } from './context/CartContext';

// Import components
import Navbar from './components/Navbar';

// Import pages
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import ProductDetailPage from './pages/ProductDetailPage';
import CartPage from './pages/CartPage';
import HistoryPage from './pages/HistoryPage';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#4F46E5', // indigo
    },
    secondary: {
      main: '#10B981', // emerald
    },
    background: {
      default: '#F9FAFB', // light gray
    },
    text: {
      primary: '#111827', // dark gray
    },
    error: {
      main: '#F59E0B', // amber as accent/error
    },
  },
  typography: {
    fontFamily: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 700,
    },
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 700,
    },
    h6: {
      fontWeight: 700,
    },
    body1: {
      fontWeight: 400,
    },
    body2: {
      fontWeight: 400,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <CartProvider>
        <Router>
          <Navbar />
          <Box component="main" sx={{ minHeight: '100vh', py: 4 }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/products/:productId" element={<ProductDetailPage />} />
              <Route path="/products" element={<SearchPage />} />
              <Route path="/cart" element={<CartPage />} />
              <Route path="/history" element={<HistoryPage />} />
            </Routes>
          </Box>
          <ToastContainer position="bottom-right" />
        </Router>
      </CartProvider>
    </ThemeProvider>
  );
}

export default App;
