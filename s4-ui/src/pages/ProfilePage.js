import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Container, Row, Col, Card, Button, Form, 
  Spinner, Alert, Badge, Tab, Tabs /* ListGroup */
} from 'react-bootstrap';
import { 
  FaUser, FaEnvelope, FaBuilding, FaEdit, 
  FaSave, FaKey, FaEye, FaEyeSlash, FaCloudDownloadAlt,
  FaArrowLeft, FaDatabase, FaFileAlt, FaSearch /* FaLock */
} from 'react-icons/fa';
import { AuthContext } from '../App';
import API from '../services/api';
import Navbar from '../components/Navbar';

const ProfilePage = () => {
  const { user, /* handleLogout */ } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [usageData, setUsageData] = useState(null);
  const [loadingUsage, setLoadingUsage] = useState(false);
  // const [apiKeyVisible, setApiKeyVisible] = useState(false);
  const [billingHistory, setBillingHistory] = useState([]);
  const [loadingBilling, setLoadingBilling] = useState(false);
  
  // Profile form state
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    company: '',
    jobTitle: '',
    phone: ''
  });
  
  const [apiKey /* setApiKey */] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  // const [isSaving, setIsSaving] = useState(false);
  
  // Initialize profile with user data
  useEffect(() => {
    if (user) {
      setProfile({
        name: user.name || '',
        email: user.email || '',
        company: user.company || '',
        jobTitle: user.job_title || '',
        phone: user.phone || ''
      });
    }
  }, [user]);
  
  // Fetch usage data
  useEffect(() => {
    const fetchUsageData = async () => {
      try {
        setLoadingUsage(true);
        const response = await API.getUsageStats();
        setUsageData(response.data);
      } catch (err) {
        console.error('Error fetching usage data:', err);
      } finally {
        setLoadingUsage(false);
      }
    };
    
    fetchUsageData();
  }, []);
  
  // Fetch billing history
  useEffect(() => {
    const fetchBillingHistory = async () => {
      try {
        setLoadingBilling(true);
        const response = await API.getBillingHistory();
        setBillingHistory(response.data);
      } catch (err) {
        console.error('Error fetching billing history:', err);
      } finally {
        setLoadingBilling(false);
      }
    };
    
    fetchBillingHistory();
  }, []);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfile(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      await API.updateUserProfile(profile);
      
      setSuccess('Profile updated successfully!');
      setEditMode(false);
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  
  // const getUsagePercentage = (used, limit) => {
  //   if (!used || !limit) return 0;
  //   return Math.min(Math.round((used / limit) * 100), 100);
  // };
  
  // const getUsageVariant = (percentage) => {
  //   if (percentage < 50) return 'success';
  //   if (percentage < 75) return 'warning';
  //   return 'danger';
  // };
  
  return (
    <>
      <Navbar />
      <Container className="py-4">
        <Button 
          variant="outline-secondary" 
          className="mb-4"
          onClick={() => navigate('/')}
        >
          <FaArrowLeft className="me-2" /> Back to Dashboard
        </Button>
        
        <h2 className="mb-4">Your Profile</h2>
        
        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}
        
        <Tabs defaultActiveKey="profile" className="mb-4">
          <Tab eventKey="profile" title="Profile Information">
            <Card className="mb-4">
              <Card.Header className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Personal Information</h5>
                {!editMode ? (
                  <Button 
                    variant="outline-primary" 
                    size="sm"
                    onClick={() => setEditMode(true)}
                  >
                    <FaEdit className="me-2" /> Edit
                  </Button>
                ) : (
                  <Button 
                    variant="outline-secondary" 
                    size="sm"
                    onClick={() => setEditMode(false)}
                  >
                    Cancel
                  </Button>
                )}
              </Card.Header>
              <Card.Body>
                <Form onSubmit={handleSubmit}>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Full Name</Form.Label>
                        <div className="input-group">
                          <span className="input-group-text">
                            <FaUser />
                          </span>
                          <Form.Control
                            type="text"
                            name="name"
                            value={profile.name}
                            onChange={handleInputChange}
                            disabled={!editMode || loading}
                            readOnly={!editMode}
                          />
                        </div>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Email Address</Form.Label>
                        <div className="input-group">
                          <span className="input-group-text">
                            <FaEnvelope />
                          </span>
                          <Form.Control
                            type="email"
                            name="email"
                            value={profile.email}
                            onChange={handleInputChange}
                            disabled={!editMode || loading}
                            readOnly={!editMode}
                          />
                        </div>
                      </Form.Group>
                    </Col>
                  </Row>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Company</Form.Label>
                        <div className="input-group">
                          <span className="input-group-text">
                            <FaBuilding />
                          </span>
                          <Form.Control
                            type="text"
                            name="company"
                            value={profile.company}
                            onChange={handleInputChange}
                            disabled={!editMode || loading}
                            readOnly={!editMode}
                          />
                        </div>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Job Title</Form.Label>
                        <Form.Control
                          type="text"
                          name="jobTitle"
                          value={profile.jobTitle}
                          onChange={handleInputChange}
                          disabled={!editMode || loading}
                          readOnly={!editMode}
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Phone Number</Form.Label>
                        <Form.Control
                          type="tel"
                          name="phone"
                          value={profile.phone}
                          onChange={handleInputChange}
                          disabled={!editMode || loading}
                          readOnly={!editMode}
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                  
                  {editMode && (
                    <div className="d-flex justify-content-end">
                      <Button 
                        type="submit" 
                        variant="primary"
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <Spinner animation="border" size="sm" className="me-2" /> 
                            Saving...
                          </>
                        ) : (
                          <>
                            <FaSave className="me-2" /> Save Changes
                          </>
                        )}
                      </Button>
                    </div>
                  )}
                </Form>
              </Card.Body>
            </Card>
            
            <Card>
              <Card.Header>
                <h5 className="mb-0">API Key</h5>
              </Card.Header>
              <Card.Body>
                <Row>
                  <Col md={8}>
                    <div className="input-group">
                      <span className="input-group-text">
                        <FaKey />
                      </span>
                      <Form.Control
                        type={showApiKey ? "text" : "password"}
                        value={apiKey}
                        readOnly
                      />
                      <Button 
                        variant="outline-secondary"
                        onClick={() => setShowApiKey(!showApiKey)}
                      >
                        {showApiKey ? <FaEyeSlash /> : <FaEye />}
                      </Button>
                    </div>
                    <Form.Text className="text-muted">
                      Your API key is used to authenticate requests to the S4 API. Keep it secure.
                    </Form.Text>
                  </Col>
                  <Col md={4} className="d-flex align-items-end mt-3 mt-md-0">
                    <Button variant="outline-secondary" className="w-100">
                      <FaCloudDownloadAlt className="me-2" /> Download API Key
                    </Button>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Tab>
          
          <Tab eventKey="usage" title="Usage Statistics">
            <Card>
              <Card.Header>
                <h5 className="mb-0">Service Usage</h5>
              </Card.Header>
              <Card.Body>
                {loadingUsage ? (
                  <div className="text-center py-5">
                    <Spinner animation="border" variant="primary" />
                    <p className="mt-3">Loading usage data...</p>
                  </div>
                ) : usageData ? (
                  <>
                    <Row className="mb-4">
                      <Col md={4} className="mb-3 mb-md-0">
                        <div className="p-3 bg-light rounded text-center">
                          <div className="mb-2">
                            <FaDatabase className="fs-3 text-primary" />
                          </div>
                          <h3>{usageData.storage_used_gb || '0'} GB</h3>
                          <p className="text-muted mb-0">Storage Used</p>
                          {usageData.storage_limit_gb && (
                            <div className="mt-2">
                              <div className="progress">
                                <div 
                                  className="progress-bar" 
                                  style={{ width: `${(usageData.storage_used_gb / usageData.storage_limit_gb) * 100}%` }}
                                  role="progressbar"
                                  aria-valuenow={usageData.storage_used_gb}
                                  aria-valuemin="0"
                                  aria-valuemax={usageData.storage_limit_gb}
                                ></div>
                              </div>
                              <small className="text-muted">
                                {usageData.storage_used_gb} of {usageData.storage_limit_gb} GB ({Math.round((usageData.storage_used_gb / usageData.storage_limit_gb) * 100)}%)
                              </small>
                            </div>
                          )}
                        </div>
                      </Col>
                      <Col md={4} className="mb-3 mb-md-0">
                        <div className="p-3 bg-light rounded text-center">
                          <div className="mb-2">
                            <FaFileAlt className="fs-3 text-success" />
                          </div>
                          <h3>{usageData.document_count || '0'}</h3>
                          <p className="text-muted mb-0">Total Documents</p>
                        </div>
                      </Col>
                      <Col md={4}>
                        <div className="p-3 bg-light rounded text-center">
                          <div className="mb-2">
                            <FaSearch className="fs-3 text-warning" />
                          </div>
                          <h3>{usageData.search_count_current_month || '0'}</h3>
                          <p className="text-muted mb-0">Searches This Month</p>
                        </div>
                      </Col>
                    </Row>
                    
                    <div className="mb-4">
                      <h6>Current Plan</h6>
                      <div className="d-flex align-items-center">
                        <div>
                          <Badge bg={
                            user?.subscription?.plan_name?.toLowerCase() === 'basic' ? 'info' :
                            user?.subscription?.plan_name?.toLowerCase() === 'standard' ? 'success' : 
                            user?.subscription?.plan_name?.toLowerCase() === 'premium' ? 'warning' : 
                            user?.subscription?.plan_name?.toLowerCase() === 'enterprise' ? 'danger' : 
                            'secondary'
                          } className="me-2 fs-6 py-2 px-3">
                            {user?.subscription?.plan_name || 'Free'}
                          </Badge>
                        </div>
                        <div className="ms-3">
                          <Button 
                            variant="outline-primary" 
                            size="sm"
                            onClick={() => navigate('/payment')}
                          >
                            Upgrade Plan
                          </Button>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h6>Plan Details</h6>
                      <ul className="list-unstyled">
                        <li className="mb-2">
                          <strong>Storage Limit:</strong> {usageData.storage_limit_gb} GB
                        </li>
                        <li className="mb-2">
                          <strong>Processing Limit:</strong> {usageData.processing_limit_tokens ? `${usageData.processing_limit_tokens.toLocaleString()} tokens/month` : 'Unlimited'}
                        </li>
                        <li className="mb-2">
                          <strong>API Rate Limit:</strong> {usageData.api_rate_limit ? `${usageData.api_rate_limit} requests/minute` : 'N/A'}
                        </li>
                        <li className="mb-2">
                          <strong>Next Billing Date:</strong> {formatDate(user?.subscription?.next_billing_date)}
                        </li>
                      </ul>
                    </div>
                  </>
                ) : (
                  <Alert variant="info">
                    No usage data available. This could be because you haven't used the service yet or there was an error fetching your usage statistics.
                  </Alert>
                )}
              </Card.Body>
            </Card>
          </Tab>
          
          <Tab eventKey="billing" title="Billing History">
            <Card>
              <Card.Header>
                <h5 className="mb-0">Billing Information</h5>
              </Card.Header>
              <Card.Body>
                {loadingBilling ? (
                  <div className="text-center py-5">
                    <Spinner animation="border" variant="primary" />
                    <p className="mt-3">Loading billing data...</p>
                  </div>
                ) : billingHistory && billingHistory.length > 0 ? (
                  <div className="table-responsive">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Description</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {billingHistory.map((item, index) => (
                          <tr key={index}>
                            <td>{formatDate(item.date)}</td>
                            <td>{item.description}</td>
                            <td>${item.amount.toFixed(2)}</td>
                            <td>
                              <Badge bg={
                                item.status === 'paid' ? 'success' :
                                item.status === 'pending' ? 'warning' :
                                item.status === 'failed' ? 'danger' :
                                'secondary'
                              }>
                                {item.status}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <Alert variant="info">
                    No billing history available. Your billing information will appear here once you make a payment.
                  </Alert>
                )}
                
                <div className="mt-4">
                  <Button 
                    variant="primary" 
                    onClick={() => navigate('/payment')}
                  >
                    Manage Subscription
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Tab>
        </Tabs>
      </Container>
    </>
  );
};

export default ProfilePage;        