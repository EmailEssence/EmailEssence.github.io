import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./preflight.css";
import Display from "./page";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Display />
  </StrictMode>
);
