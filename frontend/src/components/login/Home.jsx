import Logo from "../../assets/Logo";
import "./Home.css";
import { useNavigate } from "react-router";

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="home">
      <div className="logo-container">
        <Logo />
      </div>
      <div className="nav-container">
        <div className="about">
          Cut through email overload with our AI-powered solution that
          intelligently summarizes and categorizes messages, bringing clarity to
          your communications.
        </div>
        <div
          className="login-navigate-button"
          onClick={() => navigate("/login")}
        >
          Login Page
        </div>
      </div>
    </div>
  );
}
