import PropTypes from "prop-types";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import fetchEmails from "../../emails/emailHandler";
import "./Loading.css";

export default function Loading({ setInitialEmails }) {
  const navigate = useNavigate();
  useEffect(() => {
    async function getInitialEmails() {
      const initialEmails = await fetchEmails();
      setInitialEmails(initialEmails);
      navigate("/client/home");
      // TODO: implement
    }
    getInitialEmails();
  }, []);
  return (
    <div className="loading">
      <div className="loading-spinner" role="spinner"></div>
      <p className="loading-text">Loading...</p>
    </div>
  );
}

Loading.propTypes = {
  setInitialEmails: PropTypes.func,
};
