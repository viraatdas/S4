import React, { useState } from 'react';
import { Container, Card, Row, Col, Table, Badge, Button, Form, InputGroup, Spinner, Alert } from 'react-bootstrap';
import { FaCode, FaDownload, FaUpload, FaTrash, FaList, FaSearch, FaRobot, FaQuestion } from 'react-icons/fa';
import Navbar from '../components/Navbar';
import API from '../services/api';

const ApiPage = () => {
  const baseUrl = window.location.origin.replace('3000', '8000');
  // const [downloadExample, setDownloadExample] = useState({
  //   userId: 'user123',
  //   docId: 'doc-123',
  //   filename: 'example.pdf'
  // });

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };
  
  // const handleDownload = (userId, docId, filename) => {
  //   API.downloadDocument(userId, docId, filename)
  //     .then(() => console.log('Download initiated successfully'))
  //     .catch(err => console.error('Download error:', err));
  // };

  return (
    <>
      <Navbar />
      <Container className="py-5 mt-5">
        <Row className="mb-4">
          <Col>
            <h1 className="display-4 mb-3">
              <FaCode className="me-3 text-primary" />
              S4 API Documentation
            </h1>
            <p className="lead text-muted">
              Simple endpoints for document management and semantic search
            </p>
          </Col>
        </Row>

        <Card className="shadow-sm mb-4">
          <Card.Header className="bg-light">
            <h2 className="h5 mb-0">Authentication</h2>
          </Card.Header>
          <Card.Body>
            <p>
              All API requests require authentication. Include your session token in the Authorization header:
            </p>
            <div className="bg-light p-3 rounded mb-3 code-block">
              <code>Authorization: Bearer st-your-session-token</code>
              <Button 
                variant="outline-secondary" 
                size="sm" 
                className="ms-2"
                onClick={() => copyToClipboard('Authorization: Bearer st-your-session-token')}
              >
                Copy
              </Button>
            </div>
          </Card.Body>
        </Card>

        <Card className="shadow-sm mb-4">
          <Card.Header className="bg-light d-flex align-items-center">
            <FaList className="me-2 text-success" />
            <h2 className="h5 mb-0">List Documents</h2>
          </Card.Header>
          <Card.Body>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <Badge bg="success" className="me-2">GET</Badge>
                <code className="endpoint">{baseUrl}/documents</code>
              </div>
              <Button 
                variant="outline-secondary" 
                size="sm"
                onClick={() => copyToClipboard(`${baseUrl}/documents`)}
              >
                Copy URL
              </Button>
            </div>
            
            <p>Returns a list of all documents for the authenticated user.</p>
            
            <h5 className="mt-4">Response Example:</h5>
            <pre className="bg-light p-3 rounded">
{`[
  {
    "id": "doc-123",
    "name": "example.pdf",
    "size": 1024,
    "type": "application/pdf",
    "url": "/documents/view/user123/doc-123/example.pdf",
    "download_url": "/documents/download/user123/doc-123/example.pdf",
    "created_at": "2025-04-02T12:34:56Z",
    "tokens": 256
  }
]`}
            </pre>
          </Card.Body>
        </Card>

        <Card className="shadow-sm mb-4">
          <Card.Header className="bg-light d-flex align-items-center">
            <FaUpload className="me-2 text-primary" />
            <h2 className="h5 mb-0">Upload Document</h2>
          </Card.Header>
          <Card.Body>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <Badge bg="primary" className="me-2">POST</Badge>
                <code className="endpoint">{baseUrl}/documents/upload</code>
              </div>
              <Button 
                variant="outline-secondary" 
                size="sm"
                onClick={() => copyToClipboard(`${baseUrl}/documents/upload`)}
              >
                Copy URL
              </Button>
            </div>
            
            <p>Upload a new document. Must be sent as <code>multipart/form-data</code>.</p>
            
            <h5 className="mt-3">Request Parameters:</h5>
            <Table bordered hover size="sm" className="mb-4">
              <thead className="bg-light">
                <tr>
                  <th>Parameter</th>
                  <th>Type</th>
                  <th>Required</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>file</code></td>
                  <td>File</td>
                  <td>Yes</td>
                  <td>The document file to upload</td>
                </tr>
              </tbody>
            </Table>
            
            <h5>cURL Example:</h5>
            <div className="bg-light p-3 rounded mb-3 code-block">
              <pre className="mb-0">
{`curl -X POST ${baseUrl}/documents/upload \\
  -H "Authorization: Bearer st-your-session-token" \\
  -F "file=@/path/to/your/document.pdf"`}
              </pre>
              <Button 
                variant="outline-secondary" 
                size="sm" 
                className="mt-2"
                onClick={() => copyToClipboard(`curl -X POST ${baseUrl}/documents/upload \\\n  -H "Authorization: Bearer st-your-session-token" \\\n  -F "file=@/path/to/your/document.pdf"`)}
              >
                Copy
              </Button>
            </div>
            
            <h5 className="mt-4">Response Example:</h5>
            <pre className="bg-light p-3 rounded">
{`{
  "success": true,
  "documentId": "doc-123",
  "filename": "document.pdf",
  "url": "/documents/view/user123/doc-123/document.pdf",
  "download_url": "/documents/download/user123/doc-123/document.pdf",
  "message": "Document uploaded successfully"
}`}
            </pre>
          </Card.Body>
        </Card>

        <Card className="shadow-sm mb-4">
          <Card.Header className="bg-light d-flex align-items-center">
            <FaDownload className="me-2 text-info" />
            <h2 className="h5 mb-0">Download Document</h2>
          </Card.Header>
          <Card.Body>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <Badge bg="info" className="me-2">GET</Badge>
                <code className="endpoint">{baseUrl}/documents/download/{'{user_id}'}/{'{doc_id}'}/{'{filename}'}</code>
              </div>
              <Button 
                variant="outline-secondary" 
                size="sm"
                onClick={() => copyToClipboard(`${baseUrl}/documents/download/{user_id}/{doc_id}/{filename}`)}
              >
                Copy URL
              </Button>
            </div>
            
            <p>Download a specific document. Returns the file with <code>Content-Disposition: attachment</code>.</p>
            
            <h5 className="mt-3">Path Parameters:</h5>
            <Table bordered hover size="sm" className="mb-4">
              <thead className="bg-light">
                <tr>
                  <th>Parameter</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>user_id</code></td>
                  <td>ID of the user who owns the document</td>
                </tr>
                <tr>
                  <td><code>doc_id</code></td>
                  <td>ID of the document to download</td>
                </tr>
                <tr>
                  <td><code>filename</code></td>
                  <td>Original filename of the document</td>
                </tr>
              </tbody>
            </Table>
            
            <h5>cURL Example:</h5>
            <div className="bg-light p-3 rounded mb-3 code-block">
              <pre className="mb-0">
{`curl -X GET ${baseUrl}/documents/download/user123/doc-123/document.pdf \\
  -H "Authorization: Bearer st-your-session-token" \\
  --output downloaded-document.pdf`}
              </pre>
              <Button 
                variant="outline-secondary" 
                size="sm" 
                className="mt-2"
                onClick={() => copyToClipboard(`curl -X GET ${baseUrl}/documents/download/user123/doc-123/document.pdf \\\n  -H "Authorization: Bearer st-your-session-token" \\\n  --output downloaded-document.pdf`)}
              >
                Copy
              </Button>
            </div>
          </Card.Body>
        </Card>

        <Card className="shadow-sm mb-4">
          <Card.Header className="bg-light d-flex align-items-center">
            <FaQuestion className="me-2 text-primary" />
            <h2 className="h5 mb-0">Query Documents</h2>
          </Card.Header>
          <Card.Body>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <Badge bg="primary" className="me-2">POST</Badge>
                <code className="endpoint">{baseUrl}/documents/query</code>
              </div>
              <Button 
                variant="outline-secondary" 
                size="sm"
                onClick={() => copyToClipboard(`${baseUrl}/documents/query`)}
              >
                Copy URL
              </Button>
            </div>
            
            <p>Ask questions about your documents and get AI-powered answers based on their content.</p>
            
            <h5 className="mt-3">Request Parameters:</h5>
            <Table bordered hover size="sm" className="mb-4">
              <thead className="bg-light">
                <tr>
                  <th>Parameter</th>
                  <th>Type</th>
                  <th>Required</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>query</code></td>
                  <td>String</td>
                  <td>Yes</td>
                  <td>The question or query about your documents</td>
                </tr>
                <tr>
                  <td><code>document_ids</code></td>
                  <td>Array</td>
                  <td>No</td>
                  <td>Optional array of document IDs to limit the search scope</td>
                </tr>
              </tbody>
            </Table>
            
            <h5>cURL Example:</h5>
            <div className="bg-light p-3 rounded mb-3 code-block">
              <pre className="mb-0">
{`curl -X POST ${baseUrl}/documents/query \\
  -H "Authorization: Bearer st-your-session-token" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What are the key points in the quarterly report?",
    "document_ids": ["doc-123", "doc-456"]
  }'`}
              </pre>
              <Button 
                variant="outline-secondary" 
                size="sm" 
                className="mt-2"
                onClick={() => copyToClipboard(`curl -X POST ${baseUrl}/documents/query \
  -H "Authorization: Bearer st-your-session-token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key points in the quarterly report?",
    "document_ids": ["doc-123", "doc-456"]
  }'`)}
              >
                Copy
              </Button>
            </div>
            
            <h5 className="mt-4">Response Example:</h5>
            <pre className="bg-light p-3 rounded">
{`{
  "answer": "The quarterly report highlights three key points: 1) Revenue increased by 15% year-over-year, 2) New product line exceeded sales expectations by 20%, and 3) Expansion into European markets is planned for Q3.",
  "sources": [
    {
      "document_id": "doc-123",
      "document_name": "Q2_Financial_Report.pdf",
      "relevance_score": 0.92
    }
  ]
}`}
            </pre>

            <h5 className="mt-4">Try It Out:</h5>
            <QueryDocumentsDemo baseUrl={baseUrl} />
          </Card.Body>
        </Card>

        <Card className="shadow-sm mb-4">
          <Card.Header className="bg-light d-flex align-items-center">
            <FaTrash className="me-2 text-danger" />
            <h2 className="h5 mb-0">Delete Document</h2>
          </Card.Header>
          <Card.Body>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <Badge bg="danger" className="me-2">DELETE</Badge>
                <code className="endpoint">{baseUrl}/documents/{'{doc_id}'}</code>
              </div>
              <Button 
                variant="outline-secondary" 
                size="sm"
                onClick={() => copyToClipboard(`${baseUrl}/documents/{doc_id}`)}
              >
                Copy URL
              </Button>
            </div>
            
            <p>Delete a specific document.</p>
            
            <h5 className="mt-3">Path Parameters:</h5>
            <Table bordered hover size="sm" className="mb-4">
              <thead className="bg-light">
                <tr>
                  <th>Parameter</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>doc_id</code></td>
                  <td>ID of the document to delete</td>
                </tr>
              </tbody>
            </Table>
            
            <h5>cURL Example:</h5>
            <div className="bg-light p-3 rounded mb-3 code-block">
              <pre className="mb-0">
{`curl -X DELETE ${baseUrl}/documents/doc-123 \\
  -H "Authorization: Bearer st-your-session-token"`}
              </pre>
              <Button 
                variant="outline-secondary" 
                size="sm" 
                className="mt-2"
                onClick={() => copyToClipboard(`curl -X DELETE ${baseUrl}/documents/doc-123 \\\n  -H "Authorization: Bearer st-your-session-token"`)}
              >
                Copy
              </Button>
            </div>
            
            <h5 className="mt-4">Response Example:</h5>
            <pre className="bg-light p-3 rounded">
{`{
  "success": true,
  "message": "Document doc-123 deleted successfully"
}`}
            </pre>
          </Card.Body>
        </Card>
      </Container>
    </>
  );
};

// Query Documents Demo Component
const QueryDocumentsDemo = ({ baseUrl }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // In a real implementation, this would make an actual API call
      // For demo purposes, we're simulating a response
      setTimeout(() => {
        const demoResponse = {
          answer: `Based on your documents, ${query.trim().endsWith('?') ? '' : 'regarding "' + query + '", '} the key information is that the project has been progressing well with all milestones met on time. The budget is currently 5% under projections, and stakeholder feedback has been overwhelmingly positive.`,
          sources: [
            {
              document_id: "doc-123",
              document_name: "Project_Status_Report.pdf",
              relevance_score: 0.89
            },
            {
              document_id: "doc-456",
              document_name: "Budget_Analysis_Q2.xlsx",
              relevance_score: 0.76
            }
          ]
        };
        setResult(demoResponse);
        setLoading(false);
      }, 1500);
    } catch (err) {
      setError('An error occurred while processing your query. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="query-demo mt-3">
      <Form onSubmit={handleSubmit}>
        <InputGroup className="mb-3">
          <Form.Control
            placeholder="Ask a question about your documents..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />
          <Button variant="primary" type="submit" disabled={loading || !query.trim()}>
            {loading ? <Spinner animation="border" size="sm" /> : <FaSearch />}
            {loading ? ' Searching...' : ' Ask'}
          </Button>
        </InputGroup>
      </Form>

      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}

      {result && (
        <div className="mt-3">
          <Card>
            <Card.Header className="bg-light d-flex align-items-center">
              <FaRobot className="me-2 text-primary" />
              <h6 className="mb-0">Answer</h6>
            </Card.Header>
            <Card.Body>
              <p>{result.answer}</p>
              
              <h6 className="mt-3 mb-2">Sources:</h6>
              <ul className="list-group">
                {result.sources.map((source, index) => (
                  <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <span className="fw-bold">{source.document_name}</span>
                      <span className="text-muted ms-2">({source.document_id})</span>
                    </div>
                    <Badge bg="info" pill>
                      {Math.round(source.relevance_score * 100)}% match
                    </Badge>
                  </li>
                ))}
              </ul>
            </Card.Body>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ApiPage;
