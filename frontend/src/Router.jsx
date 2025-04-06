import { BrowserRouter, Routes, Route } from "react-router";
import Auth from "./Auth";
import Login from "./components/login/login";
import Loading from "./Loading";
import Dashboard from "./components/dashboard/dashboard";
import Inbox from "./components/inbox/inbox";
import Client from "./client";
import { Settings } from "./components/settings/settings";

function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Auth />}>
          <Route path="login" element={<Login />} />
          <Route path="loading" element={<Loading />} />
        </Route>
        <Route path="client" element={<Client />}>
          <Route index element={<Dashboard />} />
          <Route path="inbox" element={<Inbox />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default Router;
