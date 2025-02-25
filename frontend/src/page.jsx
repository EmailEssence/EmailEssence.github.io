/* eslint-disable no-unused-vars */
import { useState } from "react";
// import { markEmailAsRead } from "./emails/emailHandler";
import { Login } from "./components/login/login";
import Client from "./client";
import fetchEmails from "./emails/emailParse";

export default function Page() {
  const [emailsByDate, setEmailsByDate] = useState(null);
  const [loading, setLoading] = useState(false);

  const [loggedIn, setLoggedIn] = useState(() => {
    const savedToken = localStorage.getItem("auth_token");
    return !!savedToken;
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem("auth_token");
  });

  const handleLogin = async (token) => {
    try {
      setLoading(true);
      // Persist token
      localStorage.setItem("auth_token", token);
      setToken(token);

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

  const loginPage = () => {
    return (
      <Login
        forward={handleLogin}
        // onSignUpClick={() => setCurPage("register")}
      />
    );
  };

  const display = () => {
    return loading ? (
      <div>Loading emails...</div>
    ) : !loggedIn ? (
      loginPage()
    ) : emailsByDate === null ? ( // Does not initialize dashboard if user has no emails
      <div>Initializing dashboard...</div>
    ) : (
      Client(emailsByDate)
    );
  };

  return <div className="page">{display()}</div>;
}
