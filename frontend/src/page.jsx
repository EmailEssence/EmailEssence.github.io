// ReadME:
// Uncomment Import & Run: npm run dev In ./frontend to Test

import {useState} from "react";
//import Settings from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
// import Inbox from "./components/inbox/inbox";
import "./page.css";

export default function Page() {
  //const [showPage, setShowPage] = useState(false);
  const [placeholder, setPlaceholder] = useState("80px");

  // Function to handle the settings click
  const handleLogoClick = () => {
    if (placeholder === "80px") {
      setPlaceholder("180px");
    } else {
      setPlaceholder("80px");
    }
  };
  // const divClassName = `settings ${showPage ? "show" : ""}`;
  return (
    <>
      <div className="page">
        <SideBar onLogoClick={handleLogoClick} containerWidth={placeholder} />
        {/* Interchange settings/dashboard/inbox Until we make global variables */}
        {/* <Settings /> */}
        {/* <Inbox /> */}
      </div>
    </>
  );
}
