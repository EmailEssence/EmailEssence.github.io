import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import Display from "./components/router/Router";
import "./main.css";

/* Entry point for our react application.*/
createRoot(document.getElementById("root")).render(
  <BrowserRouter basename={`/${import.meta.env.BASE_URL}`}>
    <Display />
  </BrowserRouter>
);
