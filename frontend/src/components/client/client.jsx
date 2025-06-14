import { useEffect, useReducer, useState } from "react";
import { Outlet, Route, Routes, useNavigate } from "react-router";
import fetchEmails, {
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
  const [hasUnloadedEmails, setHasUnloadedEmails] = useState(true);
  const [client, dispatchClient] = useReducer(clientReducer, {
    expandedSideBar: false,
    emails: [],
    curEmail: {},
  });
  const [userPreferences, dispatchUserPreferences] = useReducer(
    userPreferencesReducer,
    { isChecked: true, emailFetchInterval: 120, theme: "light" }
  );

  /**
   * Sets up an interval to fetch new emails based on user preference.
   * @returns {void}
   */
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

  const handleSetEmails = (emails) => {
    dispatchClient({
      type: "emailAdd",
      email: emails,
    });
  };

  // requests a page worth of emails and adds to the current email list,
  // returns whether more emails exist or not
  const requestMoreEmails = async () => {
    console.log(
      `fetchEmails being called with ${emailsPerPage} & ${client.emails.length}`
    );
    const newEmails = await fetchEmails(emailsPerPage, client.emails.length);
    console.log(`newEmails.length = ${newEmails.length}`);
    if (newEmails.length > 0) {
      handleAddEmails(newEmails);
      console.log(`Length: ${newEmails.length}`);
    } else {
      setHasUnloadedEmails(false);
    }
  };

  const handleSetCurEmail = (email) => {
    dispatchClient({
      type: "emailChange",
      email: email,
    });
  };

  const handleRequestSummaries = async (emails) => {
    const allEmails = client.emails;
    const ids = emails.map((email) => {
      return email.email_id;
    });
    console.log("In handle request summaries");
    const result = await Promise.all(
      allEmails.map((email) => {
        let newEmail = email;
        if (ids.includes(email.email_id)) newEmail = setSummary(email);
        return newEmail;
      })
    );

    dispatchClient({
      type: "emailAdd",
      email: result,
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
              setInitialEmails={handleSetEmails}
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
                hasUnloadedEmails={hasUnloadedEmails}
                emailsPerPage={emailsPerPage}
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
                hasUnloadedEmails={hasUnloadedEmails}
              />
            }
          />
        </Route>
      </Routes>
    </>
  );
}

export default Client;
