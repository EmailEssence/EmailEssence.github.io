import { baseUrl } from "../emails/emailParse";

export const authenticate = async () => {
  // Check for auth hash and render OAuthCallback if present
  try {
    const response = await fetch(`${baseUrl}/auth/login`);
    const data = await response.json();
    if (data.authorization_url) {
      window.location.href = data.authorization_url;
    }
  } catch (error) {
    console.error("Login Error", error);
  } finally {
    console.log("user is now logged in");
  }
};

export const handleOAuthCallback = async (handleAuthenticate) => {
  const hash = window.location.hash;
  if (hash && hash.startsWith("#auth=")) {
    try {
      const encodedState = hash.substring(6);
      const authState = JSON.parse(decodeURIComponent(encodedState));

      if (authState.authenticated && authState.token) {
        // Token is already verified by backend
        handleAuthenticate(authState.token);
        window.location.hash = "";
        return;
      }
    } catch (error) {
      console.error("Error parsing auth state:", error);
    }
  }
};
