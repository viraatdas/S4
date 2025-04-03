import SuperTokens from "supertokens-auth-react";
import ThirdPartyAuth from "supertokens-auth-react/recipe/thirdparty";
import Session from "supertokens-auth-react/recipe/session";
import { ThirdPartyPreBuiltUI } from "supertokens-auth-react/recipe/thirdparty/prebuiltui";

const API_DOMAIN = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WEBSITE_DOMAIN = process.env.REACT_APP_WEBSITE_DOMAIN || 'http://localhost:3000';

// SuperTokens connection URI and credentials from environment variables
const SUPERTOKENS_CONNECTION_URI = process.env.REACT_APP_SUPERTOKENS_CONNECTION_URI || 'http://localhost:3567';
const SUPERTOKENS_API_KEY = process.env.REACT_APP_SUPERTOKENS_API_KEY || '';
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '';
const GOOGLE_CLIENT_SECRET = process.env.REACT_APP_GOOGLE_CLIENT_SECRET || '';

// For debugging
const logEvents = true;

export const initSuperTokens = () => {
  SuperTokens.init({
    appInfo: {
      appName: "S4 - Smart S3 Storage Service",
      apiDomain: API_DOMAIN,
      websiteDomain: WEBSITE_DOMAIN,
      apiBasePath: "/auth",
      websiteBasePath: "/auth"
    },
    recipeList: [
      ThirdPartyAuth.init({
        signInAndUpFeature: {
          providers: [
            ThirdPartyAuth.Google.init({
              clientId: GOOGLE_CLIENT_ID,
              clientSecret: GOOGLE_CLIENT_SECRET,
              scope: ["openid", "profile", "email"],
              authorisationRedirect: {
                params: {
                  prompt: "consent",
                  access_type: "offline",
                  include_granted_scopes: "true"
                }
              }
            })
          ],
          // Customize the sign-in/sign-up form
          style: {
            button: {
              backgroundColor: "#4285F4",
              borderColor: "#4285F4"
            }
          }
        },
        onHandleEvent: (context) => {
          // Log events for debugging
          if (logEvents) {
            console.log("SuperTokens event:", context.action, context);
          }
          
          if (context.action === "SUCCESS") {
            // Store token and user info in localStorage for our custom flow
            if (context.user) {
              const token = `st-${context.user.id}-${Date.now()}`;
              localStorage.setItem('token', token);
              localStorage.setItem('email', context.user.email);
              console.log('Stored authentication data in localStorage:', {
                token: token.substring(0, 10) + '...',
                email: context.user.email
              });
              
              // Store admin status if applicable
              if (context.user.isAdmin) {
                localStorage.setItem('adminKey', 'true');
              }
            }
            
            // Redirect to dashboard on successful authentication
            window.location.href = "/dashboard";
          } else if (context.action === "SIGN_IN_AND_UP_ERROR") {
            console.error("Auth error:", context.error);
          }
        }
      }),
      Session.init({
        tokenTransferMethod: "header",
        sessionExpiredStatusCode: 401,
        autoAddCredentials: true,
        onHandleEvent: (context) => {
          if (logEvents) {
            console.log("Session event:", context.action, context);
          }
        }
      })
    ],
    connectionURI: SUPERTOKENS_CONNECTION_URI,
    apiKey: SUPERTOKENS_API_KEY,
    // Add redirection URL configuration
    getRedirectionURL: async (context) => {
      if (logEvents) {
        console.log("Redirection context:", context);
      }
      
      if (context.action === "SUCCESS") {
        // Always redirect to dashboard after successful authentication
        return "/dashboard";
      }
      return undefined;
    }
  });
};

// Export the prebuilt UI components for use in routing
export const SuperTokensUIComponents = {
  ThirdPartyPreBuiltUI
};

// Export the session verification function for protected routes
export const sessionVerificationFunction = Session.doesSessionExist;
