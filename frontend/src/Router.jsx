import { BrowserRouter, Routes, Route } from "react-router";
import Page from "./page";

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
