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
  } else if (parseURL(window.location.href) !== "") {
    try {
      const encodedState = parseURL(window.location.href);
      if (!containsEncodedComponents(encodedState)) {
        throw new Error("Wrong State");
      }
      const unencoded = decodeURIComponent(encodedState); //unrecognized: (%), (/)
      const authState = JSON.parse(unencoded);
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

function containsEncodedComponents(x) {
  // ie ?,=,&,/ etc
  return decodeURI(x) !== decodeURIComponent(x);
}
//localhost:3000/auth/callback?state=eyJyZWRpcmVjdF91cmkiOiAiaHR0cDovL2xvY2FsaG9zdDozMDAwIiwgIm5vbmNlIjogImVhZTIwMjY2LWY0NjQtNDNjMi04NjY4LTcwMDljMGEwYjRlZSJ9&code=4/0AQSTgQEI2xz3ik8iEsE4GvWonHueX_ZDIUc8CEbtbh7aDTMaT3MkFMJxQwSL89ztSzWP9g&scope=email%20profile%20https://mail.google.com/%20openid%20https://www.googleapis.com/auth/userinfo.profile%20https://www.googleapis.com/auth/userinfo.email&authuser=1&prompt=consent
//localhost:3000/auth/callback?state=eyJyZWRpcmVjdF91cmkiOiAiaHR0cDovL2xvY2FsaG9zdDozMDAwIiwgIm5vbmNlIjogIjM5MGVkZTZhLTVmNjMtNGQyYi04OWQwLWJjNjMwNDlhOWY1MyJ9&code=4%2F0AQSTgQGNmXUrk2Bzczx7ws3cpU-57UyfgGthRb_q708oqAyjx_IRUq6f8Nwf34RMpv6sDw&scope=email+profile+openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fmail.google.com%2F+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email&authuser=1&prompt=none#
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
