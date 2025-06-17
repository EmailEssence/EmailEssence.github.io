import PropTypes from "prop-types";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import fetchEmails, { getUserPreferences } from "../../emails/emailHandler";
import "./Loading.css";

const user_id = null; // Get user ID

/**
 * A loading component that handles the OAuth callback and navigates to the home page.
 * It displays a loading spinner and text while the OAuth process is completed.
 */
export default function Loading({
  setInitialEmails,
  setInitialEmail,
  emailsPerPage,
}) {
  const navigate = useNavigate();
  useEffect(() => {
    // duplicate call
    async function getInitialData() {
      const initialEmails = await fetchEmails(emailsPerPage);
      if (user_id) getUserPreferences(user_id);
      if (initialEmails.length < 1) {
        localStorage.setItem("error_message", "Failed To Retrieve Emails");
        navigate("/error");
      } else {
        setInitialEmails(initialEmails);
        setInitialEmail(initialEmails[0]);
        navigate("/client/home");
      }
    }
    getInitialData();
  }, [navigate, setInitialEmails, setInitialEmail, emailsPerPage]);
  return (
    <div className="loading">
      <div className="loading-spinner" role="spinner"></div>
      <p className="loading-text">Loading...</p>
    </div>
  );
}

Loading.propTypes = {
  setInitialEmails: PropTypes.func,
  setInitialEmail: PropTypes.func,
  emailsPerPage: PropTypes.number,
};
