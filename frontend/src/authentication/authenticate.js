import { baseUrl } from "../emails/emailParse";

const parseURL = (url) => {
  const code = "code=";
  const i1 = url.indexOf(code);
  const i2 = url.indexOf("scope=");
  if (i1 === -1 || i2 === -1) {
    return null;
  }
  return url.substring(i1 + code.length, i2 - 1);
};

export const authenticate = async () => {
  console.log("Reached authenticate()");
  // Check for auth hash and render OAuthCallback if present
  try {
    const response = await fetch(
      `${baseUrl}/auth/login?redirect_uri=http://localhost:3000`
    );
    const data = await response.json();
    if (data.authorization_url) {
      window.open(data.authorization_url);
      // window.location.href = data.authorization_url;
    }
  } catch (error) {
    console.error("Login Error", error);
  } finally {
    console.log("user is now logged in");
  }
};

export const handleOAuthCallback = async (handleAuthenticate) => {
  const hash = window.location.hash;
  console.log("in hash function");
  if (hash && hash.startsWith("#auth=")) {
    console.log("In hash hash");
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
  } else if (parseURL(window.location.href) !== "") {
    try {
      const code = parseURL(window.location.href);
      const encodedState = code;
      console.log("encoded State: " + encodedState);
      // const authState = JSON.parse(decodeURIComponent(encodedState));
      // if (authState.authenticated && authState.token) {
      //   // Token is already verified by backend
      //   handleAuthenticate(authState.token);
      //   window.location.hash = "";
      //   return;
      // }
    } catch (error) {
      console.error("Error parsing auth state:", error);
    }
  }
};
