import React from 'react';
import { Container, Row, Col, Button, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaSearch, FaBolt, FaChevronRight, FaFileAudio, FaFileVideo, FaFileAlt, FaBrain, FaCheck } from 'react-icons/fa';

const HomePage = () => {
  const scrollToPricing = () => {
    document.getElementById('pricing-section').scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="main-content p-0">
      {/* Hero Section */}
      <section className="fly-hero">
        <Container className="fly-container">
          <h1 className="fly-hero-title">
            <span>Intelligent Storage</span> with<br />LLM-Powered Understanding
          </h1>
          <p className="fly-hero-description">
            S4 is a next-generation blob storage solution that understands your content. 
            Store any file type - text, audio, video, or documents - and unlock semantic 
            search powered by large language models. Get instant, meaningful results 
            across your entire content library.
          </p>
          <div className="d-flex justify-content-center">
            <Link to="/auth">
              <Button className="fly-button-primary">
                Try S4 Now <FaChevronRight className="ms-2" />
              </Button>
            </Link>
            <Button className="fly-button-secondary" onClick={scrollToPricing}>
              View Pricing
            </Button>
          </div>
        </Container>
        <div className="fly-illustrations"></div>
      </section>

      {/* Features Section */}
      <section className="py-5 bg-white">
        <Container className="py-5">
          <Row className="justify-content-center text-center mb-5">
            <Col lg={8}>
              <h2 className="section-title">Universal Content Understanding</h2>
            </Col>
          </Row>

          <Row className="g-4">
            <Col md={6} lg={3}>
              <div className="fly-card h-100">
                <div className="feature-icon mb-4">
                  <FaBrain />
                </div>
                <h3 className="h5 mb-3">LLM Integration</h3>
                <p className="text-muted mb-0">
                  Built-in large language models understand your content's meaning and context automatically.
                </p>
              </div>
            </Col>

            <Col md={6} lg={3}>
              <div className="fly-card h-100">
                <div className="feature-icon mb-4">
                  <FaFileAlt />
                  <FaFileAudio className="ms-1" />
                  <FaFileVideo className="ms-1" />
                </div>
                <h3 className="h5 mb-3">Multi-Modal Support</h3>
                <p className="text-muted mb-0">
                  Process any file type - text, PDFs, audio, video, and more with semantic understanding.
                </p>
              </div>
            </Col>

            <Col md={6} lg={3}>
              <div className="fly-card h-100">
                <div className="feature-icon mb-4">
                  <FaSearch />
                </div>
                <h3 className="h5 mb-3">Semantic Search</h3>
                <p className="text-muted mb-0">
                  Find content based on meaning and context, not just keywords or metadata.
                </p>
              </div>
            </Col>

            <Col md={6} lg={3}>
              <div className="fly-card h-100">
                <div className="feature-icon mb-4">
                  <FaBolt />
                </div>
                <h3 className="h5 mb-3">Instant Results</h3>
                <p className="text-muted mb-0">
                  Lightning-fast retrieval with optimized vector search across all content types.
                </p>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <Container>
          <Row className="text-center justify-content-center mb-5">
            <Col lg={8}>
              <h2 className="section-title">Enterprise-Ready Storage</h2>
              <p className="text-muted">
                A modern blob storage solution trusted by companies for their intelligent content needs
              </p>
            </Col>
          </Row>
          
          <div className="stats-container">
            <div className="stat-item">
              <div className="stat-value">Any</div>
              <div className="stat-label">File Type</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">LLM</div>
              <div className="stat-label">Powered</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">5ms</div>
              <div className="stat-label">Response Time</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">10K+</div>
              <div className="stat-label">Files Processed</div>
            </div>
          </div>
        </Container>
      </section>

      {/* Pricing Section */}
      <section id="pricing-section" className="py-5 bg-white">
        <Container className="py-5">
          <Row className="justify-content-center text-center mb-5">
            <Col lg={8}>
              <h2 className="section-title">Pricing</h2>
              <p className="text-muted">
                Choose the right plan for your storage and intelligence needs
              </p>
            </Col>
          </Row>
          
          <Row className="g-4">
            <Col md={6} lg={3}>
              <Card className="pricing-card h-100 text-center">
                <Card.Body>
                  <h3 className="mb-3">Free</h3>
                  <div className="price-value mb-4">
                    <span className="price">$0</span>
                    <span className="period">/month</span>
                  </div>
                  <ul className="feature-list list-unstyled">
                    <li><FaCheck className="text-success me-2" />1GB Storage</li>
                    <li><FaCheck className="text-success me-2" />Basic LLM Processing</li>
                    <li><FaCheck className="text-success me-2" />Text Files Only</li>
                    <li><FaCheck className="text-success me-2" />Community Support</li>
                  </ul>
                  <Link to="/auth">
                    <Button variant="outline-primary" className="w-100 mt-4">Get Started</Button>
                  </Link>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={6} lg={3}>
              <Card className="pricing-card h-100 text-center">
                <Card.Body>
                  <h3 className="mb-3">Starter</h3>
                  <div className="price-value mb-4">
                    <span className="price">$29</span>
                    <span className="period">/month</span>
                  </div>
                  <ul className="feature-list list-unstyled">
                    <li><FaCheck className="text-success me-2" />25GB Storage</li>
                    <li><FaCheck className="text-success me-2" />Advanced LLM Processing</li>
                    <li><FaCheck className="text-success me-2" />All File Types</li>
                    <li><FaCheck className="text-success me-2" />Priority Support</li>
                  </ul>
                  <Link to="/auth">
                    <Button variant="outline-primary" className="w-100 mt-4">Get Started</Button>
                  </Link>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={6} lg={3}>
              <Card className="pricing-card h-100 text-center pricing-popular">
                <span className="popular-badge">Most Popular</span>
                <Card.Body>
                  <h3 className="mb-3">Business</h3>
                  <div className="price-value mb-4">
                    <span className="price">$99</span>
                    <span className="period">/month</span>
                  </div>
                  <ul className="feature-list list-unstyled">
                    <li><FaCheck className="text-success me-2" />100GB Storage</li>
                    <li><FaCheck className="text-success me-2" />Premium LLM Models</li>
                    <li><FaCheck className="text-success me-2" />Advanced Analytics</li>
                    <li><FaCheck className="text-success me-2" />24/7 Support</li>
                  </ul>
                  <Link to="/auth">
                    <Button variant="primary" className="w-100 mt-4">Get Started</Button>
                  </Link>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={6} lg={3}>
              <Card className="pricing-card h-100 text-center">
                <Card.Body>
                  <h3 className="mb-3">Enterprise</h3>
                  <div className="price-value mb-4">
                    <span className="price">Custom</span>
                  </div>
                  <ul className="feature-list list-unstyled">
                    <li><FaCheck className="text-success me-2" />Unlimited Storage</li>
                    <li><FaCheck className="text-success me-2" />LLM Fine-tuning</li>
                    <li><FaCheck className="text-success me-2" />Dedicated Infrastructure</li>
                    <li><FaCheck className="text-success me-2" />SLA & Account Manager</li>
                  </ul>
                  <Button variant="outline-primary" className="w-100 mt-4">Contact Sales</Button>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Call to Action */}
      <section className="py-5 bg-white">
        <Container className="py-5 text-center">
          <Row className="justify-content-center">
            <Col lg={8}>
              <h2 className="section-title">Store Smarter, Not Harder</h2>
              <p className="text-muted mb-4">
                Experience the future of storage with built-in intelligence. Upload any file and start searching semantically in minutes.
              </p>
              <Link to="/auth">
                <Button className="fly-button-primary btn-lg">
                  Get Started Free
                </Button>
              </Link>
            </Col>
          </Row>
        </Container>
      </section>
    </div>
  );
};

export default HomePage; 