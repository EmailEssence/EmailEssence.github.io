import { useEffect } from "react";
import { useNavigate } from "react-router";
import { handleOAuthCallback } from "../../authentication/authenticate";
import "./Loading.css";

export default function Loading() {
  const navigate = useNavigate();
  useEffect(() => {
    async function completeOAuth() {
      const complete = await handleOAuthCallback();
      if (complete) {
        navigate("/client/loading");
      } else {
        navigate("/error");
      }
    }
    completeOAuth();
  });

  return (
    <div className="loading">
      <div className="loading-spinner" role="spinner"></div>
      <p className="loading-text">Loading...</p>
    </div>
  );
}
