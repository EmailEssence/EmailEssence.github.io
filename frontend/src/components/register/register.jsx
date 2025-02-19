import styles from "./register.module.css";

export default function Register({ onLoginClick }) {
  const handleGoogleRegister = () => {
    window.location.href = "GoogleOAuthAuthorizationURL";
  };

  return (
    <div className={styles.page}>
      <div className={styles.formBox}>
        <div className={styles.registerDiv}>
          <div className={styles.registerIcon}>
            <img src="./src/assets/Logo.PNG" alt="Register Icon" className={styles.registerPhoto} />
          </div>
          <p className={styles.title}>Create an Account</p>
          <div className={styles.loginInLink}>
            Already have an account? <a href="#" onClick={onLoginClick}>Login</a>
          </div>
          <form className={styles.registerInput}>
            <div>
              <label htmlFor="email"></label>
              <input
                className={styles.inputBox}
                type="email"
                id="email"
                name="email"
                placeholder="Enter your Email Address"
              />
            </div>
            <div>
              <label htmlFor="password"></label>
              <input
                className={styles.inputBox}
                type="password"
                id="password"
                name="password"
                placeholder="Password"
              />
            </div>
            <div>
              <input
                className={styles.registerButton}
                type="submit"
                value="Continue"
              />
            </div>
            <div className={styles.orContinueWith}>
              <span>or continue with:</span>
            </div>
            <div>
              <input
                onClick={handleGoogleRegister}
                className={styles.registerButton}
                type="submit"
                value="Google"
              />
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}