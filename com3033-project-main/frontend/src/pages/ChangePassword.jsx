import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import apiAuth from "../apiAuth";

import "../styles/Form.css";
import LoadingIndicator from "../components/LoadingIndicator";

function ChangePassword() {
  const { userId } = useParams();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitalert, setSubmitalert] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    setLoading(true);
    e.preventDefault();
    setErrorMessage([]);
    setSubmitalert(false);

    if (password !== confirmPassword) {
      setLoading(false);
      setErrorMessage(["Passwords do not match."]);
      return;
    }

    try {
      await apiAuth.patch(`/api/users/${userId}/update/`, {
        password,
      });

      setSubmitalert(true);
      setTimeout(() => {
        setLoading(false); // Optional: stop loading just before redirect
        navigate(-1);
      }, 3000);
      
    } catch (error) {
      if (error.response) {
        const data = error.response.data;
        const messages = [];

        for (const key in data) {
          if (Array.isArray(data[key])) {
            messages.push(...data[key]);
          } else if (typeof data[key] === "string") {
            messages.push(data[key]);
          }
        }

        if (messages.length > 0) {
          setErrorMessage(messages);
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
      <h1>Change Password for User {userId}</h1>

      <div className="form-input-wrapper">
        <input
          className="form-input with-icon"
          type="password"
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
              <li>Not be too similar to your username/email</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Confirm Password Field */}
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

      {errorMessage && errorMessage.length > 0 && (
        <div style={{ color: "red", marginBottom: "10px" }}>
          <ul style={{ paddingLeft: "20px", margin: 0 }}>
            {errorMessage.map((msg, index) => (
              <li key={index}>{msg}</li>
            ))}
          </ul>
        </div>
      )}

      {submitalert && (
        <div style={{ color: "black", marginBottom: "10px" }}>
          Password changed successfully. Redirecting...
        </div>
      )}

      {loading && <LoadingIndicator />}

      <button className="form-button" type="submit" style={{ marginBottom: "10px" }}>
        Submit Password
      </button>
    </form>
  );
}

export default ChangePassword;

