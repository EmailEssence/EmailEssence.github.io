import { useRef } from "react";
import Logo from "../../assets/Logo";
import "./Home.css";

export default function Home() {
  const homeRef = useRef(null);
  const aboutRef = useRef(null);
  const contactRef = useRef(null);
  const privacyRef = useRef(null);
  const termsRef = useRef(null);
  const loginRef = useRef(null);

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
        <div className="nav-item" onClick={() => scrollToSection(aboutRef)}>
          About Us
        </div>
        <div className="nav-item" onClick={() => scrollToSection(contactRef)}>
          Contact Us
        </div>
        <div className="nav-item" onClick={() => scrollToSection(privacyRef)}>
          Privacy Policy
        </div>
        <div className="nav-item" onClick={() => scrollToSection(termsRef)}>
          Terms of Service
        </div>
        <div className="nav-item" onClick={() => scrollToSection(loginRef)}>
          Sign In
        </div>
      </div>

      <div ref={homeRef} className="title-container">
        <h1 className="title">Welcome to EmailEssence</h1>
        <h2 className="subtitle">Sign in now to connect to your AI-Powered Email Assistant</h2>
        {/* insert snapshot of ui */}
        <div
          className="login-navigate-button"
          onClick={() => navigate("/login")}
        >
          Sign In
        </div>
      </div>

      <div className="overview-container">
        <div className="overview">
          <h1>Overview</h1>
          <div className="overview-items">
            <div className="item1">
              {/* insert image */}
              <h2>Talking Point 1</h2>
              <p>
                Lorem nostrud tempor ut eiusmod ipsum irure fugiat sunt consectetur
                cillum tempor. Nulla non qui veniam amet amet qui ut ad est duis
                qui enim minim Lorem. Elit ea ea adipisicing nisi et cillum eu
                proident magna do dolor.
              </p>
            </div>

            <div className="item2">
              {/* insert image */}
              <h2>Talking Point 2</h2>
              <p>
                Lorem nostrud tempor ut eiusmod ipsum irure fugiat sunt consectetur
                cillum tempor. Nulla non qui veniam amet amet qui ut ad est duis
                qui enim minim Lorem. Elit ea ea adipisicing nisi et cillum eu
                proident magna do dolor.
              </p>
            </div>
            <div className="item3">
              {/* insert image */}
              <h2>Talking Point 3</h2>
              <p>
                Lorem nostrud tempor ut eiusmod ipsum irure fugiat sunt consectetur
                cillum tempor. Nulla non qui veniam amet amet qui ut ad est duis
                qui enim minim Lorem. Elit ea ea adipisicing nisi et cillum eu
                proident magna do dolor.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div ref={aboutRef} className="about-us">
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
