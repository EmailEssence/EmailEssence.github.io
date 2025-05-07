import styles from "./login.module.css";
import Logo from "../../assets/Logo";
import PropTypes from "prop-types";

const Login = ({ handleGoogleClick }) => {
  return (
    <div className={styles.page}>
      <div className={styles.formBox}>
        <div className={styles.loginDiv}>
          <div className={styles.loginIcon}>
            <Logo />
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

Login.propTypes = {
  handleGoogleClick: PropTypes.func,
};

export default Login;
