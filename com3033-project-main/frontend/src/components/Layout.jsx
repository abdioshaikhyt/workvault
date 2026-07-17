
import React, { Fragment, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSearch } from "./SearchContext";
import useUserInfo from "../components/GetUsername";
import apiAuth from "../apiAuth";


function Layout({ children }) {
  const navigate = useNavigate();
  const {searchTerm, setSearchTerm } = useSearch();
  const { userId: jwtUserId, isStaff, practice_superuser} = useUserInfo();
  const [displayName, setDisplayName] = useState("");

  // Trigger redirect on Enter
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && searchTerm.trim() !== "") {
      navigate(`/search?q=${encodeURIComponent(searchTerm.trim())}`);
      // Optional: don't clear searchTerm so it remains visible
    }
  };

  useEffect(() => {
  apiAuth.get("api/user/display_name/")
    .then(res => {
      setDisplayName(res.data.display_name);
      
    })
    
    .catch((error) => {
      setError(error.response?.data?.detail || error.message);
    })
    
}, []);

  return (
    <div>
      {!isStaff && (
        <Fragment>
      {/* Global search bar */}
      <input
        type="text"
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Search client jobs..."
        style={{ width: "300px", marginRight: "16px" }}
      />
      {/* Navigation bar and header content */} 
      <button style={{ float: "left" , marginRight: "16px"}} onClick={() => navigate("/dashboard")}>Dashboard</button>
      <button style={{ float: "left" , marginRight: "16px"}} onClick={() => navigate("/new_client")}>New Client</button>
      <button style={{ float: "left" , marginRight: "16px"}} onClick={() => navigate("/client_list")}>Client List</button>
      <button style={{ float: "left" , marginRight: "16px"}} onClick={() => navigate("/new_job")}>New Job</button>
      <button style={{ float: "left" , marginRight: "16px"}} onClick={() => navigate("/job_list")}>Job List</button>
      </Fragment>
      )}
      
      {practice_superuser && (
        <button style={{ float: "left" , marginRight: "16px"}} onClick={() => navigate("/admin_panel")}>
          Admin Panel
        </button>
      )}
      <strong>{displayName}</strong>
      <button style={{ marginLeft: "50px", float: "centre" }} onClick={() => navigate("/Logout")}>Logout</button>
      <div style={{ clear: "both" }} />
      
      {children}
    </div>
  );
}

export default Layout;