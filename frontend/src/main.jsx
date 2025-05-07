import { BrowserRouter } from "react-router";
import { createRoot } from "react-dom/client";
import "./main.css";
import Display from "./components/router/Router";

createRoot(document.getElementById("root")).render(
  <BrowserRouter basename={`/${import.meta.env.PUBLIC_URL}`}>
    <Display />
  </BrowserRouter>
);
