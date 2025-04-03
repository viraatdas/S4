import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Nav } from 'react-bootstrap';
import { 
  FaUsersCog, FaChartLine, FaCodeBranch, 
  FaCreditCard, FaDatabase, FaCog, FaSignOutAlt 
} from 'react-icons/fa';

const AdminSidebar = ({ onLogout }) => {
  const location = useLocation();
  
  // Define sidebar items
  const sidebarItems = [
    {
      path: '/admin/dashboard',
      label: 'Tenants',
      icon: <FaUsersCog />
    },
    {
      path: '/admin/analytics',
      label: 'Analytics',
      icon: <FaChartLine />
    },
    {
      path: '/admin/plans',
      label: 'Subscription Plans',
      icon: <FaCreditCard />
    },
    {
      path: '/admin/storage',
      label: 'Storage',
      icon: <FaDatabase />
    },
    {
      path: '/admin/system',
      label: 'System Settings',
      icon: <FaCog />
    },
    {
      path: '/admin/versions',
      label: 'API Versions',
      icon: <FaCodeBranch />
    }
  ];
  
  return (
    <div className="admin-sidebar bg-dark text-white h-100 d-flex flex-column">
      <div className="p-3 border-bottom border-secondary">
        <h4 className="mb-0 text-center">
          S4 Admin
        </h4>
      </div>
      
      <Nav className="flex-column mt-3">
        {sidebarItems.map((item) => (
          <Nav.Item key={item.path}>
            <Nav.Link
              as={Link}
              to={item.path}
              className={`sidebar-item d-flex align-items-center ${
                location.pathname === item.path ? 'active' : ''
              }`}
            >
              <span className="icon-wrapper me-3">
                {item.icon}
              </span>
              {item.label}
            </Nav.Link>
          </Nav.Item>
        ))}
      </Nav>
      
      <div className="mt-auto border-top border-secondary p-3">
        <Nav.Link 
          onClick={onLogout}
          className="sidebar-item d-flex align-items-center text-danger"
        >
          <span className="icon-wrapper me-3">
            <FaSignOutAlt />
          </span>
          Logout
        </Nav.Link>
      </div>
      
      <div className="p-3 text-center">
        <small className="text-muted">
          S4 Admin Portal v1.0.0
        </small>
      </div>
    </div>
  );
};

export default AdminSidebar; 