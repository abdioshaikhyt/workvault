import React, { useState } from "react";
import apiAuth from "../apiAuth";
import Layout from "../components/Layout";

function NewPractice() {
  const [practice_name, setPractice_name] = useState("");
  
  const createPractice = (e) => {
    e.preventDefault();
    apiAuth.post("/api/practices/create/", { practice_name })
      .then((res) => {
        if (res.status === 201) {
          alert("Practice created!");
          setPractice_name("");
        } else {
          alert("Failed to create practice.");
        }
      })
      .catch((err) => alert(err));
  };

  return (
    <Layout>
      <h2>Create a Practice</h2>
      <form onSubmit={createPractice}>
        <label htmlFor="practice_name">Practice name:</label>
        <br />
        <input
          type="text"
          id="practice_name"
          name="practice_name"
          required
          value={practice_name}
          onChange={(e) => setPractice_name(e.target.value)}
        />
        <br />
        <br />
        <button className="form-button" type="submit" style={{ marginBottom: "10px" }}>
        Add Practice
        </button>
      </form>
    </Layout>
  );
}

export default NewPractice;