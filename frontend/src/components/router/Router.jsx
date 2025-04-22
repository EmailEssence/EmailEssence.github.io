import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router";
import { authenticate } from "../../authentication/authenticate";
import { emails, userPreferences } from "../../emails/emailParse";
import Client from "../client/client";
import Login from "../login/login";
import Error from "../login/Error";
import Loading from "../login/Loading";

function Router() {
  return (
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  );
}

export function AppRouter() {
  const [userEmails, setUserEmails] = useState(emails);
  const location = useLocation();
  useEffect(() => {
    if (location.hash.includes("#newEmails")) {
      if (userEmails.length < emails.length) setUserEmails(emails);
      window.history.replaceState(
        null,
        "",
        window.location.pathname + window.location.search
      ); // Remove the hash
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.hash]);

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
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
