import styles from "./register.module.css";

export default function Register({ onLoginClick }) {
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
                placeholder="Email Address"
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
                value="Register"
              />
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}