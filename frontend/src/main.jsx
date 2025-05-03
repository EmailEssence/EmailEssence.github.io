import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./main.css";
import Display from "./components/router/Router";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Display />
  </StrictMode>
);
