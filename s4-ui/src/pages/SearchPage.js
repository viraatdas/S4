import React, { useState } from 'react';
import { Container, Form, Button, Card, Alert, Spinner, InputGroup } from 'react-bootstrap';
import { FaSearch, FaFileAlt, FaArrowRight, FaInfoCircle } from 'react-icons/fa';
import s4Service from '../services/s4Service';

const SearchPage = ({ authKey }) => {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [resultLimit, setResultLimit] = useState(5);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      const results = await s4Service.searchDocuments(query, resultLimit);
      setSearchResults(results.results || []);
      setHasSearched(true);
    } catch (err) {
      console.error('Search error:', err);
      setError(
        err.response?.data?.detail || 
        'An error occurred while performing the search. Please try again.'
      );
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Calculate confidence percentage from score
  const getConfidencePercentage = (score) => {
    return Math.round(score * 100);
  };

  // Truncate text if too long
  const truncateText = (text, maxLength = 250) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <Container>
      <h2 className="mb-4">Semantic Search</h2>
      
      <Card className="shadow-sm mb-4">
        <Card.Body>
          <Form onSubmit={handleSearch}>
            <Form.Group className="mb-3">
              <InputGroup>
                <Form.Control
                  type="text"
                  placeholder="Enter your search query..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
                <Button variant="primary" type="submit" disabled={loading}>
                  <FaSearch className="me-2" /> Search
                </Button>
              </InputGroup>
            </Form.Group>
            
            <div className="d-flex align-items-center justify-content-between">
              <Form.Group className="mb-0 d-flex align-items-center">
                <Form.Label className="me-2 mb-0">Results:</Form.Label>
                <Form.Select 
                  style={{ width: '80px' }}
                  value={resultLimit}
                  onChange={(e) => setResultLimit(Number(e.target.value))}
                >
                  <option value="3">3</option>
                  <option value="5">5</option>
                  <option value="10">10</option>
                  <option value="20">20</option>
                </Form.Select>
              </Form.Group>
              
              <div className="text-muted small">
                <FaInfoCircle className="me-1" /> 
                Semantic search looks for meaning, not just keywords
              </div>
            </div>
          </Form>
        </Card.Body>
      </Card>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {loading ? (
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-3">Searching documents...</p>
        </div>
      ) : hasSearched ? (
        searchResults.length > 0 ? (
          <div>
            <h4 className="mb-3">Search Results</h4>
            {searchResults.map((result, index) => (
              <Card key={index} className="mb-3 shadow-sm">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="d-flex align-items-center mb-2">
                      <FaFileAlt className="text-primary me-2" />
                      <h5 className="mb-0">{result.document.title || result.document.filename}</h5>
                    </div>
                    <span className="badge bg-success">
                      {getConfidencePercentage(result.score)}% Match
                    </span>
                  </div>
                  
                  {result.document.category && (
                    <div className="mb-2 text-muted small">
                      Category: {result.document.category}
                    </div>
                  )}
                  
                  <Card.Text className="border-start ps-3 my-3">
                    {truncateText(result.content)}
                  </Card.Text>
                  
                  <div className="text-end">
                    <Button variant="outline-primary" size="sm">
                      View Document <FaArrowRight className="ms-1" />
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            ))}
          </div>
        ) : (
          <Alert variant="info">
            No documents found matching your query. Try different keywords or phrases.
          </Alert>
        )
      ) : (
        <div className="text-center py-5 text-muted">
          <FaSearch className="display-1 mb-3" />
          <p>Enter a search query to find relevant documents</p>
        </div>
      )}
    </Container>
  );
};

export default SearchPage; 