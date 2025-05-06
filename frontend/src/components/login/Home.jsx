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
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Vero officiis
          enim corrupti totam autem ipsam quaerat molestiae reprehenderit quae
          ab nihil, accusamus odit eum expedita porro saepe, dolorem perferendis
          tempore.
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
