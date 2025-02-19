/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */
import { useEffect } from "react";
import { baseUrl } from "../../emails/emailParse";
import styles from "./login.module.css";

export const OAuthCallback = (forward, code) => {
  useEffect(() => {
    const handleCallback = async () => {
      if (code) {
        try {
          // Exchange code for token
          const response = await fetch(`${baseUrl}/auth/callback?code=${code}`);
          // const data = await response.json();

          // Check auth status
          const statusResponse = await fetch(`${baseUrl}/auth/status`);
          const statusData = await statusResponse.json();
          if (statusData.is_authenticated) {
            // :)
            forward();
          } else {
            console.error("Authentication failed");
          }
        } catch (error) {
          console.error("Auth callback Error", error);
        }
      } else {
        console.error("No code found in URL");
      }
    };
    handleCallback();
  }, [forward, code]);

  return <div>Completing sign in...</div>;
};

export const Login = ({ forward }) => {
  const handleLogin = async () => {
    try {
      const response = await fetch(`${baseUrl}/auth/login`);
      const data = await response.json();
      if (data.authorization_url) {
        window.location.href = data.authorization_url;
        //https://ee-backend-w86t.onrender.com/auth/callback?state=3kcnwylQpcgVHUziNLC6rDcYcPyoRB&code=4%2F0ASVgi3JA0nLePkt6ii6OtB4_P1O9TlnwPNbd_-0ZDs7DSGGPH0TpCL1EOIHlZcxS9bzIYQ&scope=https%3A%2F%2Fmail.google.com%2F
      }
    } catch (error) {
      console.error("Login Error", error);
    }
  };

  const params = new URLSearchParams(window.location.search);
  const code = params.get("code");

  if (code) {
    return <OAuthCallback forward={forward} code={code} />;
  }

  return (
    <div className={styles.page} data-testid="page">
      <div className={styles.formBox} data-testid="formBox">
        <div className={styles.loginDiv} data-testid="loginDiv">
          <div className={styles.loginIcon} data-testid="loginIcon">
            <img
              src="./src/assets/Logo.svg"
              alt="Login Icon"
              className={styles.loginPhoto}
              data-testid="loginPhoto"
            />
          </div>
          <p className={styles.title} data-testid="title">Welcome Back</p>
          <button
            onClick={handleLogin || defaultHandleLogin}
            className={styles.googleButton}
            data-testid="googleButton"
          >
            Login with Google
          </button>
        </div>
      </div>
    </div>
  );
}
