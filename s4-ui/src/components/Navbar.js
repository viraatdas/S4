import React, { useContext, useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Navbar as BootstrapNavbar, Nav, Container, NavDropdown, Badge } from 'react-bootstrap';
import { FaSignOutAlt, FaCreditCard, FaUserCircle, FaShieldAlt } from 'react-icons/fa';
import { AuthContext } from '../App';

const Navbar = () => {
  const { isAuthenticated, user, handleLogout } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [showDropdown, setShowDropdown] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  
  // Check if user is admin
  useEffect(() => {
    const adminKey = localStorage.getItem('adminKey');
    setIsAdmin(!!adminKey);
    
    // Add scroll listener
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  
  const getUserInitials = () => {
    if (!user || !user.name) {
      // Return a styled S4 logo for users without a name
      return (
        <span style={{ fontWeight: 800, letterSpacing: '-1px' }}>S4</span>
      );
    }
    
    const nameParts = user.name.split(' ');
    if (nameParts.length === 1) {
      return nameParts[0].charAt(0).toUpperCase();
    }
    
    return `${nameParts[0].charAt(0)}${nameParts[nameParts.length - 1].charAt(0)}`.toUpperCase();
  };
  
  const getPlanBadge = () => {
    if (!user || !user.subscription) return null;
    
    const planName = user.subscription.plan_name;
    let variant = 'secondary';
    
    switch (planName.toLowerCase()) {
      case 'basic':
        variant = 'info';
        break;
      case 'standard':
        variant = 'success';
        break;
      case 'premium':
        variant = 'warning';
        break;
      case 'enterprise':
        variant = 'danger';
        break;
      default:
        break;
    }
    
    return (
      <Badge 
        bg={variant} 
        className="ms-2 rounded-pill"
        style={{ fontSize: '0.7rem', padding: '0.35em 0.8em' }}
      >
        {planName}
      </Badge>
    );
  };
  
  const handleGoToProfile = () => {
    navigate('/profile');
    setShowDropdown(false);
  };
  
  const handleGoToPayment = () => {
    navigate('/payment');
    setShowDropdown(false);
  };
  
  const handleGoToAdminDashboard = () => {
    navigate('/admin/dashboard');
    setShowDropdown(false);
  };
  
  const handleUserLogout = () => {
    handleLogout();
    setShowDropdown(false);
  };
  
  const scrollToPricing = (e) => {
    e.preventDefault();
    const pricingSection = document.getElementById('pricing-section');
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'smooth' });
    } else {
      navigate('/#pricing-section');
    }
  };
  
  return (
    <BootstrapNavbar 
      expand="lg" 
      className={`fly-navbar ${scrolled ? 'scrolled' : ''}`}
      fixed="top"
    >
      <Container className="fly-container">
        <BootstrapNavbar.Brand as={Link} to="/" className="fly-brand">
          <div className="fly-logo">
            <span style={{ fontWeight: 800, letterSpacing: '-1px' }}>S4</span>
          </div>
        </BootstrapNavbar.Brand>
        
        {isAuthenticated && (
          <Nav className="fly-nav mx-auto d-none d-lg-flex">
            <Nav.Link as={Link} to="/dashboard" className="fly-nav-link">
              Dashboard
            </Nav.Link>
            <Nav.Link as={Link} to="/api" className="fly-nav-link">
              API
            </Nav.Link>
            {/* Keep only Dashboard and API links as requested by user */}
          </Nav>
        )}
        
        <BootstrapNavbar.Toggle aria-controls="navbar-nav" />
        
        <BootstrapNavbar.Collapse id="navbar-nav" className="justify-content-end">
          {!isAuthenticated && (
            <Nav className="d-none d-lg-flex me-lg-4">
              <Nav.Link as={Link} to="/docs" className="fly-nav-link">
                Docs
              </Nav.Link>
              <Nav.Link href="/#pricing-section" className="fly-nav-link" onClick={scrollToPricing}>
                Pricing
              </Nav.Link>
            </Nav>
          )}
          
          <Nav>
            {isAuthenticated ? (
              <div className="d-flex align-items-center">
                <NavDropdown 
                  show={showDropdown} 
                  onToggle={(isOpen) => setShowDropdown(isOpen)}
                  title={
                    <div className="user-profile-toggle">
                      <div className="user-avatar" aria-label="User profile">
                        {getUserInitials()}
                      </div>
                    </div>
                  } 
                  id="user-dropdown" 
                  align="end"
                  className="user-dropdown"
                >
                  <div className="dropdown-header">
                    <div className="user-profile-info">
                      <div className="user-avatar-large">
                        {getUserInitials()}
                      </div>
                      <div className="user-details">
                        <h6 className="user-fullname">{user?.name || 'User'}</h6>
                        <p className="user-email">{user?.email || 'email@example.com'}</p>
                      </div>
                    </div>
                  </div>
                  
                  <NavDropdown.Item onClick={handleGoToProfile} className="dropdown-item-modern">
                    <FaUserCircle className="dropdown-icon" /> 
                    <span>Profile</span>
                  </NavDropdown.Item>
                  
                  <NavDropdown.Item onClick={handleGoToPayment} className="dropdown-item-modern">
                    <FaCreditCard className="dropdown-icon" /> 
                    <span>Subscription</span>
                    {getPlanBadge()}
                  </NavDropdown.Item>
                  
                  {isAdmin && (
                    <NavDropdown.Item onClick={handleGoToAdminDashboard} className="dropdown-item-modern">
                      <FaShieldAlt className="dropdown-icon" /> 
                      <span>Admin Dashboard</span>
                    </NavDropdown.Item>
                  )}
                  
                  <NavDropdown.Divider />
                  
                  <NavDropdown.Item onClick={handleUserLogout} className="dropdown-item-modern text-danger">
                    <FaSignOutAlt className="dropdown-icon" /> 
                    <span>Sign Out</span>
                  </NavDropdown.Item>
                </NavDropdown>
              </div>
            ) : (
              <>
                <Nav.Link as={Link} to="/login" className="fly-button-secondary me-2">
                  Sign In
                </Nav.Link>
                <Nav.Link as={Link} to="/login" className="fly-button-primary d-none d-sm-block">
                  Get Started
                </Nav.Link>
              </>
            )}
          </Nav>
        </BootstrapNavbar.Collapse>
      </Container>
    </BootstrapNavbar>
  );
};

export default Navbar; 