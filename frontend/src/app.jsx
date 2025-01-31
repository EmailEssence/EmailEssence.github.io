import {useState} from "react";
//import Settings from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
import Inbox from "./components/inbox/inbox";
import "./app.css";

export default function Page() {
  const [showPage, setShowPage] = useState(false);

  // Function to handle the settings click
  const handleSettingsClick = () => {
    setShowPage(!showPage);
  };
  // const divClassName = `settings ${showPage ? "show" : ""}`;
  return (
    <>
      <div className="page">
        <SideBar onSettingsClick={handleSettingsClick} />
        {/* Interchange settings/dashboard/inbox Until we make global variables */}
        {/* <Settings /> */}
        <Inbox />
      </div>
    </>
  );
}
