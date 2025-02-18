import styles from "./login.module.css";

export default function Login({ forward, onSignUpClick }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  // // Function to handle form submission
  // const handleSubmit = async (e) => {
  //   e.preventDefault();

  //   // Send a POST request to the server
  //   const response = await fetch("", {
  //     method: "POST",
  //     headers: {
  //       "Content-Type": "application/json",
  //     },
  //     body: JSON.stringify({ email, password }),
  //   });

  //   // Handle the response
  //   const data = await response.json();
  //   if (data.error) {
  //     setError(data.error);
  //   } else {
  //     forward(data); // forward to the next page
  //   }
  // }

  return (
    <div className={styles.page}>
      <div className={styles.formBox}>
        <div className={styles.loginDiv}>
          <div className={styles.loginIcon}>
            <img src="./src/assets/Logo.PNG" alt="Login Icon" className={styles.loginPhoto} />
          </div>
          <p className={styles.title}>Welcome Back</p>
          <div className={styles.signUpLink}>
            Don't have an account yet? <a href="#" onClick={onSignUpClick}>Sign up</a>
          </div>
          {/* {error && <div className={styles.error}>{error}</div>}  */}
          <form className={styles.loginInput}  /*onSubmit={handleSubmit}*/> 
            <div>
              <label htmlFor="email"></label>
              <input
                className={styles.inputBox}
                type="email"
                id="email"
                name="email"
                placeholder="Email Address"
                // value={email}
                // onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password"></label>
              <input
                className={styles.inputBox}
                type="password"
                id="password"
                name="password"
                placeholder="Password"
                // value={password}
                // onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div>
              <input
                onClick={forward} //forwards to dashboard for the meantime
                className={styles.loginButton}
                type="submit"
                value="Login"
              />
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
