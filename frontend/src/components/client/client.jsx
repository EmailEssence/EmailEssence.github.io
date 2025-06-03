import { useEffect, useReducer } from "react";
import { Outlet, Route, Routes, useNavigate } from "react-router";
import { fetchNewEmails } from "../../emails/emailHandler";
import "./client.css";
import Dashboard from "./dashboard/dashboard";
import Inbox from "./inbox/inbox";
import { clientReducer, userPreferencesReducer } from "./reducers";
import { Settings } from "./settings/settings";
import SideBar from "./sidebar/sidebar";
import Loading from "../login/Loading";

function Client() {
  const navigate = useNavigate();
  const [client, dispatchClient] = useReducer(clientReducer, {
    expandedSideBar: false,
    emails: [],
    curEmail: {},
  });
  const [userPreferences, dispatchUserPreferences] = useReducer(
    userPreferencesReducer,
    { isChecked: true, emailFetchInterval: 120, theme: "light" }
  );

  useEffect(() => {
    const clock = setInterval(async () => {
      try {
        const newEmails = await fetchNewEmails();
        // TODO: Do something with new emails
      } catch (error) {
        console.error(`Loading Emails Error: ${error}`);
      }
    }, userPreferences.emailFetchInterval * 1000);
    return () => clearInterval(clock);
  }, [userPreferences.emailFetchInterval]);

  const root = document.querySelector(":root");
  root.style.setProperty(
    "--sidebar-width",
    `calc(${client.expandedSideBar ? "70px + 5vw" : "30px + 2vw"})`
  );

  const handleLogoClick = () => {
    dispatchClient({
      type: "logoClick",
      state: client.expandedSideBar,
    });
  };

  const handlePageChange = (pageName) => {
    const toChange = import.meta.env.MODE === "test" ? "/client" : null;
    if (toChange) {
      navigate(pageName.replace(toChange, ""));
    } else {
      navigate(pageName);
    }
  };

  const handleToggleSummariesInInbox = () => {
    dispatchUserPreferences({
      type: "isChecked",
      isChecked: userPreferences.isChecked,
    });
  };

  const handleSetEmailFetchInterval = (interval) => {
    dispatchUserPreferences({
      type: "emailFetchInterval",
      emailFetchInterval: interval,
    });
  };

  const handleSetTheme = (theme) => {
    dispatchUserPreferences({
      type: "theme",
      theme: theme,
    });
  };
  const handleAddEmails = (emailsToAdd, addToFront = false) => {
    if (addToFront) {
      // add emails to the Front
      dispatchClient({
        type: "emailAdd",
        email: [...emailsToAdd, ...client.emails],
      });
    } else {
      // add emails to the back
      dispatchClient({
        type: "emailAdd",
        email: [...client.emails, ...emailsToAdd],
      });
    }
  };

  const handleSetCurEmail = (email) => {
    dispatchClient({
      type: "emailChange",
      email: email,
    });
  };

  return (
    <>
      <Routes>
        <Route
          path="loading"
          element={<Loading setInitialEmails={handleAddEmails} />}
        />
        <Route
          path="*"
          element={
            <div className="client">
              <SideBar
                onLogoClick={handleLogoClick}
                expanded={client.expandedSideBar}
                handlePageChange={handlePageChange}
              />
              <Outlet />
            </div>
          }
        >
          <Route
            path="inbox"
            element={
              <Inbox
                displaySummaries={userPreferences.isChecked}
                emailList={client.emails}
                setCurEmail={handleSetCurEmail}
                curEmail={client.curEmail}
              />
            }
          />
          <Route
            path="settings"
            element={
              <Settings
                isChecked={userPreferences.isChecked}
                handleToggleSummariesInInbox={handleToggleSummariesInInbox}
                emailFetchInterval={userPreferences.emailFetchInterval}
                handleSetEmailFetchInterval={handleSetEmailFetchInterval}
                theme={userPreferences.theme}
                handleSetTheme={handleSetTheme}
              />
            }
          />
          <Route
            path="home"
            element={
              <Dashboard
                emailList={client.emails}
                handlePageChange={handlePageChange}
                setCurEmail={handleSetCurEmail}
              />
            }
          />
        </Route>
      </Routes>
    </>
  );
}

export default Client;
