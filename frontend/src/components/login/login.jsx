import "./login.css";

// eslint-disable-next-line react/prop-types
export default function Login({ forward }) {
  return (
    <div className="formBox">
      <div className="loginDiv">
        <div className="loginIcon">
          <img src="./src/assets/Logo.PNG" alt="Login Icon" className="loginPhoto" />
        </div>
        <p className="title">Welcome Back</p>
        <div className="signUpLink"> Don't have an account yet? <a href="./register">Sign up</a></div>
        <form className="loginInput">
          <div>
            <label htmlFor="email"></label>
            <input
              className="inputBox"
              type="email"
              id="email"
              name="email"
              placeholder="Email Address"
            />
          </div>
          <div>
            <label htmlFor="password"></label>
            <input
              className="inputBox"
              type="password"
              id="password"
              name="password"
              placeholder="Password"
            />
          </div>
          <div>
            <input
              onClick={forward}
              className="loginButton"
              type="submit"
              value="Login"
            />
          </div>
        </form>
      </div>
    </div>
  );
}
