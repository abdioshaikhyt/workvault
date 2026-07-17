import { useState } from "react";
import apiAuth from "../apiAuth";
import { useNavigate } from "react-router-dom";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";

const PasswordResetRequest = () => {
  const [email, setEmail] = useState("");
  const [submitalert, setSubmitalert] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    setLoading(true);
    e.preventDefault();
    setErrorMessage("");

    try {
      const data = { email };
      const res = await apiAuth.post("/api/password_reset/", data);
      setSubmitalert(true);

      setTimeout(() => {
        setLoading(false); 
        navigate(-1);
      }, 3000);
      
    } catch (error) {
      if (error.response) {
        const data = error.response.data;
        if (data.email && Array.isArray(data.email)) {
          setErrorMessage(data.email[0]);
        } else {
          setErrorMessage("An unexpected error occurred.");
        }
      } else {
        setErrorMessage("Network error. Please try again.");
      }
      setLoading(false);
    } 
  };

  return (
    <form onSubmit={handleSubmit} className="form-container">
      <h1>Forgotten Password</h1>
      <div className="form-input-wrapper">
      <input
        className="form-input"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      </div>

      {errorMessage && (
        <div style={{ color: "red", marginBottom: "10px" }}>
            {errorMessage}
        </div>
      )}

      {submitalert && (
        <>
        <div style={{ color: "black", marginBottom: "10px" }}>
            You will receive an email with instructions on how to reset your password.
        </div>
        <div style={{ color: "black", marginBottom: "10px" }}>
            Redirecting...
        </div>
        </>
      )}

      {loading && <LoadingIndicator />}

      <button className="form-button" type="submit" style={{ marginBottom: "10px" }}>
        Send email
      </button>
    </form>
  );
};

export default PasswordResetRequest;