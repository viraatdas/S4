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
        
        // Use Google's token endpoint directly instead of going through our backend
        // This avoids potential CORS issues and simplifies the flow
        const tokenUrl = 'https://oauth2.googleapis.com/token';
        const websiteDomain = process.env.REACT_APP_WEBSITE_DOMAIN || 'http://localhost:3000';
        const redirectUri = `${websiteDomain}/auth/callback/google`;
        
        const tokenData = new URLSearchParams();
        tokenData.append('client_id', GOOGLE_CLIENT_ID);
        tokenData.append('client_secret', GOOGLE_CLIENT_SECRET);
        tokenData.append('code', code);
        tokenData.append('redirect_uri', redirectUri);
        tokenData.append('grant_type', 'authorization_code');
        
        console.log('OAuthCallbackPage: Token request data:', {
          client_id: GOOGLE_CLIENT_ID,
          code: code.substring(0, 10) + '...',
          redirect_uri: redirectUri,
          grant_type: 'authorization_code'
        });
        
        const tokenResponse = await fetch(tokenUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: tokenData
        });
        
        if (!tokenResponse.ok) {
          const errorText = await tokenResponse.text();
          console.error('Token exchange error:', errorText);
          throw new Error(`Token exchange failed: ${tokenResponse.status}`);
        }
        
        const tokenJson = await tokenResponse.json();
        console.log('OAuthCallbackPage: Received tokens:', Object.keys(tokenJson));
        
        // Get user info from Google
        const userInfoUrl = 'https://www.googleapis.com/oauth2/v3/userinfo';
        const userResponse = await fetch(userInfoUrl, {
          headers: {
            'Authorization': `Bearer ${tokenJson.access_token}`
          }
        });
        
        if (!userResponse.ok) {
          const errorText = await userResponse.text();
          console.error('User info error:', errorText);
          throw new Error(`Failed to get user info: ${userResponse.status}`);
        }
        
        const userInfo = await userResponse.json();
        console.log('OAuthCallbackPage: User info:', {
          sub: userInfo.sub,
          email: userInfo.email,
          name: userInfo.name
        });
        
        // Create a session token
        const sessionToken = `st-${userInfo.sub}-${Date.now()}`;
        
        // Prepare response data with user information from Google
        const data = {
          success: true,
          token: sessionToken,
          email: userInfo.email,
          user: {
            id: userInfo.sub,
            email: userInfo.email,
            name: userInfo.name || '',
            picture: userInfo.picture || ''
          }
        };
        
        console.log('OAuthCallbackPage: Authentication data:', data);
        
        // Store tokens
        localStorage.setItem('token', data.token);
        localStorage.setItem('email', data.email);
        
        // Store user data if available
        if (data.user) {
          localStorage.setItem('user', JSON.stringify(data.user));
        }
        
        if (handleOAuthSuccess) {
          handleOAuthSuccess({
            email: data.email,
            id: data.user?.id || data.token.split('-')[1] || 'user-id',
            name: data.user?.name,
            picture: data.user?.picture
          }, data.token);
        }
        
        console.log('OAuthCallbackPage: Successfully authenticated with Google');
        
        // Redirect to dashboard
        navigate('/dashboard', { replace: true });
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