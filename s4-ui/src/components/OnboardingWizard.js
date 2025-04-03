import React, { useState } from 'react';
import { Modal, Button, Container, Row, Col, ProgressBar, Form, Alert } from 'react-bootstrap';
import { FaCloudUploadAlt, FaSearch, FaBrain, FaFileAlt, FaFileVideo, FaFileAudio, FaCheckCircle, FaArrowRight, FaArrowLeft } from 'react-icons/fa';

const OnboardingWizard = ({ show, onComplete, onSkip, onUploadFile }) => {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState('');
  
  const totalSteps = 3;
  
  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      onComplete();
    }
  };
  
  const handlePrevious = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };
  
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadError('');
    }
  };
  
  const handleUpload = async () => {
    if (!file) {
      setUploadError('Please select a file first');
      return;
    }
    
    setIsUploading(true);
    setUploadError('');
    
    try {
      await onUploadFile(file);
      setUploadSuccess(true);
      setTimeout(() => {
        handleNext();
      }, 1500);
    } catch (error) {
      setUploadError(error.message || 'Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };
  
  // Content for each step
  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <div className="text-center p-4">
            <div className="onboarding-icon mb-4">
              <FaBrain className="text-primary" size={60} />
            </div>
            <h2>Welcome to S4!</h2>
            <p className="lead mb-4">
              Your intelligent storage solution with built-in semantic understanding.
            </p>
            <Row className="justify-content-center mb-4">
              <Col md={10}>
                <div className="d-flex mb-4 justify-content-center">
                  <div className="feature-item text-center px-3">
                    <FaFileAlt className="feature-icon text-primary mb-2" />
                    <div>Text</div>
                  </div>
                  <div className="feature-item text-center px-3">
                    <FaFileVideo className="feature-icon text-success mb-2" />
                    <div>Video</div>
                  </div>
                  <div className="feature-item text-center px-3">
                    <FaFileAudio className="feature-icon text-info mb-2" />
                    <div>Audio</div>
                  </div>
                </div>
                <p className="text-muted">
                  S4 can process and understand virtually any file type, letting you search 
                  by meaning rather than just keywords.
                </p>
              </Col>
            </Row>
          </div>
        );
      
      case 2:
        return (
          <div className="p-4">
            <div className="text-center mb-4">
              <div className="onboarding-icon mb-3">
                <FaCloudUploadAlt className="text-primary" size={60} />
              </div>
              <h2>Upload Your First Document</h2>
              <p className="text-muted mb-4">
                Let's get started by uploading your first file to experience the power of semantic search.
              </p>
            </div>
            
            {uploadSuccess ? (
              <div className="text-center my-4">
                <FaCheckCircle className="text-success" size={60} />
                <h4 className="mt-3">Upload Successful!</h4>
                <p className="text-muted">
                  Your document has been uploaded and is being processed.
                </p>
              </div>
            ) : (
              <Form>
                {uploadError && <Alert variant="danger">{uploadError}</Alert>}
                
                <Form.Group className="mb-4">
                  <Form.Label>Select a file to upload</Form.Label>
                  <Form.Control
                    type="file"
                    onChange={handleFileChange}
                    disabled={isUploading}
                  />
                  <Form.Text className="text-muted">
                    Supported formats: PDF, DOCX, TXT, MP3, MP4, etc.
                  </Form.Text>
                </Form.Group>
                
                <div className="text-center">
                  <Button 
                    variant="primary" 
                    onClick={handleUpload}
                    disabled={!file || isUploading}
                    className="px-4"
                  >
                    {isUploading ? 'Uploading...' : 'Upload File'}
                  </Button>
                  <div className="mt-3">
                    <Button 
                      variant="link" 
                      onClick={handleNext}
                    >
                      Skip for now
                    </Button>
                  </div>
                </div>
              </Form>
            )}
          </div>
        );
      
      case 3:
        return (
          <div className="text-center p-4">
            <div className="onboarding-icon mb-4">
              <FaSearch className="text-primary" size={60} />
            </div>
            <h2>Semantic Search Power</h2>
            <p className="lead mb-3">
              You're all set! Now you can search your content semantically.
            </p>
            <div className="search-demo p-4 bg-light rounded mb-4">
              <div className="search-example mb-3">
                <div className="search-query">
                  <strong>Search query:</strong> "Climate change impacts on agriculture"
                </div>
                <div className="search-result mt-2 text-start">
                  <div className="result-item p-2 border-start border-primary border-3">
                    <div className="file-name text-muted small">report.pdf</div>
                    <div className="content">
                      "...our analysis shows that rising temperatures will significantly affect crop yields in tropical regions..."
                    </div>
                  </div>
                </div>
              </div>
              <p className="text-muted small mb-0">
                Even if the terms don't match exactly, S4 understands the meaning and finds relevant content.
              </p>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <Modal 
      show={show} 
      onHide={onSkip}
      centered
      backdrop="static"
      size="lg"
      className="onboarding-modal"
    >
      <Modal.Header className="border-0 pb-0">
        <Container>
          <ProgressBar 
            now={(step / totalSteps) * 100} 
            className="onboarding-progress" 
          />
        </Container>
      </Modal.Header>
      
      <Modal.Body>
        {renderStepContent()}
      </Modal.Body>
      
      <Modal.Footer className="border-0 pt-0">
        <Container>
          <div className="d-flex justify-content-between">
            <Button 
              variant="outline-secondary"
              onClick={step === 1 ? onSkip : handlePrevious}
            >
              {step === 1 ? 'Skip Tutorial' : (
                <>
                  <FaArrowLeft className="me-2" /> Back
                </>
              )}
            </Button>
            
            <Button 
              variant="primary"
              onClick={handleNext}
              disabled={step === 2 && !uploadSuccess && file}
            >
              {step === totalSteps ? 'Get Started' : (
                <>
                  Next <FaArrowRight className="ms-2" />
                </>
              )}
            </Button>
          </div>
        </Container>
      </Modal.Footer>
    </Modal>
  );
};

export default OnboardingWizard; 