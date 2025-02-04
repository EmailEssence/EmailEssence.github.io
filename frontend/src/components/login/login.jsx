import "./login.css";

// eslint-disable-next-line react/prop-types
export default function Login({forward}) {
  return (
    <div className="loginDiv">
      <p className="title">Registration Form</p>

      <form className="App">
        <div>
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            name="username"
            placeholder="Enter your username"
          />
        </div>
        <div>
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            name="email"
            placeholder="Enter your email"
          />
        </div>
        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            name="password"
            placeholder="Enter your password"
          />
        </div>
        <div>
          <input
            onClick={forward}
            type="submit"
            value="Register"
            style={{backgroundColor: "#a1eafb"}}
          />
        </div>
      </form>
    </div>
  );
}
