import { BrowserRouter, Routes, Route, useLocation } from "react-router";
import Auth from "./Auth";
import Login from "./components/login/login";
import Loading from "./Loading";
import Client from "./client";
import Error from "./Error";
import { authenticate } from "./authentication/authenticate";
import { emails, userPreferences } from "./emails/emailParse";
import { useState, useEffect } from "react";

function Router() {
  return (
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  );
}

function AppRouter() {
  const [userEmails, setUserEmails] = useState(emails);
  const location = useLocation();
  useEffect(() => {
    if (userEmails.length < emails.length) setUserEmails(emails);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]);

  return (
    <Routes>
      <Route path="/" element={<Auth />}>
        <Route
          path="login"
          element={<Login handleGoogleClick={authenticate} />}
        />
        <Route path="loading" element={<Loading />} />
      </Route>
      <Route
        path="client/*"
        element={
          <Client
            emailsByDate={userEmails}
            defaultUserPreferences={userPreferences}
          />
        }
      />
      <Route path="error" element={<Error />} />
    </Routes>
  );
}

export default Router;
