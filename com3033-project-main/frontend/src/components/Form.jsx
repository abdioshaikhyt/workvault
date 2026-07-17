import { useState, useRef, useEffect } from "react";
import apiAuth, { BASE_URL } from "../apiAuth.js";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import LoadingIndicator from "./LoadingIndicator";
import { jwtDecode } from "jwt-decode";
import "../styles/Form.css";
import "altcha";



function Form({ route, method }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [practiceName, setPracticeName] = useState("");
    const [loading, setLoading] = useState(false);
    const [captchaToken, setCaptchaToken] = useState(null);
    const [captchaChallenge, setCaptchaChallenge] = useState(null);
    const [submitalert, setSubmitalert] = useState(false);
    const [errorMessage, setErrorMessage] = useState([]);
    const navigate = useNavigate();


    const widgetRef = useRef(null); // ref for the widget element


      // Attach ALTCHA success event listener
    useEffect(() => {
    const widget = widgetRef.current;
    if (!widget) return;

    const handler = (ev) => {
        console.log("[ALTCHA] statechange:", ev.detail);
        if (ev.detail.state === "verified") {
            setCaptchaToken(ev.detail.payload);
            const challenge = ev.detail.challenge; // most modern builds expose this
            setCaptchaChallenge(challenge);
            console.log("[ALTCHA] token captured:", ev.detail.payload);
        }
    };

    widget.addEventListener("statechange", handler);
    return () => {
        widget.removeEventListener("statechange", handler);
    };
  }, []);
      // if name is login or Login return the login captchapage Else return return registration form

    const name = method === "login" ? "Login" : "Register"
    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault()
        setErrorMessage([]);

        try {

            const data = { username, password, captcha: captchaToken, challenge: captchaChallenge };
            if (method === "register") {
                data.email = email;
                data.practice_name = practiceName;
                data.first_name = firstName;
                data.last_name = lastName;
            }

            const res = await apiAuth.post(route, data);
            if (method === "login") {
                sessionStorage.setItem(ACCESS_TOKEN, res.data.access);
                sessionStorage.setItem(REFRESH_TOKEN, res.data.refresh);
                const decoded = jwtDecode(res.data.access);

                  if (decoded.is_staff === true && decoded.practice_superuser === false) {

                    navigate("/admin_panel");

                  } else {

                    navigate("/dashboard");

                    }

            } else {

                setSubmitalert(true);

                setTimeout(() => navigate("/"), 2000);

            } 

            
            
        } catch (error) {
            setLoading(false);
            setSubmitalert(false);

            if (error.response?.data) {
                const errs = [];
                for (const key in error.response.data) {
                    if (Array.isArray(error.response.data[key])) {
                        errs.push(...error.response.data[key]);
                    } else if (typeof error.response.data[key] === "string") {
                        errs.push(error.response.data[key]);
                    }
                }
                setErrorMessage(errs.length ? errs : ["An unexpected error occurred."]);
            } else {
                setErrorMessage(["Network error. Please try again."]);
            }


        }
    };

    return (
    <form onSubmit={handleSubmit} className="form-container">
      <h1>{name}</h1>

      {/* Username */}
      <div className="form-input-wrapper">
        <input
          className="form-input"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
        />
      </div>

      {/* Email (register only) */}
      {method === "register" && (
        <>
        <div className="form-input-wrapper">
            <input
              className="form-input"
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="First Name"
              required
            />
          </div>
          <div className="form-input-wrapper">
            <input
              className="form-input"
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Last Name"
              required
            />
          </div>
        <div className="form-input-wrapper">
          <input
            className="form-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email (Optional)"
          />
        </div>
        <div className="form-input-wrapper">
            <input
              className="form-input"
              type="text"
              value={practiceName}
              onChange={(e) => setPracticeName(e.target.value)}
              placeholder="Practice Name"
              required
            />
          </div>
          </>
      )}

      {/* Password */}
      <div className="form-input-wrapper">
        <input
          className="form-input with-icon"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        {method === "register" && (
          <div className="tooltip-container">
            <span className="info-icon">i</span>
            <div className="tooltip-text">
              Password must:
              <ul>
                <li>Be at least 8 characters</li>
                <li>Not be too common</li>
                <li>Not be entirely numeric</li>
                <li>Not be blank</li>
                <li>Not be too similar to your username/email</li>
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* ALTCHA widget */}
      <altcha-widget
        ref={widgetRef}
        name="captcha"
        workers="16"
        hidefooter="true"
        debug
        const challengeurl = {`${BASE_URL}/api/altcha/challenge/`}
        //const challengeurl={`${import.meta.env.VITE_AUTH_API_URL}/api/altcha/challenge/`}
        style={{ margin: "15px 0", display: "block" }}
      ></altcha-widget>
     

      {/* Error messages */}
      {errorMessage.length > 0 && (
        <div style={{ color: "red", marginBottom: "10px" }}>
          <ul style={{ paddingLeft: "20px", margin: 0 }}>
            {errorMessage.map((msg, index) => (
              <li key={index}>{msg}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Register success message */}
      {method === "register" && submitalert && (
        <>
          <div style={{ color: "black", marginBottom: "10px" }}>
            Please wait until verification has completed before logging in.
          </div>
          <div style={{ color: "black", marginBottom: "10px" }}>
            Redirecting...
          </div>
        </>
      )}

      {loading && <LoadingIndicator />}

      <button className="form-button" type="submit" style={{ marginBottom: "10px" }}>
        {name}
      </button>

      {/* Login page extra buttons */}
      {method === "login" && (
        <>
          <button
            className="form-button"
            type="button"
            style={{ marginTop: "10px" }}
            onClick={() => navigate("/Register")}
          >
            Register
          </button>
          <p>
            <a
              href="/request/password_reset"
              style={{ color: "blue", textDecoration: "underline" }}
            >
              forgotten password?
            </a>
          </p>
        </>
      )}
    </form>
  );
}

export default Form;