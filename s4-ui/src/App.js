import React, { useState, useEffect, createContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/AuthPage';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DocumentsPage from './pages/DocumentsPage';
import SearchPage from './pages/SearchPage';
import ProfilePage from './pages/ProfilePage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import PaymentPage from './pages/PaymentPage';
import OAuthCallbackPage from './pages/OAuthCallbackPage';
import ApiPage from './pages/ApiPage';
import API from './services/api';
// import ApiService from './services/api-service';
import './styles/index.css';

// Import SuperTokens
import { initSuperTokens } from './config/supertokens';
import Session from 'supertokens-auth-react/recipe/session';

// Initialize SuperTokens
initSuperTokens();

// Create Auth Context
export const AuthContext = createContext();

// Authentication state management

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log('Checking authentication status...');
        console.log('Current URL:', window.location.href);
        
        // Check URL parameters for token from OAuth flow
        const urlParams = new URLSearchParams(window.location.search);
        const tokenFromUrl = urlParams.get('token');
        const emailFromUrl = urlParams.get('email');
        
        if (tokenFromUrl && emailFromUrl) {
          // Store the token and user info in localStorage
          localStorage.setItem('token', tokenFromUrl);
          localStorage.setItem('email', emailFromUrl);
          
          const userData = {
            email: emailFromUrl,
            id: tokenFromUrl.split('-')[1] // Extract user ID from token
          };
          setUser(userData);
          setIsAuthenticated(true);
          
          // Log successful authentication
          console.log('Successfully authenticated with Google:', emailFromUrl);
          console.log('Token stored in localStorage:', tokenFromUrl);
          
          // Clean up URL parameters after a short delay to ensure state is updated
          setTimeout(() => {
            window.history.replaceState({}, document.title, window.location.pathname);
            console.log('URL parameters cleaned up');
            
            // Force a re-render if we're on the dashboard page
            if (window.location.pathname === '/dashboard') {
              console.log('Already on dashboard, forcing re-render');
              setLoading(false);
            }
          }, 500);
        } else {
          // Check for token in local storage
          const token = localStorage.getItem('token');
          const email = localStorage.getItem('email');
          
          console.log('No URL parameters, checking localStorage');
          console.log('Token in localStorage:', token ? 'Present' : 'Not found');
          console.log('Email in localStorage:', email || 'Not found');
          
          if (token) {
            // Use stored email if available
            if (email) {
              setUser({ email, id: token.split('-')[1] });
              setIsAuthenticated(true);
              console.log('User authenticated from localStorage');
            } else {
              // Verify token and get user info
              try {
                console.log('Verifying token with API...');
                const response = await API.verifyToken(token);
                setUser(response.data.user);
                setIsAuthenticated(true);
                console.log('Token verified successfully');
              } catch (tokenError) {
                console.error('API token error:', tokenError);
                localStorage.removeItem('token');
                localStorage.removeItem('email');
                console.log('Token verification failed, cleared localStorage');
              }
            }
          } else {
            console.log('No authentication token found');
          }
        }
      } catch (error) {
        console.error('Auth error:', error);
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);
  
  // Handle login
  const handleLogin = (userData, token) => {
    setUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('token', token);
    
    // Also store email for easy access
    if (userData && userData.email) {
      localStorage.setItem('email', userData.email);
      console.log('Stored user email in localStorage:', userData.email);
    }
  };
  
  // Handle Google login
  const handleGoogleLogin = () => {
    // Directly redirect to the backend's Google OAuth endpoint
    console.log('Redirecting to Google OAuth endpoint');
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    window.location.href = `${apiUrl}/auth/oauth/google`;
  };
  
  // Handle logout
  const handleLogout = () => {
    // Clear user state and local storage
    setUser(null);
    setIsAuthenticated(false);
    
    // Clear all authentication data
    localStorage.removeItem('token');
    localStorage.removeItem('email');
    localStorage.removeItem('user');
    localStorage.removeItem('adminKey');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    
    // Also sign out from SuperTokens if session exists
    Session.signOut().catch(error => {
      console.error('Error signing out from SuperTokens:', error);
    });
    
    console.log('User logged out successfully');
    
    // Redirect to home page
    window.location.href = '/';
  };
  
  // Auth protected route component
  const ProtectedRoute = ({ children }) => {
    if (loading) return <div className="loading">Loading...</div>;
    
    // Check for token in localStorage directly as a fallback
    const hasToken = isAuthenticated || localStorage.getItem('token');
    
    if (!hasToken) {
      // Redirect to login page if not authenticated
      console.log('Not authenticated, redirecting to login page');
      return <Navigate to="/login" />;
    }
    
    // If we have a token but user state is not set, update it
    if (!isAuthenticated && hasToken) {
      const email = localStorage.getItem('email');
      if (email) {
        const userData = { email, id: hasToken.split('-')[1] || 'user-id' };
        setUser(userData);
        setIsAuthenticated(true);
        console.log('Set user state from localStorage:', userData);
      }
    }
    
    return children;
  };
  
  // Admin protected route component
  const AdminRoute = ({ children }) => {
    if (loading) return <div className="loading">Loading...</div>;
    
    const adminKey = localStorage.getItem('adminKey');
    
    if (!isAuthenticated || !adminKey) {
      return <Navigate to="/" />;
    }
    
    return children;
  };
  
  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      user, 
      handleLogin, 
      handleLogout,
      handleGoogleLogin
    }}>
      <Navbar />
      <Routes>
        {/* Authentication Routes */}
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/auth/callback/google" element={<OAuthCallbackPage />} />
        
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/api" element={<ApiPage />} />
          
          {/* Protected routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />
          
          <Route path="/documents" element={
            <ProtectedRoute>
              <DocumentsPage />
            </ProtectedRoute>
          } />
          
          <Route path="/search" element={
            <ProtectedRoute>
              <SearchPage />
            </ProtectedRoute>
          } />
          
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } />
          
          <Route path="/payment" element={
            <ProtectedRoute>
              <PaymentPage />
            </ProtectedRoute>
          } />
          
          {/* Admin routes */}
          <Route path="/admin/dashboard" element={
            <AdminRoute>
              <AdminDashboardPage />
            </AdminRoute>
          } />
          
          {/* Redirect unknown routes to home */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthContext.Provider>
  );
}

export default App;  