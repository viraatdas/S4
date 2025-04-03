# S4 Authentication with SuperTokens

This document explains how to set up and use Google authentication in S4 using SuperTokens.

## Overview

S4 now supports two authentication methods:
1. **API Key Authentication** (original method)
2. **Google OAuth Authentication** (new method using SuperTokens)

The system is designed to support both methods simultaneously, allowing for a smooth transition from API keys to OAuth.

## Setup Instructions

### 1. Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" and select "OAuth client ID"
5. Select "Web application" as the application type
6. Add the following authorized redirect URI:
   - `http://localhost:3000/auth/callback/google` (for local development)
   - `https://your-production-domain.com/auth/callback/google` (for production)
7. Note your Client ID and Client Secret

### 2. Environment Configuration

Update your `.env` file with the following variables:

```
# SuperTokens Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SUPERTOKENS_CONNECTION_URI=https://try.supertokens.io
API_DOMAIN=http://localhost:8000
WEBSITE_DOMAIN=http://localhost:3000
```

For production, you should set up your own SuperTokens Core instance instead of using `try.supertokens.io`. See the [SuperTokens documentation](https://supertokens.com/docs/thirdparty/introduction) for more details.

### 3. Running the Application

Start the backend:
```bash
cd /path/to/S4
python -m s4
```

Start the frontend:
```bash
cd /path/to/S4/s4-ui
npm start
```

## Authentication Flow

1. Users can access the login page at `/auth` (SuperTokens pre-built UI)
2. After successful Google authentication, users will be redirected to the dashboard
3. The system will automatically create a tenant for new users based on their email address
4. All API requests will include the session token automatically

## API Usage

The backend now supports both authentication methods:

1. **SuperTokens Session**: Automatically handled by the frontend SDK
2. **API Key**: Include the `X-API-Key` header in your requests

Example API request with SuperTokens session (handled automatically by the frontend):
```javascript
// Using the SuperTokens API client
import SuperTokensAPI from './services/supertokens-api';

// This will automatically include the session token
const documents = await SuperTokensAPI.getDocuments();
```

Example API request with API key (legacy method):
```javascript
// Using the original API client
import API from './services/api';

// This will include the API key from localStorage
const documents = await API.getDocuments();
```

## Security Considerations

1. Always use HTTPS in production
2. Set appropriate CORS origins in your `.env` file
3. Regularly rotate API keys for legacy authentication
4. Consider implementing additional security measures like rate limiting

## Troubleshooting

- If you encounter CORS issues, ensure your `S4_CORS_ORIGINS` environment variable is set correctly
- For authentication problems, check the browser console and server logs
- Verify that your Google OAuth credentials are correct and the redirect URIs are properly configured

For more information, refer to the [SuperTokens documentation](https://supertokens.com/docs/thirdparty/introduction).
