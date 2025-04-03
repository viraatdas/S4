import axios from 'axios';

// Default to localhost in development, but can be overridden with environment variables
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create an axios instance with default config
const s4Api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth key to each request
s4Api.interceptors.request.use(
  (config) => {
    const tenantKey = localStorage.getItem('tenantKey');
    if (tenantKey) {
      config.headers['X-Tenant-Key'] = tenantKey;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const s4Service = {
  // Validate tenant key
  validateTenantKey: async (tenantKey) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tenant/validate`, {
        headers: {
          'X-Tenant-Key': tenantKey,
        },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get dashboard stats
  getDashboardStats: async () => {
    try {
      const response = await s4Api.get('/tenant/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Document operations
  getDocuments: async (page = 1, limit = 10) => {
    try {
      const response = await s4Api.get('/documents', {
        params: { page, limit },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  uploadDocument: async (file, metadata) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('metadata', JSON.stringify(metadata));

      const response = await s4Api.post('/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  deleteDocument: async (documentId) => {
    try {
      const response = await s4Api.delete(`/documents/${documentId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Search operations
  searchDocuments: async (query, limit = 5) => {
    try {
      const response = await s4Api.post('/search', {
        query,
        limit,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default s4Service; 