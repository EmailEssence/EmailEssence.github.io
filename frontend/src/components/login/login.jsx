import styles from "./login.module.css";

export default function Login({ forward, onSignUpClick }) {
  return (
    <div className={styles.page}>
      <div className={styles.formBox}>
        <div className={styles.loginDiv}>
          <div className={styles.loginIcon}>
            <img src="./src/assets/Logo.PNG" alt="Login Icon" className={styles.loginPhoto} />
          </div>
          <p className={styles.title}>Welcome Back</p>
          <div className={styles.signUpLink}>
            Don't have an account yet? <a href="#" onClick={onSignUpClick}>Sign up</a>
          </div>
          <form className={styles.loginInput}>
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
                onClick={forward}
                className={styles.loginButton}
                type="submit"
                value="Login"
              />
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
