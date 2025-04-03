/**
 * API service for S4
 * This service handles API calls with SuperTokens authentication
 */

import { getSessionToken } from './auth-service';

// API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Make an authenticated API call
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} API response
 */
export const apiCall = async (endpoint, options = {}) => {
  try {
    // Get session token from SuperTokens
    const sessionToken = await getSessionToken();
    
    // Default headers
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    // Add authentication header
    if (sessionToken) {
      headers['Authorization'] = `Bearer ${sessionToken}`;
    } else {
      // Fall back to API key if available
      const apiKey = localStorage.getItem('token');
      if (apiKey) {
        headers['X-API-Key'] = apiKey;
      }
    }
    
    // Make API call
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
    
    // Handle response
    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: response.statusText,
      }));
      throw new Error(error.message || 'API request failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API error (${endpoint}):`, error);
    throw error;
  }
};

/**
 * API service methods
 */
const ApiService = {
  // File operations
  uploadFile: async (file, metadata = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (Object.keys(metadata).length > 0) {
      formData.append('metadata_json', JSON.stringify(metadata));
    }
    
    return apiCall('/files', {
      method: 'POST',
      headers: {
        // Don't set Content-Type here, it will be set automatically with the boundary
      },
      body: formData,
    });
  },
  
  listFiles: async (prefix = '') => {
    return apiCall(`/files?prefix=${encodeURIComponent(prefix)}`);
  },
  
  deleteFile: async (fileId) => {
    return apiCall(`/files/${fileId}`, {
      method: 'DELETE',
    });
  },
  
  getFileMetadata: async (fileId) => {
    return apiCall(`/files/${fileId}/metadata`);
  },
  
  updateFileMetadata: async (fileId, metadata) => {
    return apiCall(`/files/${fileId}/metadata`, {
      method: 'PUT',
      body: JSON.stringify(metadata),
    });
  },
  
  // Search operations
  searchFiles: async (query, limit = 5, fileId = null) => {
    let url = `/search?query=${encodeURIComponent(query)}&limit=${limit}`;
    if (fileId) {
      url += `&file_id=${fileId}`;
    }
    return apiCall(url);
  },
  
  // Usage statistics
  getUsage: async () => {
    return apiCall('/usage');
  },
};

export default ApiService;
