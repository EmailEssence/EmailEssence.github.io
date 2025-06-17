import { useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import Logo from "../../assets/Logo";
import "./Home.css";

export default function TermsOfService() {
  const navigate = useNavigate();
  const homeRef = useRef(null);
  const overviewRef = useRef(null);
  const aboutRef = useRef(null);

  /* Scrolls to the top */
  useEffect(() => { window.scrollTo(0, 0); }, []);

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

      <div className="terms-of-service">
        <h1>Terms of Service</h1>
        <p><strong>Effective Date:</strong> 6/01/2025<br />
          <strong>Last Updated:</strong> 6/01/2025</p>
        <p>
          Welcome to EmailEssence! By using our service, you agree to the
          following terms and conditions. If you do not agree, please do not
          use our service.
        </p>
        <h2>1. Acceptance of Terms</h2>
        <p>
          By accessing or using EmailEssence, you agree to be bound by these
          Terms of Service and our Privacy Policy. If you do not agree, you may
          not use our service.
        </p>
        <h2>2. User Responsibilities</h2>
        <p>
          You are responsible for maintaining the confidentiality of your
          account and password. You agree to notify us immediately of any
          unauthorized use of your account or any other breach of security.
          We will not be liable for any loss or damage arising from your
          failure to comply with this obligation.
        </p>
        <h2>3. Prohibited Activities</h2>
        <p>
          You agree not to engage in any of the following prohibited
          activities:
        </p>
        <ul>
          <li>Using the service for any illegal or unauthorized purpose</li>
          <li>
            Interfering with or disrupting the security, integrity, or
            performance of the service
          </li>
          <li>
            Attempting to gain unauthorized access to the service or its
            related systems or networks
          </li>
          <li>
            Transmitting any viruses, worms, or other malicious code
          </li>
          <li>
            Collecting or harvesting any personally identifiable information
            from other users
          </li>
          <li>
            Impersonating any person or entity or misrepresenting your
            affiliation with any person or entity
          </li>
          <li>
            Engaging in any other conduct that restricts or inhibits anyone's
            use or enjoyment of the service
          </li>
        </ul>
        <h2>4. Intellectual Property</h2>
        <p>
          All content, trademarks, and other intellectual property on the
          service are the property of EmailEssence or its licensors. You may
          not use, reproduce, distribute, or create derivative works from any
          content without our prior written consent.
        </p>
        <h2>5. Limitation of Liability</h2>
        <p>
          To the fullest extent permitted by law, EmailEssence shall not be
          liable for any indirect, incidental, special, consequential, or
          punitive damages arising out of or in connection with your use of
          the service, even if we have been advised of the possibility of
          such damages.
        </p>
        <h2>6. Changes to Terms</h2>
        <p>
          We reserve the right to modify these Terms of Service at any time.
          Your continued use of the service after any changes constitutes your
          acceptance of the new terms. We encourage you to review these terms
          periodically for any updates or changes.
        </p>
        <h2>7. Governing Law</h2>
        <p>
          These Terms of Service shall be governed by and construed in
          accordance with the laws of the jurisdiction in which EmailEssence
          operates, without regard to its conflict of law principles.
        </p>
        <p>
          By using EmailEssence, you acknowledge that you have read and
          understood these Terms of Service and agree to be bound by them.
        </p>
        <p><strong>
          Sincerely, The EmailEssence Team
        </strong></p>
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
