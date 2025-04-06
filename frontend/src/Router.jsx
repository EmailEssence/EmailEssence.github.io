import { BrowserRouter, Routes, Route } from "react-router";
import Page from "./page";
import Auth from "./Auth";
import Login from "./components/login/login";
import Loading from "./Loading";
import Dashboard from "./components/dashboard/dashboard";
import Inbox from "./components/inbox/inbox";
import { Settings } from "./components/settings/settings";

function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Page />} />
        <Route element={<Auth />}>
          <Route path="login" element={<Login />} />
          <Route path="loading" element={<Loading />} />
        </Route>
        <Route path="client">
          <Route index element={<Dashboard />} />
          <Route path="inbox" element={<Inbox />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default Router;
