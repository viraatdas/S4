import Session from 'supertokens-auth-react/recipe/session';

// Get API domain from environment or use default
const getApiDomain = () => process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * API client with SuperTokens session management
 * This will automatically handle adding auth tokens to requests
 * and refreshing tokens when needed
 */
export const apiCall = async (url, method, body) => {
  const headers = {
    'Content-Type': 'application/json',
  };

  // Session.addAxiosInterceptors() is called in the SuperTokens init
  // so we don't need to manually add auth headers here

  const config = {
    method,
    url: `${getApiDomain()}${url}`,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  };

  // Use fetch with SuperTokens session management
  const response = await fetch(config.url, {
    method: config.method,
    headers: config.headers,
    body: config.body,
  });

  if (response.status >= 400) {
    throw new Error(`API Error: ${response.status}`);
  }

  return await response.json();
};

// API methods
const SuperTokensAPI = {
  // User profile
  getUserProfile: async () => {
    return apiCall('/api/user/profile', 'GET');
  },

  // Documents
  getDocuments: async () => {
    return apiCall('/api/files', 'GET');
  },

  uploadDocument: async (formData) => {
    // For file uploads, we need to use a different approach
    const response = await fetch(`${getApiDomain()}/api/files`, {
      method: 'POST',
      body: formData,
      // SuperTokens will automatically add auth headers
    });

    if (response.status >= 400) {
      throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
  },

  deleteDocument: async (id) => {
    return apiCall(`/api/files/${id}`, 'DELETE');
  },

  // Search
  searchDocuments: async (query) => {
    return apiCall('/api/search', 'POST', { query });
  },

  // Get usage statistics
  getUsageStats: async () => {
    return apiCall('/api/usage', 'GET');
  }
};

export default SuperTokensAPI;
