import React from 'react';
import '../styles/AuthPage.css';

/**
 * Authentication page component with a custom Google authentication button
 */
const AuthPage = () => {
  const handleGoogleLogin = () => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    window.location.href = `${apiUrl}/auth/oauth/google`;
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>S4 - Smart S3 Storage Service</h1>
          <p>Sign in to access your smart storage</p>
        </div>
        
        <div className="auth-card">
          <div className="custom-auth-ui">
            <h2>Welcome to S4</h2>
            <p>Please sign in to continue</p>
            <button 
              className="google-button" 
              onClick={handleGoogleLogin}
            >
              <span className="google-icon">G</span>
              Sign in with Google
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
