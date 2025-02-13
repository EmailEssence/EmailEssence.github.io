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
  const [sideBarSize, setSideBarSize] = useState(80);
  const [loggedIn, setLoggedIn] = useState(false);
  const [currentPage, setCurrentPage] = useState("login");
  const [curEmail, setCurEmail] = useState(emailsByDate[0]);
  const gridTempCol = `${sideBarSize}px 1fr`;

  const handleLogin = () => {
    setLoggedIn(true);
  };

  // Function to handle expanding and collapsing of sidebar
  const handleLogoClick = () => {
    setSideBarSize(sideBarSize === 80 ? 180 : 80);
  };

  const handlePageChange = (pageName) => {
    showPage === pageName ? setShowPage("dashboard") : setShowPage(pageName);
  };

  const handleSetCurEmail = (email) => {
    console.log("setting cur email to ");
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
          containerWidth={`${sideBarSize}px`}
          handlePageChange={handlePageChange}
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
