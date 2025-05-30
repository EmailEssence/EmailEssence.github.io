import Logo from "../../assets/Logo";
import PropTypes from "prop-types";
import "./login.css";

const Login = ({ handleGoogleClick }) => {
  return (
    <div className="login-page">
      <div className="formBox">
        <div className="loginDiv">
          <div className="loginIcon">
            <Logo />
          </div>
          <p className="title">Welcome Back</p>
          <button onClick={handleGoogleClick} className="googleButton">
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
