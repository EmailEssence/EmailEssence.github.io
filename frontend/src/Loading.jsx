import React, { useEffect } from "react";
import { handleOAuthCallback } from "./authentication/authenticate";
import "./loading.css";

export default function Loading() {
  useEffect(() => {
    const completeOAuth = async () => { //calls Oauth and updates the loading state
      await handleOAuthCallback(); 
    };

    completeOAuth();
  }, []);

  return (
    <div className="loading">
      <div className="loading-spinner"></div>
      <p className="loading-text">Loading...</p>
    </div>
  );
};
