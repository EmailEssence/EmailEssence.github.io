import { BrowserRouter } from "react-router";
import { createRoot } from "react-dom/client";
import "./main.css";
import Display from "./components/router/Router";

createRoot(document.getElementById("root")).render(
  <BrowserRouter basename={"/"}>
    <Display />
  </BrowserRouter>
);
