import "./client.css";
import { useState } from "react";
import Dashboard from "./components/dashboard/dashboard";
import Inbox from "./components/inbox/inbox";
import { Settings } from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";

export default function Client({ emailsByDate }) {
  const [curPage, setCurPage] = useState("dashboard");
  const [expandedSideBar, setExpandedSideBar] = useState(false);

  const [curEmail, setCurEmail] = useState("current Email");
  const [isChecked, setIsChecked] = useState(false);
  const [emailFetchInterval, setEmailFetchInterval] = useState(0);
  const [theme, setTheme] = useState("system");
  const gridTempCol = `${expandedSideBar ? "180" : "80"}px 1fr`;

  const handleLogoClick = () => {
    setExpandedSideBar(!expandedSideBar);
  };

  const handlePageChange = (pageName) => {
    curPage === pageName ? setCurPage("dashboard") : setCurPage(pageName);
  };

  const handleToggleSummariesInInbox = () => {
    setIsChecked(!isChecked);
  };

  const handleSetEmailFetchInterval = (interval) => {
    setEmailFetchInterval(interval);
  };

  const handleSetTheme = (theme) => {
    setTheme(theme);
  };

  const handleSetCurEmail = (email) => {
    setCurEmail(email);
  };

  const getPage = () => {
    switch (curPage) {
      case "inbox":
        return (
          <Inbox
            emailList={emailsByDate}
            setCurEmail={handleSetCurEmail}
            curEmail={curEmail}
          />
        );
      case "settings":
        return (
          <Settings
            isChecked={isChecked}
            handleToggleSummariesInInbox={handleToggleSummariesInInbox}
            emailFetchInterval={emailFetchInterval}
            handleSetEmailFetchInterval={handleSetEmailFetchInterval}
            theme={theme}
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
      <div className="client" style={{ gridTemplateColumns: gridTempCol }}>
        <SideBar
          onLogoClick={handleLogoClick}
          expanded={expandedSideBar}
          handlePageChange={handlePageChange}
          selected={curPage}
        />
        {getPage()}
      </div>
    );
  };

  return <div className="page">{emailClient()}</div>;
}
