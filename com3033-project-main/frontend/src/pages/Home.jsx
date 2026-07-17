
import React, { useEffect, useState } from "react";
import apiBook from "../apiBook";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import CourseList from "../components/CourseList";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import SearchProvider, { useSearch } from "../components/SearchContext";
function Home() {
  
  const [bookTitle, setBookTitle] = useState("");
  const [bookTitle2, setBookTitle2] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();



const [jobs, setJobs] = useState([]);

  useEffect(() => {
    // Connect to WebSocket on mount
    const token = sessionStorage.getItem(ACCESS_TOKEN);
    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${scheme}://${window.location.host}/ws/backend1/currentuser/?token=${token}`; 
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "job_list") {
        if (data.event === "userjob_updated" && Array.isArray(data.jobs)) {
          setJobs((prevJobs) => {
            const updatedJobs = [...prevJobs];
            data.jobs.forEach((job) => {
              const index = updatedJobs.findIndex((j) => j.id === job.id);
              if (index > -1) {
                // Update existing job
                updatedJobs[index] = job;
              } else {
                // Add new job
                updatedJobs.push(job);
              }
            });
            return updatedJobs;
          });
        } else if (data.event === "userjob_removed" && Array.isArray(data.job_ids)) {
          setJobs((prevJobs) => {
            // Remove jobs with matching IDs
            return prevJobs.filter((job) => !data.job_ids.includes(job.id));
          });
        } else if (data.event === "initial_load" && Array.isArray(data.jobs)) {
          // Optional: initial load can replace whole list
          setJobs(data.jobs);
        }
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error", error);
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
    };

    // Cleanup on unmount
    return () => {
      ws.close();
    };
  }, []);


  return (
    <Layout>
    <div>
      <h1>Your Dashboard</h1>
      
      
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
          
    </div>
    <CourseList />
    <div>
      <h2>Your CT Compliance Workflows</h2>
      {jobs.length === 0 ? (
        <p>None</p>
      ) : (
        <ul>
          {jobs.map((job) => (
            <li
              key={job.id}
              style={{ cursor: "pointer", color: "blue", textDecoration: "underline" }}
              onClick={() => navigate(`/job_detail/${job.id}`)}
            >
              {job.client__company_name} - Period End: {job.period_end} - Status: {job.comp_stage}  
              
            </li>
          ))}
        </ul>
      )}
      </div>
    </Layout>
  );
}

export default Home;