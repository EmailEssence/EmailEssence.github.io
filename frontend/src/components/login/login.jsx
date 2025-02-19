/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */
import styles from "./login.module.css";
import { baseUrl } from "../../emails/emailParse";
import { useEffect } from "react";

export const OAuthCallback = (forward) => {
  useEffect(() => {
    const handleCallback = async () => {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code");

      if (code) {
        try {
          // Exchange code for token
          const response = await fetch(`${baseUrl}/auth/callback?code=${code}`);
          // const data = await response.json();

          // Check auth status
          const statusResponse = await fetch(`${baseUrl}/auth/status`);
          const statusData = await statusResponse.json();
          if (statusData.is_authenticated) {
            // :)
            forward();
          } else {
            console.error("Authentication failed");
          }
        } catch (error) {
          console.error("Auth callback Error", error);
        }
      } else {
        console.error("No code found in URL");
      }
    };
    handleCallback();
  }, [forward]);

  return <div>Completing sign in...</div>;
};

export const Login = ({ forward }) => {
  const handleLogin = async () => {
    try {
      const response = await fetch(`${baseUrl}/auth/login`);
      const data = await response.json();
      if (data.authorization_url) {
        window.open(data.authorization_url, "_blank");
        //https://ee-backend-w86t.onrender.com/auth/callback?state=3kcnwylQpcgVHUziNLC6rDcYcPyoRB&code=4%2F0ASVgi3JA0nLePkt6ii6OtB4_P1O9TlnwPNbd_-0ZDs7DSGGPH0TpCL1EOIHlZcxS9bzIYQ&scope=https%3A%2F%2Fmail.google.com%2F
      }
    } catch (error) {
      console.error("Login Error", error);
    }
  };

  const params = new URLSearchParams(window.location.search);
  const code = params.get("code");

  if (code) {
    return <OAuthCallback forward={forward} />;
  }

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
