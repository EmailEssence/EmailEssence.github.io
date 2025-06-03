import PropTypes from "prop-types";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import fetchEmails, { getUserPreferences } from "../../emails/emailHandler";
import "./Loading.css";

const emailsPerPage = 20;
const user_id = null; // Get user ID

export default function Loading({ setInitialEmails }) {
  const navigate = useNavigate();
  useEffect(() => {
    async function getInitialData() {
      const initialEmails = await fetchEmails(emailsPerPage);
      if (user_id) getUserPreferences(user_id);
      if (initialEmails.length < 1) {
        localStorage.setItem("error_message", "Failed To Retrieve Emails");
        navigate("/error");
      } else {
        setInitialEmails(initialEmails);
        navigate("/client/home");
      }
    }
    getInitialData();
  }, [navigate, setInitialEmails]);
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
