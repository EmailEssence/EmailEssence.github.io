import { BrowserRouter, Routes, Route } from "react-router";
import Page from "./page";

function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Page />} />
      </Routes>
    </BrowserRouter>
  );
}

export default Router;
