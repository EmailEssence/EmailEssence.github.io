import { useState, useEffect } from "react";
// import { markEmailAsRead } from "./emails/emailHandler";
import { Login } from "./components/login/login";
import Client from "./client";
import fetchEmails from "./emails/emailParse";
import {
  handleOAuthCallback,
  authenticate,
} from "./authentication/authenticate";

export default function Page() {
  const [emailsByDate, setEmailsByDate] = useState(null);
  const [loading, setLoading] = useState(false);

  const [loggedIn, setLoggedIn] = useState(
    () => !!localStorage.getItem("auth_token")
  );

  useEffect(() => {
    const hash = window.location.hash;
    if (hash && hash.startsWith("#auth=")) {
      handleOAuthCallback(handleAuthenticate);
    }
  }, []); // In array put State/Variable that will update once user is logged in

  const handleAuthenticate = async (token) => {
    try {
      setLoading(true);
      // Persist token
      localStorage.setItem("auth_token", token);

      const emails = await fetchEmails();
      if (!Array.isArray(emails)) {
        throw new Error("Invalid email response format");
      }
      const emailArray = Array.isArray(emails) ? emails : [];

      setEmailsByDate(emailArray);
      setLoggedIn(true);
    } catch (error) {
      console.error("Auth flow error:", error);
      // Clear invalid token
      localStorage.removeItem("auth_token");
      setEmailsByDate([]);
    } finally {
      setLoading(false);
    }
  };

  const display = () => {
    return loading ? (
      <div>Loading emails...</div>
    ) : !loggedIn ? (
      <Login handleGoogleClick={async () => authenticate} />
    ) : emailsByDate === null ? (
      <div>Initializing dashboard...</div>
    ) : (
      <Client emailsByDate={emailsByDate} />
    );
  };

  return <div className="page">{display()}</div>;
}
