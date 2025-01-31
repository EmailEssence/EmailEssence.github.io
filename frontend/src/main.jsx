import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import Settings from "./components/settings/settings";
import SideBar from "./components/sidebar/sidebar";
import "./index.css";


const Main = () => {
  const [showSettings, setShowSettings] = useState(false); 

  // Function to handle the settings click
  const handleSettingsClick = () => {
    setShowSettings(!showSettings);
  };

  return (
    <>
      <SideBar onSettingsClick={handleSettingsClick} />
      <div className={`settings ${showSettings ? 'show' : ''}`}>
        <Settings />
      </div>
    </>
  );
};

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Main/>
  </StrictMode>
);

