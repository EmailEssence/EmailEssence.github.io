import { baseUrl } from "../emails/emailParse";

export const parseURL = (url) => {
  const code = "code=";
  const i1 = url.indexOf(code);
  const i2 = url.indexOf("scope=");
  if (i1 === -1 || i2 === -1) {
    return null;
  }
  return url.substring(i1 + code.length, i2 - 1);
};

export const authenticate = async () => {
  // Check for auth hash and render OAuthCallback if present
  try {
    const redirect_uri = window.location.origin;
    window.location.href = `${baseUrl}/auth/login?redirect_uri=${redirect_uri}`;
  } catch (error) {
    console.error("Login Error", error);
  }
};

export const handleOAuthCallback = async (handleAuthenticate) => {
  console.log(window.location.hash);
  const hash = window.location.hash;
  if (hash && hash.startsWith("#auth=")) {
    try {
      const encodedState = hash.substring(6);
      const authState = JSON.parse(decodeURIComponent(encodedState));

      if (authState.authenticated && authState.token) {
        const isAuthenticated = checkAuthStatus(authState.token);
        if (isAuthenticated) {
          handleAuthenticate(authState.token);
        } else {
          console.log("not authenticated");
        }
      }
      window.location.hash = "";
      return;
    } catch (error) {
      console.error("Error parsing auth state:", error);
    }
  }
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
