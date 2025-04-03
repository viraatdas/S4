import axios from 'axios';

// Get base URL from environment or use localhost default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add the API key or auth token to each request
apiClient.interceptors.request.use(
  (config) => {
    const apiKey = localStorage.getItem('apiKey');
    const accessToken = localStorage.getItem('accessToken');
    const adminKey = localStorage.getItem('adminKey');
    
    // Use admin key if available for admin endpoints
    if (adminKey && config.url.includes('/admin/')) {
      config.headers['X-Admin-Key'] = adminKey;
    }
    // Use access token if available (OAuth), otherwise use API key
    else if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    } else if (apiKey) {
      config.headers['X-API-Key'] = apiKey;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      // Clear tokens and redirect to login
      localStorage.removeItem('apiKey');
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
      return Promise.reject(error);
    }
    
    // Handle refresh token flow (with 403 status)
    if (error.response && error.response.status === 403) {
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken) {
        try {
          // Clear old access token
          localStorage.removeItem('accessToken');
          
          // Get new access token
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          // Store new access token
          localStorage.setItem('accessToken', response.data.access_token);
          
          // Retry the original request with new token
          const originalRequest = error.config;
          originalRequest.headers['Authorization'] = `Bearer ${response.data.access_token}`;
          return axios(originalRequest);
        } catch (refreshError) {
          // If refresh fails, clear all tokens and redirect to login
          console.error('Token refresh failed:', refreshError);
          localStorage.removeItem('apiKey');
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

const API = {
  // Authentication
  login: (credentials) => {
    // Support both API key and email/password login
    if (typeof credentials === 'string') {
      // Legacy API key login
      return apiClient.post('/auth/verify', { api_key: credentials });
    } else {
      // New email/password login
      return apiClient.post('/auth/login', credentials);
    }
  },
  
  // Verify JWT token
  verifyToken: (token) => {
    return apiClient.post('/auth/verify-token', { token });
  },
  
  // User registration
  register: (userData) => {
    return apiClient.post('/auth/register', userData);
  },
  
  // Password reset request
  requestPasswordReset: (email) => {
    return apiClient.post('/auth/reset-password-request', { email });
  },
  
  // Reset password with token
  resetPassword: (token, newPassword) => {
    return apiClient.post('/auth/reset-password', { token, new_password: newPassword });
  },
  
  // Admin login
  adminLogin: (adminKey) => {
    return apiClient.get('/admin/verify', {
      headers: { 'X-Admin-Key': adminKey }
    });
  },
  
  // Google OAuth authentication
  googleLogin: () => {
    return apiClient.get('/auth/google');
  },
  
  // OAuth callback
  oauthCallback: (provider, code, state) => {
    return apiClient.post(`/auth/${provider}/callback`, { code, state });
  },
  
  // Logout 
  logout: () => {
    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (accessToken || refreshToken) {
      return apiClient.post('/auth/logout', { 
        refresh_token: refreshToken 
      }).catch(err => {
        console.error('Logout API error:', err);
        // Always clear tokens even if the API call fails
        localStorage.removeItem('apiKey');
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      });
    }
    
    return Promise.resolve();
  },
  
  // Request API access - now just forwards to register
  requestAccess: (userData) => {
    return apiClient.post('/auth/register', userData);
  },
  
  // User profile
  getUserProfile: () => {
    return apiClient.get('/user/profile');
  },
  
  updateUserProfile: (profileData) => {
    return apiClient.put('/user/profile', profileData);
  },
  
  // Documents
  getDocuments: () => {
    // Add timestamp to prevent caching
    return apiClient.get(`/documents?_t=${Date.now()}`);
  },
  
  uploadDocument: (formData) => {
    return apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  deleteDocument: (id) => {
    return apiClient.delete(`/documents/${id}`);
  },
  
  downloadDocument: (userId, docId, filename) => {
    // Create a hidden anchor element to trigger the download
    const link = document.createElement('a');
    link.href = `${API_BASE_URL}/documents/download/${userId}/${docId}/${filename}`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    return Promise.resolve({ success: true });
  },
  
  // Search
  searchDocuments: (query) => {
    return apiClient.post('/search', { query });
  },
  
  // Subscription plans
  getSubscriptionPlans: () => {
    return apiClient.get('/plans');
  },
  
  // Update subscription
  updateSubscription: (subscriptionData) => {
    return apiClient.post('/billing/subscription', subscriptionData);
  },
  
  // Get billing history
  getBillingHistory: () => {
    return apiClient.get('/billing/history');
  },
  
  // Admin API - Tenant Management
  createTenant: (tenantData) => {
    return apiClient.post('/admin/tenants', tenantData);
  },
  
  listTenants: () => {
    return apiClient.get('/admin/tenants');
  },
  
  getTenant: (tenantId) => {
    return apiClient.get(`/admin/tenants/${tenantId}`);
  },
  
  updateTenant: (tenantId, tenantData) => {
    return apiClient.put(`/admin/tenants/${tenantId}`, tenantData);
  },
  
  deleteTenant: (tenantId) => {
    return apiClient.delete(`/admin/tenants/${tenantId}`);
  },
  
  // Get usage statistics
  getUsageStats: () => {
    return apiClient.get('/user/usage');
  }
};

export default API; 