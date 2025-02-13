import { useState } from "react";
import Dashboard from "./components/dashboard/dashboard";
import Inbox from "./components/inbox/inbox";
import Login from "./components/login/login";
import Register from "./components/register/register";
import { Settings } from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
import emailsByDate from "./emails/emailParse";
import "./page.css";

export default function Page() {
  const [showPage, setShowPage] = useState("dashboard");
  const [placeholder, setPlaceholder] = useState("80px");
  const [loggedIn, setLoggedIn] = useState(false);
  const [currentPage, setCurrentPage] = useState("login");
  const [curEmail, setCurEmail] = useState(emailsByDate[0]);
  const gridTempCol = `${placeholder} 1fr`;

  const handleLogin = () => {
    setLoggedIn(true);
  };

  // Function to handle expanding and collapsing of sidebar
  const handleLogoClick = () => {
    placeholder === "80px" ? setPlaceholder("180px") : setPlaceholder("80px");
  };

  const getPageComponent = (pageName) => {
    showPage === pageName ? setShowPage("dashboard") : setShowPage(pageName);
  };

  const handleSetCurEmail = (email) => {
    setCurEmail(email);
  };

  const getPage = () => {
    switch (showPage) {
      case "inbox":
        return (
          <Inbox
            emailList={emailsByDate}
            setCurEmail={handleSetCurEmail}
            curEmail={curEmail}
          />
        );
      case "settings":
        return <Settings />;
      default:
        return (
          <Dashboard
            emailList={emailsByDate}
            getPageComponent={getPageComponent}
          />
        );
    }
  };

  const emailClient = () => {
    return (
      <div className="client" style={{ gridTemplateColumns: gridTempCol }}>
        <SideBar
          onLogoClick={handleLogoClick}
          containerWidth={placeholder}
          getPageComponent={getPageComponent}
          selected={showPage}
        />
        {getPage()}
      </div>
    );
  };

  const loginPage = () => {
    return (
      <Login
        forward={handleLogin}
        onSignUpClick={() => setCurrentPage("register")}
      />
    );
  };

  const registerPage = () => {
    return <Register onLoginClick={() => setCurrentPage("login")} />;
  };

  return (
    <>
      <div className="page">
        {loggedIn
          ? emailClient()
          : currentPage === "login"
          ? loginPage()
          : registerPage()}
      </div>
    </>
  );
}
