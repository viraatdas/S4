import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Form, Button, 
  Spinner, Alert, InputGroup
} from 'react-bootstrap';
import { FaKey, FaLock, FaUserShield, FaServer, FaUserCog } from 'react-icons/fa';
import { Link, useNavigate } from 'react-router-dom';
import API from '../services/api';
import '../styles/auth.css';

const AdminLoginPage = () => {
  const navigate = useNavigate();
  const [adminKey, setAdminKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [keyVisible, setKeyVisible] = useState(false);
  
  // Check if already logged in
  useEffect(() => {
    const existingKey = localStorage.getItem('adminKey');
    if (existingKey) {
      navigate('/admin/dashboard');
    }
  }, [navigate]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!adminKey.trim()) {
      setError('Admin key is required');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      // Validate the admin key with the API
      await API.adminLogin(adminKey);
      
      // Store the admin key in localStorage
      localStorage.setItem('adminKey', adminKey);
      
      // Navigate to admin dashboard
      navigate('/admin/dashboard');
      
    } catch (err) {
      console.error('Admin login error:', err);
      
      if (err.response && err.response.status === 401) {
        setError('Invalid admin key. Please check and try again.');
      } else {
        setError('Failed to login. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Container fluid className="auth-container">
      <Row className="justify-content-center h-100">
        <Col lg={6} className="d-none d-lg-block auth-banner">
          <div className="banner-content">
            <h1>S4 Admin Portal</h1>
            <p>Manage your S4 instance, tenants, and analytics</p>
            <div className="feature-list">
              <div className="feature-item">
                <FaUserShield />
                <span>Secure tenant management</span>
              </div>
              <div className="feature-item">
                <FaServer />
                <span>Deployment monitoring</span>
              </div>
              <div className="feature-item">
                <FaUserCog />
                <span>Advanced analytics and reporting</span>
              </div>
            </div>
          </div>
        </Col>
        <Col lg={6} md={10} sm={12} className="auth-form-container">
          <div className="auth-form-wrapper">
            <div className="text-center mb-4">
              <img src="/logo.png" alt="S4 Logo" className="logo" />
              <h2 className="d-lg-none">S4 Admin Portal</h2>
            </div>
            
            {error && <Alert variant="danger">{error}</Alert>}
            
            <Card className="auth-card">
              <Card.Body>
                <h3 className="text-center mb-4">Admin Login</h3>
                
                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-4">
                    <div className="input-group">
                      <span className="input-group-text"><FaKey /></span>
                      <Form.Control
                        type={keyVisible ? "text" : "password"}
                        placeholder="Enter your admin key"
                        value={adminKey}
                        onChange={(e) => setAdminKey(e.target.value)}
                        disabled={loading}
                      />
                      <Button
                        variant="outline-secondary"
                        onClick={() => setKeyVisible(!keyVisible)}
                      >
                        <FaLock />
                      </Button>
                    </div>
                    <Form.Text className="text-muted mt-2">
                      This is the admin key specified during deployment or generated for you.
                    </Form.Text>
                  </Form.Group>
                  
                  <Button
                    variant="primary"
                    type="submit"
                    className="w-100 mb-3"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Logging in...
                      </>
                    ) : (
                      <>Admin Login</>
                    )}
                  </Button>
                </Form>
              </Card.Body>
            </Card>
            
            <div className="text-center mt-3">
              <p className="text-muted">
                <Link to="/" className="login-link">
                  Back to User Login
                </Link>
              </p>
            </div>
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default AdminLoginPage; 