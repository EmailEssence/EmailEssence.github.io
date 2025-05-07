import { useNavigate } from "react-router";
import Logo from "../../assets/Logo";
import "./Home.css";

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="home">

      <div className="nav-container">
        <div className="logo-container">
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

      <div className="title-container">
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
          <div className="box1">
            {/* insert image */}
            <h2>Talking Point 1</h2>
            <p>
              Lorem nostrud tempor ut eiusmod ipsum irure fugiat sunt consectetur
              cillum tempor. Nulla non qui veniam amet amet qui ut ad est duis
              qui enim minim Lorem. Elit ea ea adipisicing nisi et cillum eu
              proident magna do dolor.
            </p>
          </div>

          <div className="box2">
            {/* insert image */}
            <h2>Talking Point 2</h2>
            <p>
              Lorem nostrud tempor ut eiusmod ipsum irure fugiat sunt consectetur
              cillum tempor. Nulla non qui veniam amet amet qui ut ad est duis
              qui enim minim Lorem. Elit ea ea adipisicing nisi et cillum eu
              proident magna do dolor.
            </p>
          </div>
          <div className="box2">
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
  )
}
