import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router";
import { authenticate } from "../../authentication/authenticate";
import { emails, userPreferences } from "../../emails/emailHandler";
import Client from "../client/client";
import Contact from "../login/contact";
import Error from "../login/Error";
import Home from "../login/Home";
import Loading from "../login/Loading";
import Login from "../login/login";
import PrivacyPolicy from "../login/privacy";
import TermsOfService from "../login/terms";

/**
 * Main Router component for the application.
 * Wraps AppRouter in BrowserRouter for test environments.
 * @returns {JSX.Element}
 */
export function Router() {
  const testing = import.meta.env.MODE === "test";
  if (testing) {
    return (
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    );
  }
  return <AppRouter />;
}

/**
 * Defines routes and manages user email state for client routes.
 * Updates userEmails state when the global emails array changes or when #newEmails is in the URL hash.
 * @returns {JSX.Element}
 */
export function AppRouter() {
  const [userEmails, setUserEmails] = useState(emails);
  const location = useLocation();
  useEffect(() => {
    const interval = setInterval(() => {
      if (emails != userEmails || window.location.hash === "#newEmails") {
        setUserEmails(emails);
        window.history.replaceState(
          null,
          "",
          window.location.pathname + window.location.search
        ); // Remove the hash
      }
    }, 500);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]);

  return (
    <Routes>
      <Route path="" element={<Navigate to="/home" replace />} />
      <Route path="/home" element={<Home />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/privacy" element={<PrivacyPolicy />} />
      <Route path="/terms" element={<TermsOfService />} />
      <Route
        path="/login"
        element={<Login handleGoogleClick={authenticate} />}
      />
      <Route path="/loading" element={<Loading />} />
      <Route
        path="client/*"
        // userEmails.length being more than 0 ensures that curEmail is not undefined when client is rendered
        element={
          userEmails.length > 0 && (
            <Client
              emailsByDate={userEmails}
              defaultUserPreferences={userPreferences}
            />
          )
        }
      />
      <Route path="/error" element={<Error />} />
    </Routes>
  );
}

export default Router;
