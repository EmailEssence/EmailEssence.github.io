import "./Home.css";
import { useNavigate } from "react-router";

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="home">
      <div className="container">
        <div className="logo"></div>
        <div className="about"></div>
        <div
          className="login-navigate-button"
          onClick={() => navigate("/login")}
        ></div>
      </div>
    </div>
  );
}
