import styles from "./Error.module.css";

function Error() {
  const errorMessage = localStorage.getItem("error_message") || "Unknown error";

  return (
    <div className={styles.page}>
      <div className={styles.formBox}>
        <div className={styles.errorDiv}>
          <div className={styles.errorIcon}>
            <img src="./src/assets/oldAssets/Logo.svg" alt="error Icon" />
          </div>
          <h1 className={styles.errorTitle}>Authentication Error</h1>
          <p className={styles.errorDescription}>
            Something went wrong, please try to login again.
          </p>
          <p className={styles.errorInfo}>Error: {errorMessage}</p>
          <button
            className={styles.retryButton}
            onClick={() => (window.location.href = "/login")}
          > Retry Login
          </button>
        </div>
      </div>
    </div>
  );
}

export default Error;
