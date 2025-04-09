import { useEffect, useReducer } from "react";
import "./client.css";
import Dashboard from "./components/dashboard/dashboard";
import Inbox from "./components/inbox/inbox";
import { Settings } from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
import { fetchNewEmails } from "./emails/emailParse";
import PropTypes from "prop-types";
import { clientReducer, userPreferencesReducer } from "./reducers";

function Client({
  emailsByDate,
  defaultUserPreferences = {
    isChecked: true,
    emailFetchInterval: 120,
    theme: "light",
  },
}) {
  const [client, dispatchClient] = useReducer(clientReducer, {
    curPage: "dashboard",
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
    dispatchClient({
      type: "pageChange",
      page: client.curPage === pageName ? "dashboard" : pageName,
    });
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

  const getPage = () => {
    switch (client.curPage) {
      case "inbox":
        return (
          <Inbox
            displaySummaries={userPreferences.isChecked}
            emailList={emailsByDate}
            setCurEmail={handleSetCurEmail}
            curEmail={client.curEmail}
          />
        );
      case "settings":
        return (
          <Settings
            isChecked={userPreferences.isChecked}
            handleToggleSummariesInInbox={handleToggleSummariesInInbox}
            emailFetchInterval={userPreferences.emailFetchInterval}
            handleSetEmailFetchInterval={handleSetEmailFetchInterval}
            theme={userPreferences.theme}
            handleSetTheme={handleSetTheme}
          />
        );
      default:
        return (
          <Dashboard
            emailList={emailsByDate}
            handlePageChange={handlePageChange}
            setCurEmail={handleSetCurEmail}
          />
        );
    }
  };

  const emailClient = () => {
    return (
      <div className="client">
        <SideBar
          onLogoClick={handleLogoClick}
          expanded={client.expandedSideBar}
          handlePageChange={handlePageChange}
          selected={client.curPage}
        />
        {getPage()}
      </div>
    );
  };

  return <>{emailClient()}</>;
}

Client.propTypes = {
  emailsByDate: PropTypes.array,
  setEmailsByDate: PropTypes.func,
  defaultUserPreferences: PropTypes.object,
};

export default Client;
