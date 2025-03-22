import { useEffect, useReducer } from "react";
import "./client.css";
import Dashboard from "./components/dashboard/dashboard";
import Inbox from "./components/inbox/inbox";
import { Settings } from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
import fetchEmails from "./emails/emailParse";
import { clientReducer, userPreferencesReducer } from "./reducers";

export default function Client({
  emailsByDate,
  setEmailsByDate,
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
        const requestedEmails = await fetchEmails(100); // Limited to 100 new emails per interval cycle
        if (requestedEmails.length > 0) {
          console.log(requestedEmails);
          const newEmails = getNewEmails(requestedEmails, emailsByDate); // O(n^2) operation
          console.log(newEmails);
          if (newEmails.length > 0) {
            setEmailsByDate([...newEmails, ...emailsByDate]);
          }
        }
      } catch (error) {
        console.error(`Loading Emails Error: ${error}`);
      }
    }, userPreferences.emailFetchInterval * 1000);
    return () => clearInterval(clock);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userPreferences.emailFetchInterval]);

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

function getNewEmails(requestedEmails, allEmails) {
  return requestedEmails.filter((reqEmail) => {
    let exists = false;
    for (const email of allEmails) {
      if (email.email_id === reqEmail.email_id) exists = true;
    }
    return !exists;
  });
}
