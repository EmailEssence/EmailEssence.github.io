import PropTypes from "prop-types";
import { useEffect, useReducer } from "react";
import { Outlet, Route, Routes, useNavigate } from "react-router";
import { fetchNewEmails } from "../../emails/emailHandler";
import "../client/dashboard/client.css";
import Dashboard from "./dashboard/dashboard";
import Inbox from "./inbox/inbox";
import { clientReducer, userPreferencesReducer } from "./reducers";
import { Settings } from "./settings/settings";
import SideBar from "./sidebar/sidebar";

/**
 * Main client component for authenticated user experience.
 * Handles sidebar, routing, user preferences, and periodic email fetching.
 * @param {Object} props
 * @param {Array<Email>} props.emailsByDate - List of emails grouped by date.
 * @param {Object} props.defaultUserPreferences - Default user preferences.
 * @returns {JSX.Element}
 */
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

  /**
   * Sets up an interval to fetch new emails based on user preference.
   * @returns {void}
   */
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

  // Dynamically update sidebar width
  const root = document.querySelector(":root");
  root.style.setProperty(
    "--sidebar-width",
    `calc(${client.expandedSideBar ? "70px + 5vw" : "30px + 2vw"})`
  );

  /** Handles logo click to toggle sidebar expansion. */
  const handleLogoClick = () => {
    dispatchClient({
      type: "logoClick",
      state: client.expandedSideBar,
    });
  };

  /**
   * Handles navigation between client pages.
   * @param {string} pageName - The page route to navigate to.
   */
  const handlePageChange = (pageName) => {
    const toChange = import.meta.env.MODE === "test" ? "/client" : null;
    if (toChange) {
      navigate(pageName.replace(toChange, ""));
    } else {
      navigate(pageName);
    }
  };

  /** Toggles the summaries-in-inbox user preference. */
  const handleToggleSummariesInInbox = () => {
    dispatchUserPreferences({
      type: "isChecked",
      isChecked: userPreferences.isChecked,
    });
  };

  /**
   * Sets the email fetch interval user preference.
   * @param {number} interval - Interval in seconds.
   */
  const handleSetEmailFetchInterval = (interval) => {
    dispatchUserPreferences({
      type: "emailFetchInterval",
      emailFetchInterval: interval,
    });
  };

  /**
   * Sets the theme user preference.
   * @param {string} theme - Theme name ("light", "system", "dark").
   */
  const handleSetTheme = (theme) => {
    dispatchUserPreferences({
      type: "theme",
      theme: theme,
    });
  };

  /**
   * Sets the currently selected email.
   * @param {Email} email - The email object to set as current.
   */
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
          path="home"
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
