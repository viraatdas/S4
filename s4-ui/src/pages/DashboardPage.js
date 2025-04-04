import React, { useState, useEffect, useContext } from 'react';
import { Container, Row, Col, Card, Button, Form, /* InputGroup, */ Table, Spinner, Alert, Modal, Badge } from 'react-bootstrap';
// import { useNavigate } from 'react-router-dom';
import '../styles/delete-animation.css';
import {
  FaSearch, /* FaUpload, */ FaTrash, FaFile, FaFolder, 
  /* FaChartLine, */ FaDatabase, FaCloudUploadAlt, FaFilePdf,
  FaFileWord, FaFileAlt, FaVideo, FaMusic, FaFileCode,
  FaClock, /* FaInfoCircle, */ FaExclamationTriangle, FaDownload
  /* FaEye */
} from 'react-icons/fa';
import API from '../services/api';
import Navbar from '../components/Navbar';
import { AuthContext } from '../App';
import OnboardingWizard from '../components/OnboardingWizard';
import FeatureTour from '../components/FeatureTour';

const DashboardPage = () => {
  const { user } = useContext(AuthContext);
  // const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [stats, setStats] = useState({
    totalDocuments: 0,
    totalTokens: 0,
    searchQueries: 0
  });
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState(null);
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [deleteSuccess, setDeleteSuccess] = useState(false);
  
  // Onboarding and tour states
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showTour, setShowTour] = useState(false);

  useEffect(() => {
    fetchDocuments();
    
    // Check if this is the user's first time
    const hasCompletedOnboarding = localStorage.getItem('hasCompletedOnboarding');
    if (!hasCompletedOnboarding) {
      setShowOnboarding(true);
    }
    
    // Verify authentication status
    const token = localStorage.getItem('token');
    const userEmail = localStorage.getItem('userEmail');
    console.log('Authentication Token:', token);
    console.log('User Email:', userEmail);
    
    // Log authentication data to console for verification
    if (token) {
      console.log('User is authenticated with token:', token.substring(0, 10) + '...');
    } else {
      console.error('No authentication token found in localStorage');
    }
  }, []);

  // Feature tour steps
  const tourSteps = [
    {
      selector: '.dashboard-welcome',
      title: 'Welcome to Your Dashboard',
      content: 'This is your personal dashboard where you can manage documents and access all S4 features.'
    },
    {
      selector: '.search-form-modern',
      title: 'Semantic Search',
      content: 'Search your content by meaning, not just keywords. Try asking questions or describing what you\'re looking for.'
    },
    {
      selector: '.dashboard-card:first-child',
      title: 'Document Stats',
      content: 'Track your storage usage and document statistics at a glance.'
    },
    {
      selector: '.rounded-pill.px-3',
      title: 'Upload Documents',
      content: 'Add new documents to your storage for semantic indexing. We support text, PDFs, audio, video and more.'
    }
  ];

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
    localStorage.setItem('hasCompletedOnboarding', 'true');
    setShowTour(true);
  };

  const handleTourComplete = () => {
    setShowTour(false);
    localStorage.setItem('hasCompletedTour', 'true');
  };
  
  const handleUploadFromOnboarding = async (file) => {
    // Create FormData object
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await API.uploadDocument(formData);
      
      // Refetch documents to include the newly uploaded one
      fetchDocuments();
      
      return response;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw new Error(error.response?.data?.message || 'Failed to upload document');
    }
  };

  const fetchDocuments = async () => {
    // Clear documents first to ensure we don't show stale data
    setDocuments([]);
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Fetching documents...');
      const response = await API.getDocuments();
      console.log('Documents received:', response.data);
      setDocuments(response.data || []);
      
      // Update stats
      setStats({
        totalDocuments: response.data ? response.data.length : 0,
        totalTokens: response.data ? response.data.reduce((sum, doc) => sum + (doc.tokens || 0), 0) : 0,
        searchQueries: localStorage.getItem('searchCount') || 0
      });
      
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to fetch documents. Please try again later.');
      // Ensure documents is empty on error
      setDocuments([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchTerm.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await API.searchDocuments(searchTerm);
      setSearchResults(response.data.results || []);
      
      // Increment search count in localStorage
      const currentCount = parseInt(localStorage.getItem('searchCount') || '0');
      localStorage.setItem('searchCount', currentCount + 1);
      
      // Update stats
      setStats(prev => ({
        ...prev,
        searchQueries: currentCount + 1
      }));
      
    } catch (err) {
      console.error('Error searching documents:', err);
      setError('Search failed. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadError('Please select a file to upload');
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(false);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await API.uploadDocument(formData);
      setUploadSuccess(true);
      setFile(null);
      
      // Refresh document list
      fetchDocuments();
      
      // Close modal after a delay
      setTimeout(() => {
        setShowUploadModal(false);
        setUploadSuccess(false);
      }, 2000);
      
    } catch (err) {
      console.error('Error uploading document:', err);
      setUploadError('Failed to upload document. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle initiating document deletion (shows confirmation modal)
  const handleDeleteDocumentClick = (document) => {
    setDocumentToDelete(document);
    setShowDeleteModal(true);
    setDeleteSuccess(false);
  };

  // Handle actual document deletion after confirmation
  const handleDeleteDocument = async () => {
    if (!documentToDelete) return;
    
    try {
      setIsDeleting(true);
      setError(null);
      
      // Call API to delete document
      await API.deleteDocument(documentToDelete.id);
      
      // Refresh document list
      fetchDocuments();
      
      setDeleteSuccess(true);
      
      // Close modal after a short delay to show success message
      setTimeout(() => {
        setShowDeleteModal(false);
        setDocumentToDelete(null);
      }, 1500);
    } catch (error) {
      console.error('Error deleting document:', error);
      setError('Failed to delete document. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };
  
  // Handle document download
  const handleDownloadDocument = async (doc) => {
    try {
      // Extract user ID, document ID, and filename from the download URL
      const urlParts = (doc.download_url || doc.url).split('/');
      const filename = urlParts[urlParts.length - 1];
      const docId = urlParts[urlParts.length - 2];
      const userId = urlParts[urlParts.length - 3];
      
      // Use the API service to handle the download
      await API.downloadDocument(userId, docId, filename);
    } catch (error) {
      console.error('Error downloading document:', error);
      setError('Failed to download document. Please try again.');
    }
  };

  // Helper function to get icon by file type
  const getFileIcon = (filename) => {
    if (!filename) return <FaFile />;
    
    const extension = filename.split('.').pop().toLowerCase();
    
    switch (extension) {
      case 'pdf':
        return <FaFilePdf className="text-danger" />;
      case 'docx':
      case 'doc':
        return <FaFileWord className="text-primary" />;
      case 'txt':
      case 'md':
        return <FaFileAlt className="text-secondary" />;
      case 'mp4':
      case 'mov':
      case 'avi':
      case 'webm':
        return <FaVideo className="text-success" />;
      case 'mp3':
      case 'wav':
        return <FaMusic className="text-info" />;
      case 'json':
      case 'xml':
      case 'html':
        return <FaFileCode className="text-warning" />;
      default:
        return <FaFile />;
    }
  };

  // Helper to get content type label
  const getContentTypeLabel = (filename) => {
    if (!filename) return 'Unknown';
    
    const extension = filename.split('.').pop().toLowerCase();
    
    if (['pdf', 'docx', 'doc', 'txt', 'md'].includes(extension)) {
      return 'Document';
    } else if (['mp4', 'mov', 'avi', 'webm'].includes(extension)) {
      return 'Video';
    } else if (['mp3', 'wav'].includes(extension)) {
      return 'Audio';
    } else if (['json', 'xml', 'html'].includes(extension)) {
      return 'Code';
    }
    
    return 'Other';
  };

  // Helper to format tokens count
  const formatTokens = (tokens) => {
    if (!tokens && tokens !== 0) return 'N/A';
    
    if (tokens < 1000) {
      return tokens;
    } else if (tokens < 1000000) {
      return `${(tokens / 1000).toFixed(1)}K`;
    } else {
      return `${(tokens / 1000000).toFixed(1)}M`;
    }
  };

  // Helper to format dates
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <>
      <Navbar />
      
      {/* Authentication Status Indicator */}
      {localStorage.getItem('token') && (
        <div style={{
          position: 'fixed',
          top: '70px',
          right: '20px',
          padding: '10px 15px',
          background: '#4CAF50',
          color: 'white',
          borderRadius: '5px',
          zIndex: '9999',
          boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ fontSize: '16px' }}>✓</span>
          <span>Authenticated as: {localStorage.getItem('email') || user?.email || 'User'}</span>
        </div>
      )}
      
      <Container className="py-4">
        {/* Welcome Section */}
        <div className="dashboard-welcome fade-in-up">
          <h1>Welcome, {user?.name || 'User'}!</h1>
          <p>Manage your documents and access powerful semantic search capabilities.</p>
        </div>
        
        {/* Stats Cards */}
        <Row className="mb-4 fade-in-up" style={{animationDelay: '0.1s'}}>
          <Col lg={4} md={6} className="mb-3">
            <Card className="dashboard-card h-100">
              <Card.Body className="d-flex flex-column align-items-center text-center p-4">
                <div className="dashboard-card-icon mb-3">
                  <FaDatabase />
                </div>
                <h3 className="h2 mb-1">{stats.totalDocuments}</h3>
                <p className="text-muted mb-0">Documents</p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col lg={4} md={6} className="mb-3">
            <Card className="dashboard-card h-100">
              <Card.Body className="d-flex flex-column align-items-center text-center p-4">
                <div className="dashboard-card-icon mb-3">
                  <FaFileAlt />
                </div>
                <h3 className="h2 mb-1">{formatTokens(stats.totalTokens)}</h3>
                <p className="text-muted mb-0">Total Tokens</p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col lg={4} md={12} className="mb-3">
            <Card className="dashboard-card h-100">
              <Card.Body className="d-flex flex-column align-items-center text-center p-4">
                <div className="dashboard-card-icon mb-3">
                  <FaSearch />
                </div>
                <h3 className="h2 mb-1">{stats.searchQueries}</h3>
                <p className="text-muted mb-0">Search Queries</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
        
        {/* Quick Search */}
        <Card className="mb-4 fade-in-up" style={{animationDelay: '0.2s'}}>
          <Card.Body className="p-4">
            <h4 className="mb-3">Quick Search</h4>
            <Form onSubmit={handleSearch} className="search-form-modern">
              <span className="search-icon">
                <FaSearch />
              </span>
              <Form.Control
                type="text"
                placeholder="Search for content across your documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <Button 
                type="submit" 
                variant="primary"
                disabled={isLoading || !searchTerm.trim()}
              >
                {isLoading ? <Spinner size="sm" animation="border" /> : 'Search'}
              </Button>
            </Form>
            
            {searchResults.length > 0 && (
              <div className="mt-4 scale-in">
                <h5 className="mb-3">Search Results</h5>
                <Table responsive hover className="search-results-table">
                  <thead>
                    <tr>
                      <th>Document</th>
                      <th>Score</th>
                      <th>Content</th>
                    </tr>
                  </thead>
                  <tbody>
                    {searchResults.map((result, index) => (
                      <tr key={index}>
                        <td className="text-nowrap">
                          {getFileIcon(result.document_name)} {result.document_name}
                        </td>
                        <td>
                          <Badge bg="primary">{(result.score * 100).toFixed(0)}%</Badge>
                        </td>
                        <td>
                          <div className="text-truncate" style={{maxWidth: '400px'}}>
                            {result.content}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            )}
          </Card.Body>
        </Card>
        
        {/* Documents Section */}
        <Card className="mb-4 fade-in-up" style={{animationDelay: '0.3s'}}>
          <Card.Header className="d-flex justify-content-between align-items-center bg-white p-4">
            <h4 className="mb-0">Your Documents</h4>
            <Button 
              variant="primary" 
              size="sm" 
              onClick={() => setShowUploadModal(true)}
              className="rounded-pill px-3"
            >
              <FaCloudUploadAlt className="me-2" /> Upload Document
            </Button>
          </Card.Header>
          
          <Card.Body className="p-0">
            {error && (
              <Alert variant="danger" className="m-4">
                <FaExclamationTriangle className="me-2" /> {error}
              </Alert>
            )}
            
            {isLoading ? (
              <div className="text-center p-5">
                <Spinner animation="border" variant="primary" />
                <p className="mt-3 text-muted">Loading your documents...</p>
              </div>
            ) : documents.length === 0 ? (
              <div className="empty-state m-4">
                <div className="empty-state-icon">
                  <FaFolder />
                </div>
                <h3>No Documents Yet</h3>
                <p>
                  Start by uploading documents to enable powerful semantic search capabilities.
                  We support various file formats including PDF, Word, and text files.
                </p>
                <Button
                  variant="primary"
                  onClick={() => setShowUploadModal(true)}
                  className="rounded-pill px-4"
                >
                  <FaCloudUploadAlt className="me-2" /> Upload Your First Document
                </Button>
              </div>
            ) : (
              <div className="table-responsive">
                <Table hover className="mb-0">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Type</th>
                      <th>Size</th>
                      <th>Tokens</th>
                      <th>Uploaded</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc.id} className="align-middle">
                        <td className="text-nowrap">
                          {getFileIcon(doc.name)} {doc.name}
                        </td>
                        <td>
                          <Badge bg="light" text="dark">
                            {getContentTypeLabel(doc.name)}
                          </Badge>
                        </td>
                        <td>{(doc.size / 1024).toFixed(1)} KB</td>
                        <td>{formatTokens(doc.tokens)}</td>
                        <td>
                          <div className="d-flex align-items-center">
                            <FaClock className="text-muted me-2" size={14} />
                            <span>{formatDate(doc.created_at)}</span>
                          </div>
                        </td>
                        <td>
                          <div className="d-flex gap-2">
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={() => handleDownloadDocument(doc)}
                              className="rounded-pill btn-icon-only"
                              title="Download document"
                            >
                              <FaDownload />
                            </Button>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => handleDeleteDocumentClick(doc)}
                              className="rounded-pill btn-icon-only"
                              title="Delete document"
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
            )}
          </Card.Body>
        </Card>
      </Container>
      
      {/* Upload Modal */}
      <Modal show={showUploadModal} onHide={() => setShowUploadModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Upload Document</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {uploadSuccess ? (
            <Alert variant="success">
              Document uploaded successfully!
            </Alert>
          ) : (
            <>
              {uploadError && (
                <Alert variant="danger">
                  {uploadError}
                </Alert>
              )}
              
              <Form.Group className="mb-3">
                <Form.Label>Select File</Form.Label>
                <Form.Control
                  type="file"
                  onChange={handleFileChange}
                  disabled={isUploading}
                />
                <Form.Text className="text-muted">
                  Supported formats: PDF, DOCX, TXT, MD
                </Form.Text>
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowUploadModal(false)}>
            Close
          </Button>
          {!uploadSuccess && (
            <Button
              variant="primary"
              onClick={handleUpload}
              disabled={isUploading || !file}
            >
              {isUploading ? (
                <>
                  <Spinner as="span" animation="border" size="sm" className="me-2" />
                  Uploading...
                </>
              ) : (
                'Upload'
              )}
            </Button>
          )}
        </Modal.Footer>
      </Modal>
      
      {/* Onboarding Wizard */}
      <OnboardingWizard 
        show={showOnboarding}
        onComplete={handleOnboardingComplete}
        onSkip={() => setShowOnboarding(false)}
        onUploadFile={handleUploadFromOnboarding}
      />
      
      {/* Feature Tour */}
      <FeatureTour 
        steps={tourSteps}
        onComplete={handleTourComplete}
        isActive={showTour}
      />
      
      {/* Delete Confirmation Modal */}
      <Modal 
        show={showDeleteModal} 
        onHide={() => {
          if (!isDeleting) {
            setShowDeleteModal(false);
            setDocumentToDelete(null);
          }
        }} 
        centered
        className="delete-modal"
      >
        <Modal.Header closeButton className="border-0">
          <Modal.Title className="text-danger">
            {deleteSuccess ? 'Document Deleted' : 'Delete Document'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body className="text-center py-4">
          {deleteSuccess ? (
            <div className="success-animation">
              <div className="checkmark-circle">
                <div className="checkmark draw"></div>
              </div>
              <h5 className="mt-4 mb-3">Document Deleted Successfully</h5>
              <p className="text-muted">The document has been permanently removed from your storage.</p>
            </div>
          ) : (
            <>
              <div className="delete-icon-container mb-4">
                <FaExclamationTriangle size={50} className="text-danger" />
              </div>
              <h5 className="mb-3">Are you sure you want to delete this document?</h5>
              <p className="text-muted mb-0">
                <strong>{documentToDelete?.name}</strong>
              </p>
              <p className="text-muted">This action cannot be undone.</p>
              {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
            </>
          )}
        </Modal.Body>
        {!deleteSuccess && (
          <Modal.Footer className="border-0 justify-content-center">
            <Button 
              variant="outline-secondary" 
              onClick={() => {
                setShowDeleteModal(false);
                setDocumentToDelete(null);
              }}
              disabled={isDeleting}
              className="px-4"
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteDocument}
              disabled={isDeleting}
              className="px-4 ms-2"
            >
              {isDeleting ? (
                <>
                  <Spinner as="span" animation="border" size="sm" className="me-2" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </Button>
          </Modal.Footer>
        )}
      </Modal>
    </>
  );
};

export default DashboardPage;      