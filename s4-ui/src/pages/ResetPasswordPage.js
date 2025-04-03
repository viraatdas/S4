import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { FaLock, FaCheck } from 'react-icons/fa';
import API from '../services/api';
import '../styles/auth.css';

const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [token, setToken] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Extract token from URL query params
  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const resetToken = queryParams.get('token');
    
    if (resetToken) {
      setToken(resetToken);
    } else {
      setError('Invalid or missing reset token. Please request a new password reset link.');
    }
  }, [location]);

  // Validation schema
  const validationSchema = Yup.object().shape({
    password: Yup.string()
      .required('Password is required')
      .min(8, 'Password must be at least 8 characters')
      .matches(/(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])/, 
        'Password must contain at least one uppercase letter, one lowercase letter, and one number'),
    confirmPassword: Yup.string()
      .oneOf([Yup.ref('password'), null], 'Passwords must match')
      .required('Please confirm your password')
  });

  // Handle form submission
  const handleSubmit = async (values, { setSubmitting }) => {
    if (!token) {
      setError('Reset token is missing');
      setSubmitting(false);
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      await API.resetPassword(token, values.password);
      setSuccess(true);
    } catch (err) {
      console.error('Password reset error:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to reset password. The token may be invalid or expired.'
      );
    } finally {
      setIsLoading(false);
      setSubmitting(false);
    }
  };

  return (
    <Container fluid className="auth-container">
      <Row className="justify-content-center h-100">
        <Col md={8} lg={6} xl={5} className="auth-form-container">
          <div className="auth-form-wrapper mx-auto">
            <div className="text-center mb-4">
              <img src="/logo.png" alt="S4 Logo" className="logo" />
              <h2>S4 Semantic Search</h2>
            </div>
            
            {error && <Alert variant="danger">{error}</Alert>}
            
            <Card className="auth-card">
              <Card.Body>
                <h3 className="text-center mb-4">Reset Your Password</h3>
                
                {success ? (
                  <div className="text-center">
                    <div className="success-icon mb-3">
                      <FaCheck size={40} className="text-success" />
                    </div>
                    <h5 className="mb-3">Password Reset Successful!</h5>
                    <p className="mb-4">Your password has been updated successfully.</p>
                    <Button 
                      variant="primary" 
                      className="w-100" 
                      as={Link} 
                      to="/login"
                    >
                      Back to Login
                    </Button>
                  </div>
                ) : (
                  <Formik
                    initialValues={{ password: '', confirmPassword: '' }}
                    validationSchema={validationSchema}
                    onSubmit={handleSubmit}
                  >
                    {({
                      values,
                      errors,
                      touched,
                      handleChange,
                      handleBlur,
                      handleSubmit,
                      isSubmitting,
                    }) => (
                      <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                          <Form.Label>New Password</Form.Label>
                          <div className="input-group">
                            <span className="input-group-text"><FaLock /></span>
                            <Form.Control
                              type="password"
                              name="password"
                              placeholder="Enter new password"
                              value={values.password}
                              onChange={handleChange}
                              onBlur={handleBlur}
                              isInvalid={touched.password && errors.password}
                            />
                          </div>
                          {touched.password && errors.password && (
                            <Form.Text className="text-danger">{errors.password}</Form.Text>
                          )}
                        </Form.Group>
                        
                        <Form.Group className="mb-4">
                          <Form.Label>Confirm Password</Form.Label>
                          <div className="input-group">
                            <span className="input-group-text"><FaLock /></span>
                            <Form.Control
                              type="password"
                              name="confirmPassword"
                              placeholder="Confirm new password"
                              value={values.confirmPassword}
                              onChange={handleChange}
                              onBlur={handleBlur}
                              isInvalid={touched.confirmPassword && errors.confirmPassword}
                            />
                          </div>
                          {touched.confirmPassword && errors.confirmPassword && (
                            <Form.Text className="text-danger">{errors.confirmPassword}</Form.Text>
                          )}
                        </Form.Group>
                        
                        <Button
                          variant="primary"
                          type="submit"
                          className="w-100 mb-3"
                          disabled={isSubmitting || isLoading || !token}
                        >
                          {isLoading ? (
                            <>
                              <Spinner animation="border" size="sm" className="me-2" />
                              Resetting Password...
                            </>
                          ) : (
                            <>Reset Password</>
                          )}
                        </Button>
                      </Form>
                    )}
                  </Formik>
                )}
              </Card.Body>
            </Card>
            
            <div className="text-center mt-3">
              <p>
                Remember your password?{' '}
                <Link to="/login" className="login-link">
                  Back to Login
                </Link>
              </p>
            </div>
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default ResetPasswordPage; 