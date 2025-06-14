import { useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import Logo from "../../assets/Logo";
import "./Home.css";

export default function Contact() {
    const navigate = useNavigate();
    const homeRef = useRef(null);
    const overviewRef = useRef(null);
    const aboutRef = useRef(null);

    /* Scrolls to the top */
    useEffect(() => { window.scrollTo(0, 0);}, []);

    /* smoothly scrolls to the ref section */
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

            <div className="contact-us">
                <h1>Contact Us</h1>
                <p>
                    Thank you for using EmailEssence!
                </p>
                <p>
                    We hope you enjoy our service and find it helpful in managing your
                    emails.
                </p>
                <p>
                    If you have any feedback or suggestions for improvement, please
                    feel free to reach out to us. We value your input and are always
                    looking for ways to enhance our service.
                </p>
                <p>
                    We look forward to serving you and helping you make the most of
                    your email experience.
                </p>
                <p>
                    If you have any questions or concerns,
                    please contact us at <a href="mailto:emailessencellc@gmail.com">emailessencellc@gmail.com</a>
                </p>
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