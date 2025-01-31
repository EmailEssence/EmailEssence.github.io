import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import Settings from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
import "./index.css";
import "./preflight.css";


const Main = () => {
  const [showPage, setShowPage] = useState(false); 

  // Function to handle the settings click
  const handleSettingsClick = () => {
    setShowPage(!showPage);
  };
  const divClassName = `settings ${showPage ? 'show' : ''}`
  return (
    <>
      <div className="page">
        <SideBar onSettingsClick={handleSettingsClick} />
        <div className={divClassName}>
          {/* Interchange settings/dashboard/inbox Until we make global variables */}
          <Settings />
        </div>
      </div>
    </>
  );
};

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Main/>
  </StrictMode>
);

