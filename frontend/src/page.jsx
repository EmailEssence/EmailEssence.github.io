import {useState} from "react";
import Dashboard from "./components/dashboard/dashboard";
import Settings from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
import Inbox from "./components/inbox/inbox";
import Login from "./components/login/login";
import "./page.css";

export default function Page() {
  const [showPage, setShowPage] = useState("dashboard");
  const [placeholder, setPlaceholder] = useState("80px");
  const [loggedIn, setLoggedIn] = useState(false);
  const gridTempCol = `${placeholder} 1fr`;

  const handleLogin = () => {
    setLoggedIn(true);
  };

  // Function to handle expanding and collapsing of sidebar
  const handleLogoClick = () => {
    placeholder === "80px" ? setPlaceholder("180px") : setPlaceholder("80px");
  };

  const getPageComponent = pageName => {
    showPage === pageName ? setShowPage("dashboard") : setShowPage(pageName);
  };

  const getPage = () => {
    switch (showPage) {
      case "inbox":
        return <Inbox />;
      case "settings":
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  const emailClient = () => {
    return (
      <div className="client" style={{gridTemplateColumns: gridTempCol}}>
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
    return <Login forward={handleLogin} />;
  };

  return (
    <>
      <div className="page">{loggedIn ? emailClient() : loginPage()}</div>
    </>
  );
}
