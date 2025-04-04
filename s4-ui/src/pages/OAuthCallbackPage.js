import React, { useEffect, useState, useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Container, Spinner, Alert } from 'react-bootstrap';
import { AuthContext } from '../App';
// import API from '../services/api';
import '../styles/auth.css';

// Google OAuth credentials from environment variables
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '';
const GOOGLE_CLIENT_SECRET = process.env.REACT_APP_GOOGLE_CLIENT_SECRET || '';

const OAuthCallbackPage = () => {
  const { handleOAuthSuccess } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState('');
  // const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const handleGoogleCallback = async () => {
      // setIsLoading(true);
      console.log('OAuthCallbackPage: Handling Google callback');
      console.log('Current URL:', window.location.href);
      
      // First check if we already have token and email in the URL (from backend redirect)
      const queryParams = new URLSearchParams(location.search);
      const token = queryParams.get('token');
      const email = queryParams.get('email');
      
      // If we have token and email directly in URL, store them and redirect
      if (token && email) {
        console.log('OAuthCallbackPage: Received token and email directly in URL');
        localStorage.setItem('token', token);
        localStorage.setItem('email', email);
        
        if (handleOAuthSuccess) {
          handleOAuthSuccess({
            email,
            id: token.split('-')[1] || 'user-id'
          }, token);
        }
        
        // Redirect to dashboard with clean URL
        setTimeout(() => {
          console.log('OAuthCallbackPage: Redirecting to dashboard');
          navigate('/dashboard', { replace: true });
        }, 500);
        return;
      }
      
      // Otherwise, handle the standard OAuth flow
      const code = queryParams.get('code');
      const state = queryParams.get('state');
      const error = queryParams.get('error');
      
      console.log('OAuthCallbackPage: OAuth parameters:', { 
        code: code ? `${code.substring(0, 10)}...` : 'none', 
        state, 
        error 
      });
      
      if (error) {
        console.error('OAuthCallbackPage: Authentication error:', error);
        setError(`Authentication failed: ${error}`);
        // setIsLoading(false);
        return;
      }
      
      if (!code) {
        console.error('OAuthCallbackPage: Missing authorization code');
        setError('Invalid callback URL. Missing authorization code.');
        // setIsLoading(false);
        return;
      }
      
      try {
        console.log('OAuthCallbackPage: Exchanging code for token');
        
        // Forward the authorization code to our backend
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const backendUrl = `${apiUrl}/auth/callback/google?code=${code}`;
        
        console.log('OAuthCallbackPage: Forwarding code to backend:', {
          backendUrl: backendUrl.replace(code, code.substring(0, 10) + '...')
        });
        
        // Redirect to the backend URL with the code
        window.location.href = backendUrl;
        return; // Stop execution here as we're redirecting
      } catch (err) {
        console.error('OAuthCallbackPage: Google OAuth callback error:', err);
        
        // No fallback needed anymore since we're handling the OAuth flow directly
        console.error('OAuthCallbackPage: Authentication error:', err);
        setError('Failed to authenticate with Google. Please try again.');
        // setIsLoading(false);
      }
    };
    
    handleGoogleCallback();
  }, [location, navigate, handleOAuthSuccess]);
  
  if (error) {
    return (
      <Container fluid className="auth-container">
        <div className="auth-card-wrapper">
          <div className="auth-card">
            <div className="card-content text-center">
              <img src="/logo.svg" alt="S4 Logo" className="logo" />
              <Alert variant="danger" className="mt-4">
                <h4>Authentication Error</h4>
                <p>{error}</p>
                <button 
                  className="google-signin-button mt-3" 
                  onClick={() => navigate('/login')}
                >
                  Return to Login
                </button>
              </Alert>
            </div>
          </div>
        </div>
      </Container>
    );
  }
  
  return (
    <Container fluid className="auth-container">
      <div className="auth-card-wrapper">
        <div className="auth-card">
          <div className="card-content text-center">
            <img src="/logo.svg" alt="S4 Logo" className="logo" />
            <div className="mt-4">
              <Spinner animation="border" variant="primary" role="status" />
              <p className="mt-3">Completing your sign-in with Google...</p>
            </div>
          </div>
        </div>
      </div>
    </Container>
  );
};

export default OAuthCallbackPage;              