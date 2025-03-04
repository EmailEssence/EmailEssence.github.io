/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */
import styles from "./login.module.css";
import { baseUrl } from "../../emails/emailParse";
import { useEffect } from "react";
// import Logo from "../../assets/Logo";

export const OAuthCallback = ({ forward }) => {
  useEffect(() => {
    const handleCallback = async () => {
      const hash = window.location.hash;
      if (hash && hash.startsWith("#auth=")) {
        try {
          const encodedState = hash.substring(6);
          const authState = JSON.parse(decodeURIComponent(encodedState));

          if (authState.authenticated && authState.token) {
            // Token is already verified by backend
            forward(authState.token);
            window.location.hash = "";
            return;
          }
        } catch (error) {
          console.error("Error parsing auth state:", error);
        }
      }
    };
    handleCallback();
  }, [forward]);

  return null;
};

export const Login = ({ forward }) => {
  const hash = window.location.hash;
  if (hash && hash.startsWith("#auth=")) {
    return <OAuthCallback forward={forward} />;
  }

  const handleLogin = async () => {
    // Check for auth hash and render OAuthCallback if present
    try {
      const response = await fetch(`${baseUrl}/auth/login`);
      const data = await response.json();
      if (data.authorization_url) {
        window.location.href = data.authorization_url;
      }
    } catch (error) {
      console.error("Login Error", error);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.formBox}>
        <div className={styles.loginDiv}>
          <div className={styles.loginIcon}>
            {/* <Logo /> */}
            <img src="./src/assets/oldAssets/Logo.svg" alt="Logo Icon" />
          </div>
          <p className={styles.title}>Welcome Back</p>
          <button onClick={handleLogin} className={styles.googleButton}>
            Login with Google
          </button>
        </div>
      </div>
    </div>
  );
};
// return (
//     <div className={styles.page}>
//       <div className={styles.formBox}>
//         <div className={styles.loginDiv}>
//           <div className={styles.loginIcon}>
//             <img
//               src="./src/assets/Logo.PNG"
//               alt="Login Icon"
//               className={styles.loginPhoto}
//             />
//           </div>
//           <p className={styles.title}>Welcome Back</p>
//           <div className={styles.signUpLink}>
//             Don't have an account yet?{" "}
//             <a href="#" onClick={onSignUpClick}>
//               Sign up
//             </a>
//           </div>

//           <form className={styles.loginInput}>
//             <div>
//               <label htmlFor="email"></label>
//               <input
//                 className={styles.inputBox}
//                 type="email"
//                 id="email"
//                 name="email"
//                 placeholder="Email Address"
//               />
//             </div>
//             <div>
//               <label htmlFor="password"></label>
//               <input
//                 className={styles.inputBox}
//                 type="password"
//                 id="password"
//                 name="password"
//                 placeholder="Password"
//               />
//             </div>
//             <div>
//               <input
//                 onClick={forward} //forwards to dashboard for the meantime
//                 className={styles.loginButton}
//                 type="submit"
//                 value="Login"
//               />
//             </div>
//           </form>
//           <button onClick={handleGoogleLogin} className={styles.googleButton}>
//             Login with Google
//           </button>
//         </div>
//       </div>
//     </div>
// );
// }
