import { useEffect, useReducer, useState } from "react";
import { Outlet, Route, Routes, useNavigate } from "react-router";
import {
  fetchEmails,
  handleNewEmails,
  setSummary,
} from "../../emails/emailHandler";
import "./client.css";
import Dashboard from "./dashboard/dashboard";
import Inbox from "./inbox/inbox";
import { clientReducer, userPreferencesReducer } from "./reducers";
import { Settings } from "./settings/settings";
import SideBar from "./sidebar/sidebar";
import Loading from "../login/Loading";

function Client() {
  const navigate = useNavigate();
  const [emailsPerPage, setEmailsPerPage] = useState(
    Math.max(1, Math.floor(window.innerHeight / 35))
  );
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
        const requestedEmails = await fetchEmails(0, true);
        const newEmails = handleNewEmails(client.emails, requestedEmails);
        if (newEmails.length > 0) handleAddEmails(newEmails, true);
      } catch (error) {
        console.error(`Loading Emails Error: ${error}`);
      }
    }, userPreferences.emailFetchInterval * 1000);
    return () => clearInterval(clock);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userPreferences.emailFetchInterval]);

  useEffect(() => {
    function updateEmailsPerPage() {
      setEmailsPerPage(Math.max(1, Math.floor(window.innerHeight / 35)));
    }

    let resizeTimeout = null;
    function handleResize() {
      if (resizeTimeout) clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(updateEmailsPerPage, 50);
    }

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      if (resizeTimeout) clearTimeout(resizeTimeout);
    };
  }, []);

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

  // requests a page worth of emails and adds to the current email list,
  // returns whether more emails exist or not
  const requestMoreEmails = async () => {
    const newEmails = await fetchEmails(client.emails.length);
    if (newEmails.length > 0) {
      handleAddEmails(newEmails);
    } else {
      return false;
    }
    return true;
  };

  const handleSetCurEmail = (email) => {
    dispatchClient({
      type: "emailChange",
      email: email,
    });
  };

  const handleRequestSummaries = async (emails) => {
    let curEmails = client.emails;
    for (const email in emails) {
      const res = await setSummary(email, curEmails);
      if (res.length > 0) {
        curEmails = res;
      }
    }
    dispatchClient({
      type: "emailAdd",
      email: curEmails,
    });
  };

  return (
    <>
      <Routes>
        <Route
          path="loading"
          element={
            <Loading
              emailsPerPage={emailsPerPage}
              setInitialEmails={handleAddEmails}
              setInitialEmail={handleSetCurEmail}
            />
          }
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
                requestMoreEmails={requestMoreEmails}
                requestSummaries={handleRequestSummaries}
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
                requestMoreEmails={requestMoreEmails}
                emailsPerPage={emailsPerPage}
                requestSummaries={handleRequestSummaries}
              />
            }
          />
        </Route>
      </Routes>
    </>
  );
}

export default Client;
