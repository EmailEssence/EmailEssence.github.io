import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import { authenticate } from "../../authentication/authenticate";
import Client from "../client/client";
import Contact from "../login/contact";
import Error from "../login/Error";
import Home from "../login/Home";
import Login from "../login/login";
import PrivacyPolicy from "../login/privacy";
import TermsOfService from "../login/terms";
import AuthLoading from "../login/AuthLoading";

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
  return (
    <Routes>
      <Route path="" element={<Navigate to="/home" replace />} />
      <Route path="/home" element={<Home />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/privacy" element={<PrivacyPolicy />} />
      <Route path="/terms" element={<TermsOfService />} />
      <Route path="/loading" element={<AuthLoading />} />
      <Route
        path="/login"
        element={<Login handleGoogleClick={authenticate} />}
      />
      <Route path="client/*" element={<Client />} />
      <Route path="/error" element={<Error />} />
    </Routes>
  );
}

export default Router;
