import { useEffect, useState } from "react";
import {
  authenticate,
  handleOAuthCallback,
  checkAuthStatus,
  parseURL,
} from "./authentication/authenticate";
import Client from "./client";
import { Login } from "./components/login/login";
import { fetchUserPreferences } from "./components/settings/settings";
import fetchEmails, { fetchDev, isDevMode } from "./emails/emailParse";

const devEmails = isDevMode ? fetchDev() : [];

export default function Page() {
  const [emailsByDate, setEmailsByDate] = useState(
    isDevMode ? devEmails : null
  );
  const [loading, setLoading] = useState(false);

  const [loggedIn, setLoggedIn] = useState(
    () => !!localStorage.getItem("auth_token")
  );
  // eslint-disable-next-line no-unused-vars
  const [authChanged, setAuthChanged] = useState(false);
  const [defaultUserPreferences, setDefaultUserPreferences] = useState({
    isChecked: true,
    emailFetchInterval: 120,
    theme: "light",
  });

  useEffect(() => {
    const intervalId = setInterval(() => {
      if (!loggedIn) {
        const hash = window.location.hash;
        if (hash && hash.startsWith("#auth=")) {
          handleOAuthCallback(handleAuthenticate);
        } else if (parseURL(window.location.href) !== "") {
          handleOAuthCallback(handleAuthenticate);
        }
      } else {
        try {
          checkAuthStatus(localStorage.getItem("auth_token"));
        } catch (e) {
          console.log(e);
        }
      }
    }, 1000);
    return () => clearInterval(intervalId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loggedIn]); // In array put State/Variable that will update once user is logged in

  const handleAuthenticate = async (token) => {
    try {
      setLoading(true);
      // Persist token
      localStorage.setItem("auth_token", token);
      setLoggedIn(true);
      retrieveUserData();
      setAuthChanged(true); // Update authChanged state
    } catch (error) {
      handleAuthError(error);
      setLoggedIn(false);
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
    setAuthChanged(true); // Update authChanged state
  };

  const display = () => {
    return isDevMode ? (
      <Client
        emailsByDate={emailsByDate}
        defaultUserPreferences={defaultUserPreferences}
      />
    ) : loading ? (
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
