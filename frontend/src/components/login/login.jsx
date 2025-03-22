import styles from "./login.module.css";

export const Login = ({ handleGoogleClick }) => {
  return (
    <div className={styles.page}>
      <div className={styles.formBox}>
        <div className={styles.loginDiv}>
          <div className={styles.loginIcon}>
            <img src="./src/assets/oldAssets/Logo.svg" alt="Logo Icon" />
          </div>
          <p className={styles.title}>Welcome Back</p>
          <button onClick={handleGoogleClick} className={styles.googleButton}>
            Login with Google
          </button>
        </div>
      </div>
    </div>
  );
};
