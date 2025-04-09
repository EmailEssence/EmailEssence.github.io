import React, { useEffect, useState } from "react";
import "./loading.css";

const Loading = ({ handleOAuthCallback }) => {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const completeOAuth = async () => { //calls Oauth and updates the loading state
      await handleOAuthCallback(); 
      setIsLoading(false); // once Oauth is complete it is set to false
    };

    completeOAuth();
  }, [handleOAuthCallback]);

  return (
    <div className="loading">
      {isLoading ? (
        <>
          <div className="loading-spinner"></div>
          <p className="loading-text">Loading...</p>
        </>
      ) : (
        <p className="loading-text">Authentication Completed</p>
      )}
    </div>
  );
};

export default Loading;