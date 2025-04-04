import React, { useState, useEffect } from 'react';
import { Container, /* Row, Col, */ Card, Button, Form, Alert, Spinner, Modal, Table } from 'react-bootstrap';
import { FaUpload, FaFileAlt, FaTrash, FaExclamationTriangle } from 'react-icons/fa';
import { Formik } from 'formik';
import * as Yup from 'yup';
import s4Service from '../services/s4Service';

const DocumentsPage = ({ authKey }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState('');

  // Load documents
  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await s4Service.getDocuments();
      setDocuments(data.items || []);
      setError('');
    } catch (err) {
      console.error('Error loading documents:', err);
      setError('Failed to load documents. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authKey) {
      loadDocuments();
    }
  }, [authKey]);

  // Delete document
  const handleDeleteDocument = async () => {
    if (!selectedDocument) return;
    
    try {
      await s4Service.deleteDocument(selectedDocument.id);
      setDocuments(documents.filter(doc => doc.id !== selectedDocument.id));
      setShowDeleteModal(false);
      setSelectedDocument(null);
    } catch (err) {
      console.error('Error deleting document:', err);
      setError('Failed to delete document. Please try again later.');
    }
  };

  // Upload validation schema
  const uploadValidationSchema = Yup.object().shape({
    file: Yup.mixed().required('A file is required'),
    title: Yup.string().required('Title is required'),
    category: Yup.string(),
  });

  // Format bytes to human-readable format
  const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  // Format date to readable format
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Documents</h2>
        <Button variant="primary" onClick={() => setShowUploadModal(true)}>
          <FaUpload className="me-2" /> Upload Document
        </Button>
      </div>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {loading ? (
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-3">Loading documents...</p>
        </div>
      ) : documents.length > 0 ? (
        <Card className="shadow-sm">
          <Card.Body>
            <div className="table-responsive">
              <Table hover>
                <thead>
                  <tr>
                    <th>Document</th>
                    <th>Category</th>
                    <th>Size</th>
                    <th>Uploaded</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id}>
                      <td>
                        <div className="d-flex align-items-center">
                          <FaFileAlt className="text-primary me-2" />
                          {doc.title || doc.filename}
                        </div>
                      </td>
                      <td>{doc.category || 'Uncategorized'}</td>
                      <td>{formatBytes(doc.size)}</td>
                      <td>{formatDate(doc.created_at)}</td>
                      <td>
                        <Button 
                          variant="outline-danger" 
                          size="sm"
                          onClick={() => {
                            setSelectedDocument(doc);
                            setShowDeleteModal(true);
                          }}
                        >
                          <FaTrash />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </Card.Body>
        </Card>
      ) : (
        <Alert variant="info">
          <FaUpload className="me-2" />
          No documents uploaded yet. Click "Upload Document" to get started.
        </Alert>
      )}
      
      {/* Upload Modal */}
      <Modal show={showUploadModal} onHide={() => {
        setShowUploadModal(false);
        setUploadSuccess(false);
        setUploadError('');
      }}>
        <Modal.Header closeButton>
          <Modal.Title>Upload Document</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {uploadSuccess ? (
            <Alert variant="success">
              Document uploaded successfully!
            </Alert>
          ) : (
            <Formik
              initialValues={{ file: null, title: '', category: '' }}
              validationSchema={uploadValidationSchema}
              onSubmit={async (values, { setSubmitting, resetForm }) => {
                try {
                  setUploadError('');
                  
                  const metadata = {
                    title: values.title,
                    category: values.category,
                  };
                  
                  await s4Service.uploadDocument(values.file, metadata);
                  setUploadSuccess(true);
                  loadDocuments();
                  resetForm();
                } catch (err) {
                  console.error('Error uploading document:', err);
                  setUploadError(
                    err.response?.data?.detail || 
                    'Failed to upload document. Please try again.'
                  );
                } finally {
                  setSubmitting(false);
                }
              }}
            >
              {({
                values,
                errors,
                touched,
                handleChange,
                handleBlur,
                handleSubmit,
                isSubmitting,
                setFieldValue,
              }) => (
                <Form onSubmit={handleSubmit}>
                  {uploadError && <Alert variant="danger">{uploadError}</Alert>}
                  
                  <Form.Group className="mb-3">
                    <Form.Label>File</Form.Label>
                    <Form.Control
                      type="file"
                      onChange={(e) => {
                        setFieldValue('file', e.currentTarget.files[0]);
                      }}
                      isInvalid={touched.file && errors.file}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.file}
                    </Form.Control.Feedback>
                    <Form.Text className="text-muted">
                      Supported formats: PDF, DOCX, TXT (Max size: 10MB)
                    </Form.Text>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Title</Form.Label>
                    <Form.Control
                      type="text"
                      name="title"
                      placeholder="Document title"
                      value={values.title}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      isInvalid={touched.title && errors.title}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.title}
                    </Form.Control.Feedback>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Category (Optional)</Form.Label>
                    <Form.Control
                      type="text"
                      name="category"
                      placeholder="E.g., Reports, Manuals, Contracts"
                      value={values.category}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      isInvalid={touched.category && errors.category}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.category}
                    </Form.Control.Feedback>
                  </Form.Group>
                  
                  <div className="d-flex justify-content-end">
                    <Button
                      variant="secondary"
                      className="me-2"
                      onClick={() => setShowUploadModal(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      type="submit"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Uploading...' : 'Upload'}
                    </Button>
                  </div>
                </Form>
              )}
            </Formik>
          )}
        </Modal.Body>
        {uploadSuccess && (
          <Modal.Footer>
            <Button
              variant="primary"
              onClick={() => {
                setShowUploadModal(false);
                setUploadSuccess(false);
              }}
            >
              Close
            </Button>
          </Modal.Footer>
        )}
      </Modal>
      
      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="text-center mb-4">
            <FaExclamationTriangle className="text-warning display-4" />
          </div>
          <p>
            Are you sure you want to delete the document:{' '}
            <strong>{selectedDocument?.title || selectedDocument?.filename}</strong>?
          </p>
          <p className="text-danger">This action cannot be undone.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteDocument}>
            Delete
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default DocumentsPage;  