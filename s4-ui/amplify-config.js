// Configuration for AWS Amplify deployment
// This file will be used during the build process

const config = {
  // Backend API URL will be updated during deployment
  apiUrl: process.env.REACT_APP_API_URL || 'BACKEND_URL_PLACEHOLDER',
  
  // SuperTokens configuration
  supertokens: {
    connectionUri: process.env.REACT_APP_SUPERTOKENS_CONNECTION_URI || 'https://st-dev-7fccbc80-101f-11f0-8dcf-2382362cfcad.aws.supertokens.io',
    apiKey: process.env.REACT_APP_SUPERTOKENS_API_KEY || 'q2sB3jUZAL2Ceju85rWQNyZerJ'
  },
  
  // Google OAuth configuration
  google: {
    clientId: process.env.REACT_APP_GOOGLE_CLIENT_ID || '952024236906-skd03vg8rbrlg8gbcb7h8nafqhgpmk6a.apps.googleusercontent.com'
  }
};

export default config;
