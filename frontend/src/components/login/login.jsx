/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */
import styles from "./login.module.css";
import { baseUrl } from "../../emails/emailParse";
import { useEffect } from "react";

export const OAuthCallback = ({ forward }) => {
  useEffect(() => {
    const handleCallback = async () => {
      const hash = window.location.hash;
      if (hash && hash.startsWith("#auth=")) {
        try {
          // Decode the auth state from URL hash
          const encodedState = hash.substring(6);
          const authState = JSON.parse(decodeURIComponent(encodedState));

          if (authState.authenticated && authState.token) {
            // check auth
            const statusResponse = await fetch(`${baseUrl}/auth/status`);
            const statusData = await statusResponse.json();

            if (statusData.is_authenticated) {
              // :)
              forward(authState.token); // Pass the token to forward
              window.location.hash = ""; // Clear the hash
            } else {
              console.error("Authentication check failed");
            }

            // ~.io/#auth={"authenticated"%3A true%2C "token"%3A "ya29.a0AXeO80QTFy3oQBh9U388oFBMeWfKeXtlPA7xDtJwgyvI11q9pborOhhhM0meWmbaUSx3pPyG3I6a0Aa4jXzKfj8_699t4Xbhb-Bdx0YX9GP2QFtJ0moixSIwphlXaQsSVYBtpxas4UKUgjXPLU6IyUnQKTu1-0naM4w7wAvtRwaCgYKAcwSARMSFQHGX2MiKJ_nWI2bcb5uTKCjxZ8ZGA0177"}
            // Check auth status
          }
        } catch (error) {
          console.error("Error parsing auth state:", error);
        }
      } else {
        console.error("No hash found in URL");
      }
    };
    handleCallback();
  }, [forward]);

  return <div>Completing sign in...</div>;
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
            <img
              src="./src/assets/Logo.svg"
              alt="Login Icon"
              className={styles.loginPhoto}
            />
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
