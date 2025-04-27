import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./main.css";
import Router from "./components/router/Router";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Router />
  </StrictMode>
);
