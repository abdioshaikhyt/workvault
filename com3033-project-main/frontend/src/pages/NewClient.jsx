import React from "react";
import { useState, useEffect } from "react";
import apiBook from "../apiBook";
import {useNavigate} from "react-router-dom";
import useUserInfo from "../components/GetUsername";
import Layout from "../components/Layout";

function NewClient() {
    const [company_name, setCompany_name] = useState("");
    const [contact_name, setContact_name] = useState("");
    const [contact_email, setContact_email] = useState("");

  const { userId: jwtUserId, practice_id} = useUserInfo();

  const createClient = (e) => {
    e.preventDefault();
    apiBook.post("/clients/create/", { company_name, contact_name, contact_email, practice_id })
      .then((res) => {
        if (res.status === 201) {
          alert("Client created!");
          setCompany_name("");
          setContact_name("");
          setContact_email("");
          
        } else {
          alert("Failed to create client.");
        }
      })
      .catch((err) => alert(err));
  };

  return (
    <Layout>
    <h2>Create a Client</h2>
      <form onSubmit={createClient}>
        <label htmlFor="company_name">Company name:</label>
        <br />
        <input
          type="text"
          id="company_name"
          name="company_name"
          required
          value={company_name}
          onChange={(e) => setCompany_name(e.target.value)}
        />
        <br />

        <label htmlFor="contact_name">Contact name:</label>
        <br />
        <input
          type="text"
          id="contact_name"
          name="contact_name"
          required
          value={contact_name}
          onChange={(e) => setContact_name(e.target.value)}
        />
        <br />

        <label htmlFor="contact_email">Contact email:</label>
        <br />
        <input
          type="email"
          id="contact_email"
          name="contact_email"
          required
          value={contact_email}
          onChange={(e) => setContact_email(e.target.value)}
          
        />
        <br />

        <br />

        <button className="form-button" type="submit" style={{ marginBottom: "10px" }}>
        Add Client
        </button>
      </form>
    </Layout>



  
  );
}

export default NewClient;