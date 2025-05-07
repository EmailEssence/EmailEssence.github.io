import { useNavigate } from "react-router";
import Logo from "../../assets/Logo";
import "./Home.css";

export default function About() {
  const navigate = useNavigate();
  return (
    <div className="home">
      <div className="nav-container">
        <div className="logo-container" onClick={() => navigate("/")}>
          <Logo />
        </div>
        <div className="nav-item" onClick={() => navigate("/about")}>
          About Us
        </div>
        <div className="nav-item" onClick={() => navigate("/contact")}>
          Contact Us
        </div>
        <div className="nav-item" onClick={() => navigate("/privacy")}>
          Privacy Policy
        </div>
        <div className="nav-item" onClick={() => navigate("/terms")}>
          Terms of Service
        </div>
        <div className="nav-item" onClick={() => navigate("/login")}>
          Sign In
        </div>
      </div>
      
      <div className="about-us">
        <h1>About Us</h1>
        <p>
          We are a team of passionate developers dedicated to creating
          innovative solutions that enhance productivity and streamline
          communication. Our AI email assistant is designed to help you manage
          your inbox more efficiently, allowing you to focus on what matters
          most.
        </p>
      </div>
    </div>
  );
}
