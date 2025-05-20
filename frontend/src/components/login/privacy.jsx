import { useRef } from "react";
import { useNavigate } from "react-router";
import Logo from "../../assets/Logo";
import "./Home.css";

export default function PrivacyPolicy() {
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
                <div className="logo-container" onClick={() => navigate("/home")}>
                    <Logo />
                </div>
                <div className="nav-item" onClick={() => navigate("/home") && scrollToSection(overviewRef)}>
                    Overview
                </div>
                <div className="nav-item" onClick={() => navigate("/home") && scrollToSection(aboutRef)}>
                    About Us
                </div>
                <div className="nav-item" onClick={() => navigate("/login")}>
                    Sign In
                </div>
            </div>

            <div className="privacy-policy">
                <h1>Privacy Policy</h1>
                <p>Your privacy is important to us. We do not share your data with third parties.</p>
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