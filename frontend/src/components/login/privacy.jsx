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
                <p><strong>Effective Date:</strong> 6/01/2025<br />
                    <strong>Last Updated:</strong> 6/01/2025</p>
                <p>
                    At EmailEssence, we are committed to protecting your privacy. Our software is built with the principle that your inbox is your private space, and our goal is to enhance your productivity without compromising your personal data. This Privacy Policy outlines how we handle, process, and protect your information when you use our application.
                </p>
                <h2>1. About EmailEssence</h2>
                <p>
                    EmailEssence is an AI-powered email management tool designed to improve the way users interact with their inboxes. By leveraging Natural Language Processing (NLP), we offer summarization, prioritization, and a clutter-free email reading experience across web and desktop platforms—without profiling, tracking, or advertising.
                </p>
                <h2>2. Data Collection and Usage</h2>
                <h3>2.1 Email Access via OAuth 2.0</h3>
                <ul>
                    <li>We never store your login credentials.</li>
                    <li>Access is granted only with your explicit consent.</li>
                    <li>You can revoke access at any time via your email provider.</li>
                </ul>
                <h3>2.2 Email Content</h3>
                <p>
                    When you authorize access, we retrieve only the necessary email content to display and summarize within the application. This content is never sold, shared, or used for advertising purposes.
                </p>
                <h3>2.3 AI Summarization</h3>
                <ul>
                    <li>Only minimal, relevant email content is sent securely.</li>
                    <li>No personal identifiers (e.g., email addresses) are included.</li>
                    <li>Data is never stored by the AI provider beyond the processing session.</li>
                </ul>
                <h3>2.4 Application Settings and Preferences</h3>
                <p>
                    We store limited non-personal information locally on your device to support preferences such as theme settings, interface layout, and frequency of email refresh. No behavioral tracking or analytics profiling is performed.
                </p>
                <h2>3. Data Security and Storage</h2>
                <ul>
                    <li><strong>Encryption in Transit and at Rest:</strong> All communication between your device and our servers is secured using TLS. Any data temporarily cached is encrypted using industry-standard methods (e.g., AES-256).</li>
                    <li><strong>No Persistent Storage of Emails:</strong> We do not store email content, metadata, or summaries on our servers beyond the immediate session.</li>
                    <li><strong>No IP Address Logging:</strong> We do not store IP addresses or any persistent device identifiers.</li>
                </ul>
                <h2>4. Optional Features</h2>
                <ul>
                    <li>You will be informed of the specific data required.</li>
                    <li>Usage will be restricted to the stated purpose.</li>
                    <li>You will have the ability to opt out at any time.</li>
                </ul>
                <p>We do not support or integrate with third-party advertising or tracking platforms.</p>
                <h2>5. Your Privacy Rights</h2>
                <p>
                    We support and respect user privacy rights under applicable laws such as the California Consumer Privacy Act (CCPA) and the General Data Protection Regulation (GDPR).
                    You have the right to:
                </p>
                <ul>
                    <li>Access and view the data we hold about you (if any).</li>
                    <li>Request deletion of any information you’ve voluntarily submitted.</li>
                    <li>Withdraw consent for any optional features at any time.</li>
                </ul>
                <p>To exercise your rights, contact us at <a href="mailto:emailessencellc@gmail.com">emailessencellc@gmail.com</a>.</p>
                <h2>6. Data Retention</h2>
                <ul>
                    <li>All cached data is temporary, anonymized, and automatically purged after processing or upon session expiration.</li>
                    <li>Any voluntarily provided contact information (e.g., for support) is retained only for the duration of the correspondence and is deleted once no longer needed, unless otherwise required by law.</li>
                </ul>
                <h2>7. Children’s Privacy</h2>
                <p>
                    EmailEssence is intended for users aged 13 and above. We do not knowingly collect or store data from children under the age of 13. If we become aware that a child has used our service, we will take immediate steps to delete any associated data.
                </p>
                <h2>8. Changes to This Privacy Policy</h2>
                <p>
                    We may update this policy from time to time to reflect changes in our technology, legal requirements, or business practices. We will notify users of significant updates through our website or application.<br />
                    <strong>Last updated:</strong> 6/01/2025
                </p>
                <h2>9. Contact Information</h2>
                <p>
                    If you have any questions or concerns regarding this Privacy Policy or your data, please contact us at <a href="mailto:emailessencellc@gmail.com">emailessencellc@gmail.com</a>
                </p>
                <p>
                    <strong>EmailEssence Privacy Team</strong>
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