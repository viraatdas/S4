import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Container, Row, Col, Card, Button, Spinner, 
  Form, Alert, Badge, ListGroup, ToggleButtonGroup, ToggleButton
} from 'react-bootstrap';
import { 
  FaCreditCard, FaCheck, FaInfoCircle, FaArrowLeft, 
  FaCrown, FaRocket, FaUserTie, FaUserCheck 
} from 'react-icons/fa';
import { AuthContext } from '../App';
import API from '../services/api';
import Navbar from '../components/Navbar';

const PaymentPage = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Card details state
  const [cardDetails, setCardDetails] = useState({
    name: '',
    number: '',
    expiry: '',
    cvc: '',
  });
  
  // Fetch subscription plans
  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoading(true);
        const response = await API.getSubscriptionPlans();
        
        if (response.data && Array.isArray(response.data)) {
          setPlans(response.data);
          setLoading(false);
        } else {
          // Fallback to default plans if the API doesn't return proper data
          setPlans([
            {
              id: 'basic',
              name: 'Basic',
              price_monthly: 19.99,
              features: [
                '10 GB Storage',
                '1,000,000 tokens processing/month',
                'Email support',
                'Basic analytics'
              ]
            },
            {
              id: 'standard',
              name: 'Standard',
              price_monthly: 49.99,
              features: [
                '50 GB Storage',
                '5,000,000 tokens processing/month',
                'Video content processing',
                'Priority email support',
                'Advanced analytics'
              ]
            },
            {
              id: 'premium',
              name: 'Premium',
              price_monthly: 99.99,
              features: [
                '200 GB Storage',
                'Unlimited tokens processing',
                'Audio & video content processing',
                'Priority support via chat',
                'Premium analytics',
                'Custom integrations'
              ]
            },
            {
              id: 'enterprise',
              name: 'Enterprise',
              price_monthly: 499.99,
              features: [
                'Unlimited storage',
                'Unlimited processing',
                'Dedicated account manager',
                'Phone, email & chat support',
                'On-premise deployment option',
                'Custom ML model training',
                'SLA guarantee'
              ]
            }
          ]);
          setLoading(false);
        }
      } catch (err) {
        console.error('Error fetching plans:', err);
        
        // Set default plans in case of API error
        setPlans([
          // ... same default plans from above ...
        ]);
        
        setError('Failed to load subscription plans from server. Showing default options.');
        setLoading(false);
      }
    };
    
    fetchPlans();
  }, []);
  
  // Get user's current plan if available
  useEffect(() => {
    if (user && user.subscription && plans.length > 0) {
      const userPlan = plans.find(plan => plan.id === user.subscription.plan_id);
      if (userPlan) {
        setSelectedPlan(userPlan);
      }
    }
  }, [user, plans]);
  
  const getPlanIcon = (planName) => {
    switch (planName.toLowerCase()) {
      case 'basic':
        return <FaUserCheck className="text-info" size={24} />;
      case 'standard':
        return <FaUserTie className="text-success" size={24} />;
      case 'premium':
        return <FaCrown className="text-warning" size={24} />;
      case 'enterprise':
        return <FaRocket className="text-danger" size={24} />;
      default:
        return <FaInfoCircle className="text-secondary" size={24} />;
    }
  };
  
  const handlePlanSelect = (plan) => {
    setSelectedPlan(plan);
    setError('');
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Format card number with spaces
    if (name === 'number') {
      const formattedValue = value
        .replace(/\s/g, '')
        .replace(/(\d{4})/g, '$1 ')
        .trim()
        .slice(0, 19);
      
      setCardDetails({
        ...cardDetails,
        [name]: formattedValue,
      });
      return;
    }
    
    // Format expiry date
    if (name === 'expiry') {
      const formattedValue = value
        .replace(/\D/g, '')
        .replace(/^(\d{2})(\d)/, '$1/$2')
        .slice(0, 5);
      
      setCardDetails({
        ...cardDetails,
        [name]: formattedValue,
      });
      return;
    }
    
    // CVC validation
    if (name === 'cvc') {
      const formattedValue = value.replace(/\D/g, '').slice(0, 3);
      setCardDetails({
        ...cardDetails,
        [name]: formattedValue,
      });
      return;
    }
    
    setCardDetails({
      ...cardDetails,
      [name]: value,
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedPlan) {
      setError('Please select a subscription plan');
      return;
    }
    
    // Validate card details
    if (!cardDetails.name || !cardDetails.number || !cardDetails.expiry || !cardDetails.cvc) {
      setError('Please fill in all payment information');
      return;
    }
    
    // Simple validation for card number format
    const cardNumberDigits = cardDetails.number.replace(/\s/g, '');
    if (cardNumberDigits.length < 16 || !/^\d+$/.test(cardNumberDigits)) {
      setError('Please enter a valid card number');
      return;
    }
    
    // Simple validation for expiry date
    const [month, year] = cardDetails.expiry.split('/');
    if (!month || !year || parseInt(month) > 12 || parseInt(month) < 1) {
      setError('Please enter a valid expiry date (MM/YY)');
      return;
    }
    
    try {
      setPaymentLoading(true);
      setError('');
      
      // In a production app, we would use a payment processor SDK (like Stripe)
      // to securely collect and tokenize the card information before sending to our server.
      // Here's what that would typically look like:
      
      // 1. Tokenize the card information (this is pseudo-code)
      // const paymentToken = await stripeInstance.createToken({
      //   number: cardDetails.number,
      //   exp_month: month,
      //   exp_year: year,
      //   cvc: cardDetails.cvc
      // });
      
      // 2. Send only the token and plan information to our server
      await API.updateSubscription({
        plan_id: selectedPlan.id,
        billing_cycle: billingCycle,
        // In a real app, we'd use the token instead of sending raw card details
        payment_token: "tok_simulated_payment", // This would be paymentToken.id in a real implementation
        cardholder_name: cardDetails.name
      });
      
      setSuccess(`Successfully subscribed to the ${selectedPlan.name} plan!`);
      setPaymentLoading(false);
      
      // Navigate back to dashboard after successful payment
      setTimeout(() => {
        navigate('/');
      }, 2000);
      
    } catch (err) {
      console.error('Payment error:', err);
      setError(err.response?.data?.message || 'Payment processing failed. Please try again or contact support.');
      setPaymentLoading(false);
    }
  };
  
  return (
    <>
      <Navbar />
      <Container className="py-5">
        <Button 
          variant="outline-secondary" 
          className="mb-4"
          onClick={() => navigate('/')}
        >
          <FaArrowLeft className="me-2" /> Back to Dashboard
        </Button>
        
        <h2 className="mb-4">Subscription Plans</h2>
        
        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}
        
        {loading ? (
          <div className="text-center py-5">
            <Spinner animation="border" variant="primary" />
            <p className="mt-3">Loading subscription plans...</p>
          </div>
        ) : (
          <>
            <div className="mb-4">
              <ToggleButtonGroup 
                type="radio" 
                name="billingCycle" 
                value={billingCycle}
                onChange={(val) => setBillingCycle(val)}
                className="mb-4"
              >
                <ToggleButton 
                  id="monthly" 
                  value="monthly" 
                  variant={billingCycle === 'monthly' ? 'primary' : 'outline-primary'}
                >
                  Monthly Billing
                </ToggleButton>
                <ToggleButton 
                  id="yearly" 
                  value="yearly" 
                  variant={billingCycle === 'yearly' ? 'primary' : 'outline-primary'}
                >
                  Yearly Billing (Save 16%)
                </ToggleButton>
              </ToggleButtonGroup>
            </div>
            
            <Row className="mb-5">
              {plans.map((plan) => (
                <Col key={plan.id} md={6} lg={3} className="mb-4">
                  <Card 
                    className={`h-100 ${selectedPlan?.id === plan.id ? 'border-primary' : ''}`}
                    onClick={() => handlePlanSelect(plan)}
                    style={{ cursor: 'pointer' }}
                  >
                    <Card.Header className="d-flex align-items-center">
                      {getPlanIcon(plan.name)}
                      <h5 className="ms-2 mb-0">{plan.name}</h5>
                      {user?.subscription?.plan_id === plan.id && (
                        <Badge bg="success" className="ms-auto">Current Plan</Badge>
                      )}
                    </Card.Header>
                    <Card.Body>
                      <div className="text-center mb-3">
                        <h3>
                          ${billingCycle === 'monthly' ? plan.price_monthly : Math.round(plan.price_monthly * 10 * 12 * 0.84) / 10}
                          <small className="text-muted">{billingCycle === 'monthly' ? '/mo' : '/year'}</small>
                        </h3>
                      </div>
                      <ListGroup variant="flush">
                        {plan.features.map((feature, index) => (
                          <ListGroup.Item key={index} className="border-0 py-2">
                            <FaCheck className="text-success me-2" />
                            {feature}
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    </Card.Body>
                    <Card.Footer className="bg-white">
                      <Button 
                        variant={selectedPlan?.id === plan.id ? 'primary' : 'outline-primary'} 
                        className="w-100"
                        onClick={() => handlePlanSelect(plan)}
                      >
                        {selectedPlan?.id === plan.id ? 'Selected' : 'Select'}
                      </Button>
                    </Card.Footer>
                  </Card>
                </Col>
              ))}
            </Row>
            
            {selectedPlan && (
              <Card className="mb-5">
                <Card.Header>
                  <h4 className="mb-0">Payment Information</h4>
                </Card.Header>
                <Card.Body>
                  <Form onSubmit={handleSubmit}>
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Cardholder Name</Form.Label>
                          <Form.Control
                            type="text"
                            name="name"
                            value={cardDetails.name}
                            onChange={handleInputChange}
                            placeholder="John Doe"
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Card Number</Form.Label>
                          <div className="input-group">
                            <span className="input-group-text">
                              <FaCreditCard />
                            </span>
                            <Form.Control
                              type="text"
                              name="number"
                              value={cardDetails.number}
                              onChange={handleInputChange}
                              placeholder="4242 4242 4242 4242"
                              required
                            />
                          </div>
                        </Form.Group>
                      </Col>
                    </Row>
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Expiry Date</Form.Label>
                          <Form.Control
                            type="text"
                            name="expiry"
                            value={cardDetails.expiry}
                            onChange={handleInputChange}
                            placeholder="MM/YY"
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>CVC</Form.Label>
                          <Form.Control
                            type="text"
                            name="cvc"
                            value={cardDetails.cvc}
                            onChange={handleInputChange}
                            placeholder="123"
                            required
                          />
                        </Form.Group>
                      </Col>
                    </Row>
                    <div className="d-grid mt-4">
                      <Button 
                        type="submit" 
                        variant="primary" 
                        size="lg"
                        disabled={paymentLoading}
                      >
                        {paymentLoading ? (
                          <>
                            <Spinner animation="border" size="sm" className="me-2" /> 
                            Processing Payment...
                          </>
                        ) : (
                          <>
                            Subscribe to {selectedPlan.name} Plan
                          </>
                        )}
                      </Button>
                    </div>
                  </Form>
                </Card.Body>
              </Card>
            )}
          </>
        )}
      </Container>
    </>
  );
};

export default PaymentPage; 