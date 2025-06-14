import { useEffect } from "react";
import { useNavigate } from "react-router";
import { handleOAuthCallback } from "../../authentication/authenticate";
import "./Loading.css";

/**
 * A loading component that handles the OAuth callback and navigates to the home page.
 * It displays a loading spinner and text while the OAuth process is completed.
 */
export default function Loading() {
  const navigate = useNavigate();
  useEffect(() => {
    const completeOAuth = async () => {
      try {
        /* calls Oauth and updates the loading state */
        await handleOAuthCallback();

        navigate("/client/home#newEmails");
        /* Link to /client & mention new emails */
      } catch (error) {
        console.error("OAuth callback failed:", error);
        /* Optionally navigate to an error page */
        navigate("/error");
      }
    };

    completeOAuth();
  }, [navigate]);

  return (
    <div className="loading">
      <div className="loading-spinner" role="spinner"></div>
      <p className="loading-text">Loading...</p>
    </div>
  );
}
