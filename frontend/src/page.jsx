// ReadME:
// Uncomment Import & Run: npm run dev In ./frontend to Test

import {useState} from "react";
import Dashboard from "./components/dashboard/dashboard";
import Settings from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
import Inbox from "./components/inbox/inbox";
import "./page.css";

export default function Page() {
  const [showPage, setShowPage] = useState("dashboard");
  const [placeholder, setPlaceholder] = useState("80px");

  // Function to handle expanding and collapsing of sidebar
  const handleLogoClick = () => {
    if (placeholder === "80px") {
      setPlaceholder("180px");
    } else {
      setPlaceholder("80px");
    }
  };

  const getPageComponent = pageName => {
    if (showPage === pageName) {
      setShowPage("dashboard");
      console.log("dashboard");
      return;
    }
    setShowPage(pageName);
    console.log(pageName);
  };

  const getPage = () => {
    if (showPage === "dashboard") {
      return <Dashboard />;
    } else if (showPage === "inbox") {
      return <Inbox />;
    } else {
      return <Settings />;
    }
  };

  return (
    <>
      <div className="page">
        <SideBar
          onLogoClick={handleLogoClick}
          containerWidth={placeholder}
          getPageComponent={getPageComponent}
          selected={showPage}
        />
        {/* Interchange settings/dashboard/inbox Until we make global variables */}
        {getPage()}
      </div>
    </>
  );
}
