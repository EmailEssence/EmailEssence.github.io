import { BrowserRouter, Routes, Route } from "react-router";
import Auth from "./Auth";
import Login from "./components/login/login";
import Loading from "./Loading";
import Client from "./client";
import Error from "./Error";
import { authenticate } from "./authentication/authenticate";
import { emails, userPreferences } from "./emails/emailParse";

function Router() {
  return (
    <BrowserRouter>
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
              emailsByDate={emails}
              defaultUserPreferences={userPreferences}
            />
          }
        />
        <Route path="error" element={<Error />} />
      </Routes>
    </BrowserRouter>
  );
}

export default Router;
