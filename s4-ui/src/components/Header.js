import React from 'react';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { FaSearch, FaFile, FaChartBar, FaSignOutAlt } from 'react-icons/fa';

const Header = ({ isLoggedIn, onLogout }) => {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };
  
  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        <Navbar.Brand as={Link} to={isLoggedIn ? "/dashboard" : "/login"}>
          <img
            src="/logo.png"
            width="30"
            height="30"
            className="d-inline-block align-top me-2"
            alt="S4 Logo"
          />
          S4 - Semantic Search
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          {isLoggedIn ? (
            <>
              <Nav className="me-auto">
                <Nav.Link as={Link} to="/dashboard">
                  <FaChartBar className="me-1" /> Dashboard
                </Nav.Link>
                <Nav.Link as={Link} to="/documents">
                  <FaFile className="me-1" /> Documents
                </Nav.Link>
                <Nav.Link as={Link} to="/search">
                  <FaSearch className="me-1" /> Search
                </Nav.Link>
              </Nav>
              <Button variant="outline-light" onClick={handleLogout}>
                <FaSignOutAlt className="me-1" /> Logout
              </Button>
            </>
          ) : (
            <Nav className="ms-auto">
              <Nav.Link as={Link} to="/login">Login</Nav.Link>
            </Nav>
          )}
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header; 