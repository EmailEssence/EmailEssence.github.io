import { baseUrl, retrieveUserData } from "../emails/emailHandler";

/**
 * Initiates the OAuth authentication flow by redirecting to the backend login endpoint.
 * Sets the redirect URI to the /loading route.
 * @async
 * @returns {void}
 */
export const authenticate = async () => {
  // Check for auth hash and render OAuthCallback if present
  const redirect_uri = `${window.location.origin}/loading`;
  window.location.href = `${baseUrl}/auth/login?redirect_uri=${redirect_uri}`;
};

/**
 * Handles the OAuth callback after authentication.
 * Parses the auth state from the URL hash, verifies authentication, and stores the token.
 * Navigates to the error page if authentication fails.
 * @async
 * @returns {Promise<void>}
 */
export const handleOAuthCallback = async () => {
  const hash = window.location.hash;
  if (hash && hash.startsWith("#auth=")) {
    try {
      const encodedState = hash.substring(6);
      const authState = JSON.parse(decodeURIComponent(encodedState));

      if (authState.authenticated && authState.token) {
        const isAuthenticated = checkAuthStatus(authState.token);
        if (isAuthenticated) {
          await handleAuthenticate(authState.token);
        } else {
          handleAuthError("Unable to authenticate");
        }
      }
      return;
    } catch (error) {
      window.location.hash = "";
      console.error("Error parsing auth state:", error);
      handleAuthError(error);
    }
  }
};

/**
 * Stores the authentication token and retrieves user data.
 * Navigates to the error page if authentication fails.
 * @async
 * @param {string} token - The authentication token.
 * @returns {Promise<void>}
 */
export const handleAuthenticate = async (token) => {
  try {
    localStorage.setItem("auth_token", token);
    await retrieveUserData();
  } catch (error) {
    handleAuthError(error);
  }
};


/**
 * Handles authentication errors by logging out, storing the error message,
 * and redirecting to the error page.
 * @async
 * @param {Error|string} error - The error object or message.
 * @returns {Promise<void>}
 */
const handleAuthError = async (error) => {
  console.error("Auth flow error:", error);
  localStorage.removeItem("auth_token");
  localStorage.setItem("error_message", error.message); // Store error message in local storage
  window.location.href = "/error"; // go to error page
};

/**
 * Checks the authentication status of the provided token by querying the backend.
 * @async
 * @param {string} token - The authentication token.
 * @returns {Promise<boolean>} True if authenticated, false otherwise.
 */
export const checkAuthStatus = async (token) => {
  const option = {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  };
  const req = new Request(`${baseUrl}/auth/status`, option);
  const statusResponse = await fetch(req);
  const statusData = await statusResponse.json();
  return statusData.is_authenticated;
};
