import PropTypes from "prop-types";
import { useEffect, useReducer } from "react";
import { Outlet, Route, Routes, useNavigate } from "react-router";
import { fetchNewEmails } from "../../emails/emailParse";
import "./client.css";
import Dashboard from "./dashboard/dashboard";
import Inbox from "./inbox/inbox";
import { clientReducer, userPreferencesReducer } from "./reducers";
import { Settings } from "./settings/settings";
import SideBar from "./sidebar/sidebar";

function Client({
  emailsByDate,
  defaultUserPreferences = {
    isChecked: true,
    emailFetchInterval: 120,
    theme: "light",
  },
}) {
  const navigate = useNavigate();
  const [client, dispatchClient] = useReducer(clientReducer, {
    expandedSideBar: false,
    curEmail: emailsByDate[0],
  });
  const [userPreferences, dispatchUserPreferences] = useReducer(
    userPreferencesReducer,
    defaultUserPreferences
  );

  useEffect(() => {
    const clock = setInterval(async () => {
      try {
        await fetchNewEmails();
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
    navigate(pageName);
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

  const handleSetCurEmail = (email) => {
    dispatchClient({
      type: "emailChange",
      email: email,
    });
  };

  return (
    <div className="client">
      <SideBar
        onLogoClick={handleLogoClick}
        expanded={client.expandedSideBar}
        handlePageChange={handlePageChange}
      />
      <Routes>
        <Route
          path="dashboard"
          element={
            <Dashboard
              emailList={emailsByDate}
              handlePageChange={handlePageChange}
              setCurEmail={handleSetCurEmail}
            />
          }
        />
        <Route
          path="inbox"
          element={
            <Inbox
              displaySummaries={userPreferences.isChecked}
              emailList={emailsByDate}
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
      </Routes>
      <Outlet />
    </div>
  );
}

Client.propTypes = {
  emailsByDate: PropTypes.array,
  defaultUserPreferences: PropTypes.object,
};

export default Client;
