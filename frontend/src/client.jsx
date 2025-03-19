/* eslint-disable react/prop-types */
import { useReducer } from "react";
import "./client.css";
import Dashboard from "./components/dashboard/dashboard";
import Inbox from "./components/inbox/inbox";
import { Settings } from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
import { clientReducer, userPreferencesReducer } from "./reducers";

export default function Client({ emailsByDate }) {
  const [client, dispatchClient] = useReducer(clientReducer, {
    curPage: "dashboard",
    expandedSideBar: false,
    curEmail: emailsByDate[0],
  });
  const [userPreferences, dispatchUserPreferences] = useReducer(
    userPreferencesReducer,
    { isChecked: false, emailFetchInterval: 0, theme: "system" }
  );
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

  return <div className="page">{emailClient()}</div>;
}
