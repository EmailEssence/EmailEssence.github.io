import { useNavigate } from "react-router";
import Logo from "../../assets/Logo";
import "./Home.css";

export default function PrivacyPolicy(){
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

            <div className="privacy-policy">
            <h1>Privacy Policy</h1>
            <p>Your privacy is important to us. We do not share your data with third parties.</p>
            </div>
        </div>
    );
}