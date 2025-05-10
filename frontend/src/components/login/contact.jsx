import { useNavigate } from "react-router";
import Logo from "../../assets/Logo";
import "./Home.css";

export default function Contact() {
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

            <div>
                <h1>Contact Us</h1>
                <p>Feel free to reach out to us for any inquiries.</p>
            </div>
        </div>
    );
}