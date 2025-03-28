import { useEffect, useState } from "react";
import {
  authenticate,
  handleOAuthCallback,
  checkAuthStatus,
} from "./authentication/authenticate";
import Client from "./client";
import { Login } from "./components/login/login";
import { fetchUserPreferences } from "./components/settings/settings";
import fetchEmails from "./emails/emailParse";

const userAlreadyLoggedIn = () => !!localStorage.getItem("auth_token");

export default function Page() {
  const [loading, setLoading] = useState(false);
  const [calledAuth, setCalledAuth] = useState(false);
  const [loggedIn, setLoggedIn] = useState(userAlreadyLoggedIn);

  const [emailsByDate, setEmailsByDate] = useState(null);
  const [defaultUserPreferences, setDefaultUserPreferences] = useState({
    isChecked: true,
    emailFetchInterval: 120,
    theme: "light",
  });

  useEffect(() => {
    if (calledAuth && loggedIn) {
      const intervalId = setInterval(() => {
        try {
          checkAuthStatus(localStorage.getItem("auth_token"));
          console.log("sending auth");
        } catch (e) {
          console.log(e);
        }
      }, 60000);
      return () => clearInterval(intervalId);
    } else {
      if (loggedIn) {
        handleAuthenticate(localStorage.getItem("auth_token"));
      } else {
        const hash = window.location.hash;
        if (hash && hash.startsWith("#auth=")) {
          handleOAuthCallback(handleAuthenticate);
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loggedIn, loading]);

  const handleAuthenticate = async (token) => {
    try {
      setCalledAuth(true);
      setLoading(true);
      // Persist token
      localStorage.setItem("auth_token", token);
      retrieveUserData();
      setLoggedIn(true);
    } catch (error) {
      handleAuthError(error);
      setLoggedIn(false);
      setCalledAuth(false); // Reattempt auth
    } finally {
      setLoading(false);
    }
  };

  const retrieveUserData = async () => {
    try {
      const user_id = null; // Get user ID
      const emails = await fetchEmails(100);
      if (!Array.isArray(emails)) {
        throw new Error("Invalid email response format");
      }
      const emailArray = Array.isArray(emails) ? emails : [];
      setEmailsByDate(emailArray);
      if (user_id) getUserPreferences(user_id);
    } catch (error) {
      handleAuthError(error);
    }
  };

  // Get user preferences from the server and set the default user preferences state
  const getUserPreferences = async (user_id) => {
    try {
      const preferences = await fetchUserPreferences(user_id);
      setDefaultUserPreferences(preferences);
    } catch (error) {
      console.error(error);
    }
  };

  const handleAuthError = (error) => {
    console.error("Auth flow error:", error);
    // Clear invalid token
    localStorage.removeItem("auth_token");
    setEmailsByDate([]);
  };

  const display = () => {
    return loading ? (
      <div>Loading emails...</div>
    ) : !loggedIn ? (
      <Login handleGoogleClick={authenticate} />
    ) : emailsByDate === null ? (
      <div>Initializing dashboard...</div>
    ) : (
      <Client
        emailsByDate={emailsByDate}
        setEmailsByDate={setEmailsByDate}
        defaultUserPreferences={defaultUserPreferences}
      />
    );
  };
  return <div className="page">{display()}</div>;
}
