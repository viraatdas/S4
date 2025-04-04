import React, { useState, useContext } from 'react';
import { Link /* useNavigate */ } from 'react-router-dom';
import { Alert, Container, Row, Col, Spinner, Badge } from 'react-bootstrap';
// import API from '../services/api';
import { FaGoogle, FaArrowLeft } from 'react-icons/fa';
import { AuthContext } from '../App';
import '../styles/auth.css';

// Google OAuth credentials from environment variables
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '';

const LoginPage = () => {
  const { /* handleLogin */ } = useContext(AuthContext);
  // const navigate = useNavigate();
  const [error /* setError */] = useState('');
  const [googleLoading, setGoogleLoading] = useState(false);

  // Handle Google login
  const handleGoogleLogin = () => {
    setGoogleLoading(true);
    console.log('LoginPage: Initiating Google login');
    
    // Generate a random state parameter for security
    const state = Math.random().toString(36).substring(2, 15);
    localStorage.setItem('oauth_state', state);
    
    const websiteDomain = process.env.REACT_APP_WEBSITE_DOMAIN || 'http://localhost:3000';
    const redirectUri = encodeURIComponent(`${websiteDomain}/auth/callback/google`);
    
    // Redirect directly to Google's OAuth endpoint with all required parameters
    const redirectUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${redirectUri}&response_type=code&scope=email%20profile%20openid&state=${state}&access_type=offline&prompt=consent`;
    console.log('LoginPage: Redirecting to:', redirectUrl);
    
    // Redirect to Google OAuth
    window.location.href = redirectUrl;
  };

  return (
    <div className="auth-page">
      <div className="simple-header">
        <Link to="/" className="logo-link">S4</Link>
      </div>
    
      <Container>
        <Row className="justify-content-center">
          <Col xs={12} md={10} lg={8} xl={6}>
            <div className="login-card">
              <div className="text-center mb-4">
                <div className="mb-4 app-logo">S4</div>
                <h1 className="app-title">Intelligent Storage</h1>
                <p className="app-description">
                  Store and search content semantically with LLM-powered understanding
                </p>
              </div>

              {error && <Alert variant="danger">{error}</Alert>}
              
              <div className="login-options">
                <button
                  className="google-signin-button" 
                  onClick={handleGoogleLogin}
                  disabled={googleLoading}
                >
                  {googleLoading ? (
                    <Spinner animation="border" size="sm" />
                  ) : (
                    <>
                      <FaGoogle className="google-icon" />
                      <span>Continue with Google</span>
                    </>
                  )}
                </button>
              </div>

              <div className="onboarding-steps mt-5">
                <h6 className="text-center mb-3">Get started in minutes</h6>
                
                <div className="step-item">
                  <div className="step-icon">
                    <span>1</span>
                  </div>
                  <div className="step-content">
                    <h6>Sign in</h6>
                    <p className="text-muted small">Quick sign-in with your Google account</p>
                  </div>
                </div>
                
                <div className="step-item">
                  <div className="step-icon">
                    <span>2</span>
                  </div>
                  <div className="step-content">
                    <h6>Upload content <Badge bg="success" className="ms-2 fs-8">Any file type</Badge></h6>
                    <p className="text-muted small">Upload documents, audio, or video files</p>
                  </div>
                </div>
                
                <div className="step-item">
                  <div className="step-icon">
                    <span>3</span>
                  </div>
                  <div className="step-content">
                    <h6>Search semantically</h6>
                    <p className="text-muted small">Find content by meaning, not just keywords</p>
                  </div>
                </div>
              </div>

              <div className="login-info">
                <p className="text-center text-muted mt-4 small">
                  By continuing, you agree to S4's <a href="/terms">Terms of Service</a> and <a href="/privacy">Privacy Policy</a>
                </p>
              </div>
              
              <div className="text-center mt-4">
                <Link to="/" className="btn btn-link">
                  <FaArrowLeft className="me-2" /> Back to Home
                </Link>
              </div>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default LoginPage;        