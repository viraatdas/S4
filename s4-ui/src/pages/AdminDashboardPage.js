import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Container, Row, Col, Card, Button, Table, 
  Badge, Spinner, Alert, Modal, Form
} from 'react-bootstrap';
import { 
  FaUserPlus, /* FaPen, */ FaTrash, /* FaSignOutAlt, 
  FaUsersCog, FaExclamationTriangle, FaSyncAlt, */ FaEdit, FaKey, FaClipboard, FaSearch, FaFilter /* FaEllipsisV */
} from 'react-icons/fa';
// import * as Yup from 'yup';
// import API from '../services/api';
import AdminSidebar from '../components/AdminSidebar';
import '../styles/admin.css';

// Mock data for demo
const generateMockTenants = () => {
  return Array.from({ length: 15 }, (_, i) => ({
    id: `tenant-${i + 1}`,
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`,
    company: `Company ${i + 1}`,
    plan: ['Basic', 'Premium', 'Enterprise'][Math.floor(Math.random() * 3)],
    status: ['Active', 'Active', 'Active', 'Suspended', 'Pending'][Math.floor(Math.random() * 5)],
    created_at: new Date(Date.now() - Math.floor(Math.random() * 90) * 24 * 60 * 60 * 1000).toISOString(),
    documents: Math.floor(Math.random() * 100),
    storage_used: Math.floor(Math.random() * 1000) * 1024 * 1024,
    api_key: `key_${Math.random().toString(36).substring(2, 15)}`
  }));
};

const AdminDashboardPage = () => {
  const navigate = useNavigate();
  
  // State for tenant list
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  // const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  // State for tenant create/edit modal
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('create'); // 'create' or 'edit'
  const [currentTenant, setCurrentTenant] = useState(null);
  // const [formValues, setFormValues] = useState({
  //   name: '',
  //   email: '',
  //   company: '',
  //   plan_id: 'basic'
  // });
  const [formErrors, setFormErrors] = useState({});
  const [modalLoading, /* setModalLoading */] = useState(false);
  
  // State for delete confirmation
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  /* const [tenantToDelete, setTenantToDelete] = useState(null); */
  // const [deleteLoading, setDeleteLoading] = useState(false);
  
  // State for search and filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [planFilter, setPlanFilter] = useState('all');
  
  // State for add/edit modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTenant, setNewTenant] = useState({
    name: '',
    email: '',
    company: '',
    plan: 'Basic'
  });
  const [apiKeyVisible, setApiKeyVisible] = useState({});
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Validation schema for tenant form
  // const tenantSchema = Yup.object().shape({
  //   name: Yup.string().required('Name is required'),
  //   email: Yup.string().email('Invalid email').required('Email is required'),
  //   company: Yup.string(),
  //   plan_id: Yup.string().required('Plan is required')
  // });
  
  // Check if admin is logged in
  useEffect(() => {
    const adminKey = localStorage.getItem('adminKey');
    if (!adminKey) {
      navigate('/admin/login');
    }
  }, [navigate]);
  
  // Fetch tenants
  useEffect(() => {
    const fetchTenants = async () => {
      try {
        setLoading(true);
        
        // In a real scenario, we would call the API
        // const response = await API.getAdminTenants();
        // setTenants(response.data);
        
        // Using mock data for demo
        setTimeout(() => {
          setTenants(generateMockTenants());
          setLoading(false);
        }, 1000);
        
      } catch (err) {
        console.error('Error fetching tenants:', err);
        
        if (err.response && err.response.status === 401) {
          localStorage.removeItem('adminKey');
          navigate('/admin/login');
        } else {
          setError('Failed to load tenants. Please try again.');
          setLoading(false);
        }
      }
    };
    
    fetchTenants();
  }, [navigate]);
  
  // Initialize modal for creating a tenant
  // const handleCreateTenant = () => {
  //   setFormValues({
  //     name: '',
  //     email: '',
  //     company: '',
  //     plan_id: 'basic'
  //   });
  //   setFormErrors({});
  //   setModalMode('create');
  //   setShowModal(true);
  // };
  
  // Initialize modal for editing a tenant
  const handleEditTenant = (tenant) => {
    setCurrentTenant(tenant);
    // setFormValues({
    //   name: tenant.name,
    //   email: tenant.email,
    //   company: tenant.company || '',
    //   plan_id: tenant.plan.id
    // });
    setFormErrors({});
    setModalMode('edit');
    setShowModal(true);
  };
  
  // Handle form input change
  const handleInputChange = (e) => {
    // const { name, value } = e.target;
    // setFormValues(prev => ({
    //   ...prev,
    //   [name]: value
    // }));
  };
  
  // Submit tenant form (create or update)
  // const handleSubmitTenant = async (e) => {
  //   e.preventDefault();
  //   
  //   try {
  //     setModalLoading(true);
  //     
  //     // Validate form
  //     await tenantSchema.validate(formValues, { abortEarly: false });
  //     
  //     if (modalMode === 'create') {
  //       // Create new tenant
  //       await API.createTenant(formValues);
  //     } else {
  //       // Update existing tenant
  //       await API.updateTenant(currentTenant.id, formValues);
  //     }
  //     
  //     // Close modal and refresh list
  //     setShowModal(false);
  //     setRefreshTrigger(prev => prev + 1);
  //   } catch (err) {
  //     console.error('Tenant form error:', err);
  //     
  //     if (err.name === 'ValidationError') {
  //       // Yup validation error
  //       const errors = {};
  //       err.inner.forEach(e => {
  //         errors[e.path] = e.message;
  //       });
  //       setFormErrors(errors);
  //     } else if (err.response && err.response.data && err.response.data.detail) {
  //       setError(err.response.data.detail);
  //     } else {
  //       setError('Failed to save tenant. Please try again.');
  //     }
  //   } finally {
  //     setModalLoading(false);
  //   }
  // };
  
  // Initialize delete confirmation
  const handleDeleteConfirmation = (tenant) => {
    // setTenantToDelete(tenant);
    setShowDeleteModal(true);
  };
  
  // Delete tenant
  // const handleDeleteTenant = async () => {
  //   if (!tenantToDelete) return;
  //   
  //   try {
  //     setDeleteLoading(true);
  //     await API.deleteTenant(tenantToDelete.id);
  //     
  //     // Close modal and refresh list
  //     setShowDeleteModal(false);
  //     setTenantToDelete(null);
  //     setRefreshTrigger(prev => prev + 1);
  //   } catch (err) {
  //     console.error('Error deleting tenant:', err);
  //     setError('Failed to delete tenant. Please try again.');
  //   } finally {
  //     setDeleteLoading(false);
  //   }
  // };
  
  // Handle admin logout
  const handleLogout = () => {
    localStorage.removeItem('adminKey');
    navigate('/admin/login');
  };
  
  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  
  // Get badge color for plan type
  const getPlanBadgeColor = (planId) => {
    switch (planId) {
      case 'basic':
        return 'primary';
      case 'premium':
        return 'success';
      case 'enterprise':
        return 'warning';
      default:
        return 'secondary';
    }
  };
  
  // Filter and search tenants
  const filteredTenants = tenants.filter(tenant => {
    const matchesSearch = searchTerm === '' || 
      tenant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tenant.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tenant.company.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || 
      tenant.status.toLowerCase() === statusFilter.toLowerCase();
    
    const matchesPlan = planFilter === 'all' || 
      tenant.plan.toLowerCase() === planFilter.toLowerCase();
    
    return matchesSearch && matchesStatus && matchesPlan;
  });
  
  const handleAddTenant = () => {
    setNewTenant({
      name: '',
      email: '',
      company: '',
      plan: 'Basic'
    });
    setFormErrors({});
    setShowAddModal(true);
  };
  
  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentTenant(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmitNewTenant = async (e) => {
    e.preventDefault();
    
    const errors = validateTenantForm(newTenant);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    try {
      setFormSubmitting(true);
      
      // In a real scenario, we would call the API
      // const response = await API.createTenant(newTenant);
      // const createdTenant = response.data;
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Create a mock tenant with a unique ID
      const createdTenant = {
        ...newTenant,
        id: `tenant-${tenants.length + 1}`,
        status: 'Active',
        created_at: new Date().toISOString(),
        documents: 0,
        storage_used: 0,
        api_key: `key_${Math.random().toString(36).substring(2, 15)}`
      };
      
      setTenants(prev => [createdTenant, ...prev]);
      setShowAddModal(false);
      setSuccessMessage(`Tenant ${createdTenant.name} created successfully!`);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error creating tenant:', err);
      setError('Failed to create tenant. Please try again.');
    } finally {
      setFormSubmitting(false);
    }
  };
  
  const handleSubmitEditTenant = async (e) => {
    e.preventDefault();
    
    const errors = validateTenantForm(currentTenant);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    try {
      setFormSubmitting(true);
      
      // In a real scenario, we would call the API
      // const response = await API.updateTenant(currentTenant.id, currentTenant);
      // const updatedTenant = response.data;
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setTenants(prev => 
        prev.map(tenant => 
          tenant.id === currentTenant.id ? currentTenant : tenant
        )
      );
      setShowModal(false);
      setSuccessMessage(`Tenant ${currentTenant.name} updated successfully!`);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error updating tenant:', err);
      setError('Failed to update tenant. Please try again.');
    } finally {
      setFormSubmitting(false);
    }
  };
  
  const handleConfirmDelete = async () => {
    try {
      setFormSubmitting(true);
      
      // In a real scenario, we would call the API
      // await API.deleteTenant(currentTenant.id);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setTenants(prev => prev.filter(tenant => tenant.id !== currentTenant.id));
      setShowDeleteModal(false);
      setSuccessMessage(`Tenant ${currentTenant.name} deleted successfully!`);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error deleting tenant:', err);
      setError('Failed to delete tenant. Please try again.');
    } finally {
      setFormSubmitting(false);
    }
  };
  
  const validateTenantForm = (data) => {
    const errors = {};
    
    if (!data.name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (!data.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.email = 'Email is invalid';
    }
    
    if (!data.company.trim()) {
      errors.company = 'Company is required';
    }
    
    if (!data.plan) {
      errors.plan = 'Plan is required';
    }
    
    return errors;
  };
  
  const toggleApiKeyVisibility = (tenantId) => {
    setApiKeyVisible(prev => ({
      ...prev,
      [tenantId]: !prev[tenantId]
    }));
  };
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccessMessage('API key copied to clipboard!');
    setTimeout(() => setSuccessMessage(''), 3000);
  };
  
  return (
    <div className="d-flex">
      <AdminSidebar onLogout={handleLogout} />
      
      <div className="admin-content">
        <Container fluid>
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2>Tenant Management</h2>
              <p className="text-muted">
                Manage and monitor your S4 tenants
              </p>
            </div>
            
            <Button 
              variant="primary"
              onClick={handleAddTenant}
            >
              <FaUserPlus className="me-2" />
              Add Tenant
            </Button>
          </div>
          
          {successMessage && (
            <Alert 
              variant="success" 
              dismissible 
              onClose={() => setSuccessMessage('')}
              className="mb-4"
            >
              {successMessage}
            </Alert>
          )}
          
          {error && (
            <Alert 
              variant="danger" 
              dismissible 
              onClose={() => setError('')}
              className="mb-4"
            >
              {error}
            </Alert>
          )}
          
          {/* Filters and Search */}
          <Card className="mb-4 admin-card">
            <Card.Body>
              <Row>
                <Col md={4}>
                  <Form.Group className="mb-md-0 mb-3">
                    <div className="input-group">
                      <span className="input-group-text">
                        <FaSearch />
                      </span>
                      <Form.Control
                        type="text"
                        placeholder="Search tenants..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                  </Form.Group>
                </Col>
                
                <Col md={3}>
                  <Form.Group className="mb-md-0 mb-3">
                    <div className="input-group">
                      <span className="input-group-text">
                        <FaFilter />
                      </span>
                      <Form.Select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                      >
                        <option value="all">All Statuses</option>
                        <option value="active">Active</option>
                        <option value="suspended">Suspended</option>
                        <option value="pending">Pending</option>
                      </Form.Select>
                    </div>
                  </Form.Group>
                </Col>
                
                <Col md={3}>
                  <Form.Group className="mb-md-0 mb-3">
                    <div className="input-group">
                      <span className="input-group-text">
                        <FaFilter />
                      </span>
                      <Form.Select
                        value={planFilter}
                        onChange={(e) => setPlanFilter(e.target.value)}
                      >
                        <option value="all">All Plans</option>
                        <option value="basic">Basic</option>
                        <option value="premium">Premium</option>
                        <option value="enterprise">Enterprise</option>
                      </Form.Select>
                    </div>
                  </Form.Group>
                </Col>
                
                <Col md={2} className="d-flex align-items-center justify-content-md-end">
                  <span className="text-muted">
                    {filteredTenants.length} tenant{filteredTenants.length !== 1 ? 's' : ''}
                  </span>
                </Col>
              </Row>
            </Card.Body>
          </Card>
          
          {/* Tenants Table */}
          <Card className="admin-card">
            <Card.Body className="p-0">
              {loading ? (
                <div className="admin-loading">
                  <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </Spinner>
                  <p className="mt-3">Loading tenants...</p>
                </div>
              ) : filteredTenants.length > 0 ? (
                <div className="table-responsive">
                  <Table hover className="admin-table mb-0">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Company</th>
                        <th>Plan</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>API Key</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredTenants.map(tenant => (
                        <tr key={tenant.id}>
                          <td>{tenant.name}</td>
                          <td>{tenant.email}</td>
                          <td>{tenant.company}</td>
                          <td>
                            <Badge 
                              bg={getPlanBadgeColor(tenant.plan)} 
                              className="tenant-badge"
                            >
                              {tenant.plan}
                            </Badge>
                          </td>
                          <td>
                            <Badge 
                              bg={tenant.status.toLowerCase() === 'active' ? 'success' : tenant.status.toLowerCase() === 'suspended' ? 'danger' : 'warning'} 
                              className="tenant-badge"
                            >
                              {tenant.status}
                            </Badge>
                          </td>
                          <td>{formatDate(tenant.created_at)}</td>
                          <td>
                            <div className="d-flex align-items-center">
                              <code className="me-2">
                                {apiKeyVisible[tenant.id] 
                                  ? tenant.api_key 
                                  : `${tenant.api_key.substring(0, 5)}...`}
                              </code>
                              <Button 
                                variant="link" 
                                className="p-0 me-1" 
                                onClick={() => toggleApiKeyVisibility(tenant.id)}
                                title={apiKeyVisible[tenant.id] ? "Hide API Key" : "Show API Key"}
                              >
                                <FaKey />
                              </Button>
                              {apiKeyVisible[tenant.id] && (
                                <Button 
                                  variant="link" 
                                  className="p-0" 
                                  onClick={() => copyToClipboard(tenant.api_key)}
                                  title="Copy API Key"
                                >
                                  <FaClipboard />
                                </Button>
                              )}
                            </div>
                          </td>
                          <td>
                            <div className="d-flex gap-2">
                              <Button 
                                variant="outline-primary" 
                                size="sm" 
                                className="btn-icon"
                                onClick={() => handleEditTenant(tenant)}
                                title="Edit Tenant"
                              >
                                <FaEdit />
                              </Button>
                              <Button 
                                variant="outline-danger" 
                                size="sm" 
                                className="btn-icon"
                                onClick={() => handleDeleteConfirmation(tenant)}
                                title="Delete Tenant"
                              >
                                <FaTrash />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              ) : (
                <div className="p-4 text-center">
                  <p className="mb-0">No tenants found matching your criteria.</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Container>
      </div>
      
      {/* Add Tenant Modal */}
      <Modal 
        show={showAddModal} 
        onHide={() => setShowAddModal(false)}
        centered
        backdrop="static"
        className="admin-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>Add New Tenant</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmitNewTenant}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={newTenant.name}
                onChange={handleInputChange}
                isInvalid={!!formErrors.name}
              />
              <Form.Control.Feedback type="invalid">
                {formErrors.name}
              </Form.Control.Feedback>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                name="email"
                value={newTenant.email}
                onChange={handleInputChange}
                isInvalid={!!formErrors.email}
              />
              <Form.Control.Feedback type="invalid">
                {formErrors.email}
              </Form.Control.Feedback>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Company</Form.Label>
              <Form.Control
                type="text"
                name="company"
                value={newTenant.company}
                onChange={handleInputChange}
                isInvalid={!!formErrors.company}
              />
              <Form.Control.Feedback type="invalid">
                {formErrors.company}
              </Form.Control.Feedback>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Subscription Plan</Form.Label>
              <Form.Select
                name="plan"
                value={newTenant.plan}
                onChange={handleInputChange}
                isInvalid={!!formErrors.plan}
              >
                <option value="Basic">Basic</option>
                <option value="Premium">Premium</option>
                <option value="Enterprise">Enterprise</option>
              </Form.Select>
              <Form.Control.Feedback type="invalid">
                {formErrors.plan}
              </Form.Control.Feedback>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button 
              variant="secondary" 
              onClick={() => setShowAddModal(false)}
              disabled={formSubmitting}
            >
              Cancel
            </Button>
            <Button 
              variant="primary" 
              type="submit"
              disabled={formSubmitting}
            >
              {formSubmitting ? (
                <>
                  <Spinner
                    as="span"
                    animation="border"
                    size="sm"
                    role="status"
                    aria-hidden="true"
                    className="me-2"
                  />
                  Creating...
                </>
              ) : 'Create Tenant'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
      
      {/* Edit Tenant Modal */}
      <Modal 
        show={showModal} 
        onHide={() => setShowModal(false)}
        centered
        backdrop="static"
        className="admin-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>
            {modalMode === 'create' ? 'Add New Tenant' : 'Edit Tenant'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={modalMode === 'create' ? handleSubmitNewTenant : handleSubmitEditTenant}>
            {modalMode === 'create' ? (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={newTenant.name}
                    onChange={handleInputChange}
                    isInvalid={!!formErrors.name}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.name}
                  </Form.Control.Feedback>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={newTenant.email}
                    onChange={handleInputChange}
                    isInvalid={!!formErrors.email}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.email}
                  </Form.Control.Feedback>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Company</Form.Label>
                  <Form.Control
                    type="text"
                    name="company"
                    value={newTenant.company}
                    onChange={handleInputChange}
                    isInvalid={!!formErrors.company}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.company}
                  </Form.Control.Feedback>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Subscription Plan</Form.Label>
                  <Form.Select
                    name="plan"
                    value={newTenant.plan}
                    onChange={handleInputChange}
                    isInvalid={!!formErrors.plan}
                  >
                    <option value="Basic">Basic</option>
                    <option value="Premium">Premium</option>
                    <option value="Enterprise">Enterprise</option>
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">
                    {formErrors.plan}
                  </Form.Control.Feedback>
                </Form.Group>
              </>
            ) :
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={currentTenant.name}
                    onChange={handleEditInputChange}
                    isInvalid={!!formErrors.name}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.name}
                  </Form.Control.Feedback>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={currentTenant.email}
                    onChange={handleEditInputChange}
                    isInvalid={!!formErrors.email}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.email}
                  </Form.Control.Feedback>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Company</Form.Label>
                  <Form.Control
                    type="text"
                    name="company"
                    value={currentTenant.company}
                    onChange={handleEditInputChange}
                    isInvalid={!!formErrors.company}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.company}
                  </Form.Control.Feedback>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Subscription Plan</Form.Label>
                  <Form.Select
                    name="plan_id"
                    value={currentTenant.plan}
                    onChange={handleEditInputChange}
                    isInvalid={!!formErrors.plan_id}
                  >
                    <option value="basic">Basic</option>
                    <option value="premium">Premium</option>
                    <option value="enterprise">Enterprise</option>
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">
                    {formErrors.plan_id}
                  </Form.Control.Feedback>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Status</Form.Label>
                  <Form.Select
                    name="status"
                    value={currentTenant.status}
                    onChange={handleEditInputChange}
                  >
                    <option value="Active">Active</option>
                    <option value="Suspended">Suspended</option>
                    <option value="Pending">Pending</option>
                  </Form.Select>
                </Form.Group>
              </>
            }
            <Modal.Footer>
              <Button 
                variant="secondary" 
                onClick={() => setShowModal(false)}
                disabled={modalLoading}
              >
                Cancel
              </Button>
              <Button 
                variant="primary" 
                type="submit"
                disabled={modalLoading}
              >
                {modalLoading ? (
                  <>
                    <Spinner
                      as="span"
                      animation="border"
                      size="sm"
                      role="status"
                      aria-hidden="true"
                      className="me-2"
                    />
                    {modalMode === 'create' ? 'Creating...' : 'Updating...'}
                  </>
                ) : (modalMode === 'create' ? 'Create Tenant' : 'Update Tenant')}
              </Button>
            </Modal.Footer>
          </Form>
        </Modal.Body>
      </Modal>
      
      {/* Delete Tenant Modal */}
      <Modal 
        show={showDeleteModal} 
        onHide={() => setShowDeleteModal(false)}
        centered
        backdrop="static"
        className="admin-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>Delete Tenant</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {currentTenant && (
            <>
              <p>Are you sure you want to delete the tenant <strong>{currentTenant.name}</strong>?</p>
              <Alert variant="danger">
                This action cannot be undone. All tenant data will be permanently deleted.
              </Alert>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowDeleteModal(false)}
            disabled={formSubmitting}
          >
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={handleConfirmDelete}
            disabled={formSubmitting}
          >
            {formSubmitting ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Deleting...
              </>
            ) : 'Delete Tenant'}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default AdminDashboardPage;                                  