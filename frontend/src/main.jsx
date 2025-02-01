import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import Display from "./app";
import "./preflight.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Display />
  </StrictMode>
);
