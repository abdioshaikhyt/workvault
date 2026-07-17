import React from "react";
import { useEffect, useState } from "react";
import apiAuth from "../apiAuth";
import apiBook from "../apiBook";
import apiFiles from "../apiFiles";
import apiSearch from "../apiSearch"
import apiCourses from "../apiCourses";

function Logout() {
    useEffect(() =>{
        const refreshToken = sessionStorage.getItem("refresh");
        // 1. Blacklist access token (GET)
        // 2. Blacklist refresh token (POST)

    Promise.all([
      apiBook.get("/logout/"),
      apiSearch.get("/logout/"),
      apiFiles.get("/logout/"),
      apiCourses.get("/logout/"),
      apiAuth.post("/api/logout/", { refresh: refreshToken })
    ])
      .catch((error) => {
        console.error("Logout error:", error);
      })
      .finally(() => {
        sessionStorage.clear();
        localStorage.setItem('logout', Date.now());
  // Redirect or update UI in this tab
        window.location.href = '/';
    });},[]);
}

export default Logout;
