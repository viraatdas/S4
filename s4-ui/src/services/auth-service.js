/**
 * Authentication service for S4
 * This service handles authentication with SuperTokens
 */

import Session from "supertokens-auth-react/recipe/session";

/**
 * Check if the user is authenticated with SuperTokens
 * @returns {Promise<boolean>} True if the user is authenticated
 */
export const isAuthenticated = async () => {
  try {
    return await Session.doesSessionExist();
  } catch (error) {
    console.error("Error checking authentication status:", error);
    return false;
  }
};

/**
 * Get the current user's information from SuperTokens
 * @returns {Promise<Object|null>} User information or null if not authenticated
 */
export const getCurrentUser = async () => {
  try {
    if (await isAuthenticated()) {
      const session = await Session.getAccessTokenPayloadSecurely();
      return session.sub;
    }
    return null;
  } catch (error) {
    console.error("Error getting current user:", error);
    return null;
  }
};

/**
 * Sign out the current user
 * @returns {Promise<void>}
 */
export const signOut = async () => {
  try {
    await Session.signOut();
    window.location.href = "/";
  } catch (error) {
    console.error("Error signing out:", error);
  }
};

/**
 * Get the current session token
 * @returns {Promise<string|null>} Session token or null if not authenticated
 */
export const getSessionToken = async () => {
  try {
    if (await isAuthenticated()) {
      return await Session.getAccessToken();
    }
    return null;
  } catch (error) {
    console.error("Error getting session token:", error);
    return null;
  }
};
