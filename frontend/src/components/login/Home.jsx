import { useRef } from "react";
import { useNavigate } from "react-router";
import Logo from "../../assets/Logo";
import Mail from "../../assets/mail";
import ReaderView from "../../assets/ReaderView";
import UserIcon from "../../assets/UserIcon";
import "./Home.css";

export default function Home() {
  const navigate = useNavigate();
  const homeRef = useRef(null);
  const overviewRef = useRef(null);
  const aboutRef = useRef(null);

  const scrollToSection = (ref) => {
    if (ref.current) {
      ref.current.scrollIntoView({ behavior: "smooth" });
    }
  }
  return (
    <div className="home">

      <div className="nav-container">
        <div className="logo-container" onClick={() => scrollToSection(homeRef)}>
          <Logo />
        </div>
        <div className="nav-item" onClick={() => scrollToSection(overviewRef)}>
          Overview
        </div>
        <div className="nav-item" onClick={() => scrollToSection(aboutRef)}>
          About Us
        </div>
        <div className="nav-item" onClick={() => navigate("/login")}>
          Sign In
        </div>
      </div>

      <div className="background-container">
        <div className="background-img"></div>
        <div ref={homeRef} className="title-container">
          <h1 className="title">Welcome to EmailEssence</h1>
          <h2 className="subtitle">Redefining Email Management</h2>
          <h2 className="subtitle">An intelligent solution designed to enhance how we manage our inbox</h2>
          <h2 className="subtitle">Sign in now to connect to your AI-Powered Email Assistant</h2>
          <div className="snap-of-ui"></div>
          <div
            className="login-navigate-button"
            onClick={() => navigate("/login")}
          >
            Sign In
          </div>
        </div>
      </div>

      <div ref={overviewRef} className="overview-container">
        <div className="overview">
          <h1>Overview</h1>
          <div className="overview-items">
            <div className="item1">
              <Mail className="mail-svg" />
              <h2>AI Email Summarization</h2>
              <p>
                Automatically transforms long, cluttered emails into clear and
                concise summaries — helping users focus on what truly matters.
              </p>
            </div>
            <div className="item2">
              <ReaderView className="readerview-svg" />
              <h2>Reader View</h2>
              <p>
                Offers a distraction-free reading experience by stripping away
                unnecessary formatting and emphasizing the core message of each email.
              </p>
            </div>
            <div className="item3">
              <UserIcon className="usericon-svg" />
              <h2>User-Centric Design</h2>
              <p>
                Built with simplicity and accessibility in mind — from intuitive
                navigation to clean layouts that streamline email interaction
                for every user.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* create a features section */}

      <div ref={aboutRef} className="about-us">
        <h1>About Us</h1>
        <p>
          We are a team of passionate developers dedicated to creating
          innovative solutions that enhance productivity and streamline
          communication. Our AI email assistant is designed to help you manage
          your inbox more efficiently, allowing you to focus on what matters
          most.
        </p>
        {/* insert image of all team members */}
      </div>

      <footer className="footer-container">
        <div className="footer-item" onClick={() => navigate("/privacy")}>
          Privacy Policy
        </div>
        <div className="footer-item" onClick={() => navigate("/terms")}>
          Terms of Service
        </div>
        <div className="footer-item" onClick={() => navigate("/contact")}>
          Contact Us
        </div>
        <p>&copy; 2024 EmailEssence. All rights reserved.</p>
      </footer>

    </div>


  );
}
