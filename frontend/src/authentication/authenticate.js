import { baseUrl, retrieveUserData } from "../emails/emailParse";
export const authenticate = async () => {
  // Check for auth hash and render OAuthCallback if present
  try {
    const redirect_uri = `${window.location.origin}/loading`;
    window.location.href = `${baseUrl}/auth/login?redirect_uri=${redirect_uri}`;
  } catch (error) {
    console.error("Login Error", error);
  }
};

// When Reach loading component call this function
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
      window.location.hash = "";
      return;
    } catch (error) {
      console.error("Error parsing auth state:", error);
      handleAuthError(error);
    }
  }
};

export const handleAuthenticate = async (token) => {
  try {
    localStorage.setItem("auth_token", token);
    await retrieveUserData();
  } catch (error) {
    handleAuthError(error);
  }
};

const handleAuthError = async (error) => {
  console.error("Auth flow error:", error);
  localStorage.removeItem("auth_token");
  window.location.href = "/error"; // go to error page
};

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
