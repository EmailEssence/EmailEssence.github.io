import {StrictMode} from "react";
import {createRoot} from "react-dom/client";
import "./index.css";
//import App from "./App.jsx";
import SideBar from "./components/sidebar/sidebar";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <SideBar />
  </StrictMode>
);
