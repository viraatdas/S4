import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Spinner, Alert, 
  Table, Badge, Form, Button
} from 'react-bootstrap';
import { 
  FaChartLine, FaServer, FaUsers, FaDatabase, 
  FaSearch, FaCalendarAlt, FaFileAlt, FaSyncAlt
} from 'react-icons/fa';
import AdminSidebar from '../components/AdminSidebar';
import API from '../services/api';
import { useNavigate } from 'react-router-dom';
import '../styles/admin.css';

// Mock data for demo - in production, this would come from the API
const generateMockData = () => {
  const now = new Date();
  const last30Days = Array.from({ length: 30 }, (_, i) => {
    const date = new Date();
    date.setDate(now.getDate() - (29 - i));
    return date.toISOString().split('T')[0];
  });
  
  // Generate random data for API calls and storage
  const apiCallsData = last30Days.map(date => ({
    date,
    count: Math.floor(Math.random() * 1000) + 100
  }));
  
  const storageData = last30Days.map((date, index) => ({
    date,
    size: (index * 10) + Math.floor(Math.random() * 50) + 100 // Increasing trend with randomness
  }));
  
  // Generate random data for searches and uploads
  const searchesData = last30Days.map(date => ({
    date,
    count: Math.floor(Math.random() * 500) + 50
  }));
  
  const uploadsData = last30Days.map(date => ({
    date,
    count: Math.floor(Math.random() * 100) + 10
  }));
  
  // Generate tenant stats
  const tenantStats = Array.from({ length: 5 }, (_, i) => ({
    id: `tenant-${i + 1}`,
    name: `Tenant ${i + 1}`,
    company: `Company ${i + 1}`,
    apiCalls: Math.floor(Math.random() * 5000) + 1000,
    storage: Math.floor(Math.random() * 10000) + 1000,
    documents: Math.floor(Math.random() * 500) + 50,
    searchQuality: Math.floor(Math.random() * 30) + 70
  }));
  
  return {
    apiCallsData,
    storageData,
    searchesData,
    uploadsData,
    tenantStats,
    summary: {
      totalApiCalls: apiCallsData.reduce((sum, item) => sum + item.count, 0),
      totalStorage: Math.round(storageData[storageData.length - 1].size),
      totalSearches: searchesData.reduce((sum, item) => sum + item.count, 0),
      totalUploads: uploadsData.reduce((sum, item) => sum + item.count, 0),
      totalTenants: tenantStats.length,
      totalDocuments: tenantStats.reduce((sum, tenant) => sum + tenant.documents, 0)
    }
  };
};

const AdminAnalyticsPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [timeRange, setTimeRange] = useState('30d');
  
  // Check if admin is logged in
  useEffect(() => {
    const adminKey = localStorage.getItem('adminKey');
    if (!adminKey) {
      navigate('/admin/login');
    }
  }, [navigate]);
  
  // Fetch analytics data
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        
        // In a real scenario, we would call the API with the time range
        // For demo purposes, we'll use mock data
        // const response = await API.getAdminAnalytics(timeRange);
        // setAnalyticsData(response.data);
        
        // Using mock data for demo
        setTimeout(() => {
          setAnalyticsData(generateMockData());
          setLoading(false);
        }, 1000);
        
      } catch (err) {
        console.error('Error fetching analytics:', err);
        
        if (err.response && err.response.status === 401) {
          localStorage.removeItem('adminKey');
          navigate('/admin/login');
        } else {
          setError('Failed to load analytics data. Please try again.');
          setLoading(false);
        }
      }
    };
    
    fetchAnalytics();
  }, [navigate, timeRange]);
  
  const handleLogout = () => {
    localStorage.removeItem('adminKey');
    navigate('/admin/login');
  };
  
  const handleRefresh = () => {
    setAnalyticsData(null);
    setLoading(true);
    
    // Simulate refresh
    setTimeout(() => {
      setAnalyticsData(generateMockData());
      setLoading(false);
    }, 1000);
  };
  
  const formatNumber = (num) => {
    return num.toLocaleString();
  };
  
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  return (
    <div className="d-flex">
      <AdminSidebar onLogout={handleLogout} />
      
      <div className="admin-content">
        <Container fluid>
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2>System Analytics</h2>
              <p className="text-muted">
                Overview of system performance and usage metrics
              </p>
            </div>
            
            <div className="d-flex">
              <Form.Select 
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="me-2"
                style={{ width: '150px' }}
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </Form.Select>
              
              <Button 
                variant="outline-primary"
                onClick={handleRefresh}
                disabled={loading}
              >
                <FaSyncAlt className="me-2" />
                Refresh
              </Button>
            </div>
          </div>
          
          {error && (
            <Alert variant="danger" dismissible onClose={() => setError('')}>
              {error}
            </Alert>
          )}
          
          {loading ? (
            <div className="admin-loading">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
              <p className="mt-3">Loading analytics data...</p>
            </div>
          ) : analyticsData ? (
            <>
              {/* Summary Cards */}
              <Row className="mb-4">
                <Col md={3}>
                  <Card className="admin-card stat-card primary">
                    <Card.Body className="d-flex align-items-center">
                      <div className="me-3 text-primary stat-icon">
                        <FaServer />
                      </div>
                      <div>
                        <h6 className="text-muted mb-1">Total API Calls</h6>
                        <h4>{formatNumber(analyticsData.summary.totalApiCalls)}</h4>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
                
                <Col md={3}>
                  <Card className="admin-card stat-card success">
                    <Card.Body className="d-flex align-items-center">
                      <div className="me-3 text-success stat-icon">
                        <FaUsers />
                      </div>
                      <div>
                        <h6 className="text-muted mb-1">Active Tenants</h6>
                        <h4>{analyticsData.summary.totalTenants}</h4>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
                
                <Col md={3}>
                  <Card className="admin-card stat-card warning">
                    <Card.Body className="d-flex align-items-center">
                      <div className="me-3 text-warning stat-icon">
                        <FaDatabase />
                      </div>
                      <div>
                        <h6 className="text-muted mb-1">Total Storage</h6>
                        <h4>{formatBytes(analyticsData.summary.totalStorage * 1024 * 1024)}</h4>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
                
                <Col md={3}>
                  <Card className="admin-card stat-card danger">
                    <Card.Body className="d-flex align-items-center">
                      <div className="me-3 text-danger stat-icon">
                        <FaFileAlt />
                      </div>
                      <div>
                        <h6 className="text-muted mb-1">Total Documents</h6>
                        <h4>{formatNumber(analyticsData.summary.totalDocuments)}</h4>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
              
              {/* Charts */}
              <Row className="mb-4">
                <Col md={6}>
                  <Card className="admin-card">
                    <Card.Header className="bg-transparent border-0">
                      <h5 className="mb-0">
                        <FaChartLine className="me-2" />
                        API Calls Over Time
                      </h5>
                    </Card.Header>
                    <Card.Body>
                      <div className="analytics-chart-container" style={{ height: '300px' }}>
                        <div className="text-center py-5">
                          <p className="text-muted">
                            Chart visualization would be rendered here using a library like Chart.js, Recharts, or D3.
                          </p>
                          <p>Sample Data:</p>
                          <code>
                            {JSON.stringify(analyticsData.apiCallsData.slice(0, 3))}... (and {analyticsData.apiCallsData.length - 3} more)
                          </code>
                        </div>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
                
                <Col md={6}>
                  <Card className="admin-card">
                    <Card.Header className="bg-transparent border-0">
                      <h5 className="mb-0">
                        <FaDatabase className="me-2" />
                        Storage Growth
                      </h5>
                    </Card.Header>
                    <Card.Body>
                      <div className="analytics-chart-container" style={{ height: '300px' }}>
                        <div className="text-center py-5">
                          <p className="text-muted">
                            Chart visualization would be rendered here using a library like Chart.js, Recharts, or D3.
                          </p>
                          <p>Sample Data:</p>
                          <code>
                            {JSON.stringify(analyticsData.storageData.slice(0, 3))}... (and {analyticsData.storageData.length - 3} more)
                          </code>
                        </div>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
              
              {/* Tenant Performance Table */}
              <Card className="admin-card mb-4">
                <Card.Header className="bg-transparent border-0">
                  <h5 className="mb-0">
                    <FaUsers className="me-2" />
                    Tenant Performance
                  </h5>
                </Card.Header>
                <Card.Body>
                  <div className="table-responsive">
                    <Table hover className="admin-table">
                      <thead>
                        <tr>
                          <th>Tenant</th>
                          <th>Company</th>
                          <th>API Calls</th>
                          <th>Storage Used</th>
                          <th>Documents</th>
                          <th>Search Quality</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analyticsData.tenantStats.map(tenant => (
                          <tr key={tenant.id}>
                            <td>{tenant.name}</td>
                            <td>{tenant.company}</td>
                            <td>{formatNumber(tenant.apiCalls)}</td>
                            <td>{formatBytes(tenant.storage * 1024)}</td>
                            <td>{formatNumber(tenant.documents)}</td>
                            <td>
                              <Badge 
                                bg={tenant.searchQuality > 90 ? 'success' : 
                                   tenant.searchQuality > 80 ? 'primary' :
                                   tenant.searchQuality > 70 ? 'warning' : 'danger'}
                              >
                                {tenant.searchQuality}%
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                </Card.Body>
              </Card>
              
              {/* Additional Charts */}
              <Row>
                <Col md={6}>
                  <Card className="admin-card">
                    <Card.Header className="bg-transparent border-0">
                      <h5 className="mb-0">
                        <FaSearch className="me-2" />
                        Search Performance
                      </h5>
                    </Card.Header>
                    <Card.Body>
                      <div className="analytics-chart-container" style={{ height: '250px' }}>
                        <div className="text-center py-5">
                          <p className="text-muted">
                            Chart visualization would be rendered here using a library like Chart.js, Recharts, or D3.
                          </p>
                          <p>Sample Data:</p>
                          <code>
                            {JSON.stringify(analyticsData.searchesData.slice(0, 3))}... (and {analyticsData.searchesData.length - 3} more)
                          </code>
                        </div>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
                
                <Col md={6}>
                  <Card className="admin-card">
                    <Card.Header className="bg-transparent border-0">
                      <h5 className="mb-0">
                        <FaFileAlt className="me-2" />
                        Document Uploads
                      </h5>
                    </Card.Header>
                    <Card.Body>
                      <div className="analytics-chart-container" style={{ height: '250px' }}>
                        <div className="text-center py-5">
                          <p className="text-muted">
                            Chart visualization would be rendered here using a library like Chart.js, Recharts, or D3.
                          </p>
                          <p>Sample Data:</p>
                          <code>
                            {JSON.stringify(analyticsData.uploadsData.slice(0, 3))}... (and {analyticsData.uploadsData.length - 3} more)
                          </code>
                        </div>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </>
          ) : (
            <Alert variant="info">
              No analytics data available for the selected time period.
            </Alert>
          )}
        </Container>
      </div>
    </div>
  );
};

export default AdminAnalyticsPage; 