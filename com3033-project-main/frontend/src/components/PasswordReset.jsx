import React, { useEffect, useState } from "react";
import api from "../apiAuth";
import { useParams, useNavigate } from "react-router-dom";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";

const PasswordReset = () => {
  
  const {token} = useParams();
  const [submitalert, setSubmitalert] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState(""); 
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [tokenValid, setTokenValid] = useState(null); // null = loading, true = valid, false = expired

useEffect(() => {
  const validateToken = async () => {
    try {
      await api.post("/api/validate-reset-token/", { token });
      setTokenValid(true); // Token is valid
    } catch (error) {
      setTokenValid(false); // Token invalid or expired
    }
  };

  validateToken();
}, [token]);

if (tokenValid === false) {
  return (
    <div className="form-container">
      <h1>Link Expired</h1>
      <div style={{ textAlign: "center", color: "red", marginTop: "20px" }}>
  <p>This password reset link has expired.</p>
  <p>
    <a href="/request/password_reset">Click here to request another one.</a>
  </p>
</div>
    </div>
  );
}

  const handleSubmit = async (e) => {
    setLoading(true);
    e.preventDefault();
    setErrorMessage("");

    if (password !== confirmPassword) {
      setLoading(false);
      setErrorMessage(["Passwords do not match."]);
      return;
    }

    try {
      const data = { password, token };
      const res = await api.post("/api/password_reset/confirm/", data);
      setSubmitalert(true);
      setTimeout(() => {
        setLoading(false); // Optional: stop loading just before redirect
        navigate("/login");
      }, 3000);
      
    } catch (error) {
        if (error.response) {
            const data = error.response.data;

            // Collect all error messages into an array
            const messages = [];

            for (const key in data) {
            if (Array.isArray(data[key])) {
                messages.push(...data[key]); // Add all messages from this field
            } else if (typeof data[key] === "string") {
                messages.push(data[key]); // Add string message if not an array
            }
            }

            if (messages.length > 0) {
            // Replace specific OTP error with custom message
              const updatedMessages = messages.map((msg) =>
                msg === "The OTP password entered is not valid. Please check and try again."
                ? "Please request a new forgotten password link as this has expired."
                : msg
              );
              setErrorMessage(updatedMessages);
            } else {
            setErrorMessage(["An unexpected error occurred."]);
            }
        } else {
            setErrorMessage(["Network error. Please try again."]);
        }
    setLoading(false);
  } 
};
  return (
    <form onSubmit={handleSubmit} className="form-container">
      <h1>Reset Password</h1>

  <div className="form-input-wrapper">
    <input
      type="password"
      className="form-input with-icon"
      value={password}
      onChange={(e) => setPassword(e.target.value)}
      placeholder="New Password"
      required
    />
    <div className="tooltip-container">
      <span className="info-icon">i</span>
      <div className="tooltip-text">
        Password must:
        <ul>
          <li>Be at least 8 characters</li>
          <li>Not be too common</li>
          <li>Not be entirely numeric</li>
          <li>Not be blank</li>
          <li>Not too similar to your username/email</li>
        </ul>
      </div>
    </div>
  </div>

  {/* Confirm Password */}
  <div className="form-input-wrapper">
    <input
      className="form-input"
      type="password"
      value={confirmPassword}
      onChange={(e) => setConfirmPassword(e.target.value)}
      placeholder="Confirm Password"
      required
    />
  </div>

      {/* Error messages */}
      {errorMessage && errorMessage.length > 0 && (
        <div style={{ color: "red", marginBottom: "10px" }}>
          <ul style={{ paddingLeft: "20px", margin: 0 }}>
            {errorMessage.map((msg, index) => (
              <li key={index}>{msg}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Submit alert */}
      {submitalert && (
        <>
          <div style={{ color: "black", marginBottom: "10px" }}>
            Your password reset has been successful.
          </div>
          <div style={{ color: "black", marginBottom: "10px" }}>
            Redirecting...
          </div>
        </>
      )}

      {loading && <LoadingIndicator />}

      <button className="form-button" type="submit" style={{ marginBottom: "10px" }}>
        Submit Password
      </button>
    </form>
  );
};

export default PasswordReset;