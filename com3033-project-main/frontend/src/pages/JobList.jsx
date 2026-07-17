import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import apiBook from "../apiBook";
import Layout from "../components/Layout";

function useQueryParams() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  return {
    staffLevel: params.get("staff_level") || "",
    page: parseInt(params.get("page") || "1", 10),
  };
}

function JobList() {
  const navigate = useNavigate();
  const { staffLevel: urlStaffLevel, page: urlPage } = useQueryParams();

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nextUrl, setNextUrl] = useState(null);
  const [prevUrl, setPrevUrl] = useState(null);
  const [totalCount, setTotalCount] = useState(0);

  const pageSize = 3; 

  useEffect(() => {
    if (!urlStaffLevel) {
      setJobs([]);
      setNextUrl(null);
      setPrevUrl(null);
      setTotalCount(0);
      return;
    }

    setLoading(true);
    setError(null);

    apiBook
      .get("/job_list/", { params: { staff_level: urlStaffLevel, page: urlPage, page_size: pageSize } })
      .then((resJobs) => {
        const data = resJobs.data;
        setJobs(Array.isArray(data) ? data : data.results || []);
        setNextUrl(data.next);
        setPrevUrl(data.previous);
        setTotalCount(data.count || 0);
      })
      .catch((err) => {
        setJobs([]);
        setNextUrl(null);
        setPrevUrl(null);
        setTotalCount(0);
        setError(err.response?.data?.detail || err.message || "Failed to fetch data");
      })
      .finally(() => setLoading(false));
  }, [urlStaffLevel, urlPage, pageSize]);

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  const handleStaffLevelChange = (event) => {
    const selected = event.target.value;
    // Reset to page 1 when staff level changes
    const params = new URLSearchParams();
    if (selected) params.set("staff_level", selected);
    params.set("page", "1");
    navigate(`?${params.toString()}`);
  };

  const handlePageChange = (newPage) => {
    if (newPage < 1) return;
    const params = new URLSearchParams();
    if (urlStaffLevel) params.set("staff_level", urlStaffLevel);
    params.set("page", newPage.toString());
    params.set("page_size", pageSize.toString());
    navigate(`?${params.toString()}`);
  };

  return (
    <Layout>
      <div>
        <label htmlFor="staffLevelSelect">Select Staff Level: </label>
        <select id="staffLevelSelect" value={urlStaffLevel} onChange={handleStaffLevelChange}>
          <option value="">Please select</option>
          <option value="reviewer_staff">Reviewer Staff</option>
          <option value="partner_staff">Partner Staff</option>
          <option value="preparer_staff">Preparer Staff</option>
        </select>

        {loading && <p>Loading jobs...</p>}
                
          <>
            <table>
              <thead>
                <tr>
                  <th>Client name</th>
                  <th>Period end</th>
                  <th>Job category</th>
                  <th>CT comp stage</th>
                </tr>
              </thead>
              <tbody>
                {jobs.length > 0 ? (
                  jobs.map((job, idx) => (
                    <tr 
                    key={idx}
                    onClick={() => navigate(`/job_detail/${job.id}`)}
                    style={{cursor:'pointer', color:'blue'}}
                    >
                      <td>{job.client?.company_name}</td>
                      <td>{job.period_end}</td>
                      <td>{job.job_selection}</td>
                      <td>{job.comp_stage}</td>
                    </tr>
                  ))
                ) : !urlStaffLevel && !error ? (
                  <tr>
                    <td colSpan={4} style={{ textAlign: "center" }}>
                      Please select staff level
                    </td>
                  </tr>
                ) : (
                  <tr>
                    <td colSpan={4} style={{ textAlign: "center" }}>
                      {error && <p style={{ color: "red" }}>{error}</p>}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            <div style={{ marginTop: "1em" }}>
              <button onClick={() => handlePageChange(urlPage - 1)} disabled={!prevUrl || loading}>
                Previous
              </button>
              <span style={{ margin: "0 1em" }}>
                Page {urlPage} of {totalPages}
              </span>
              <button onClick={() => handlePageChange(urlPage + 1)} disabled={!nextUrl || loading}>
                Next
              </button>
            </div>
          </>
       
      </div>
    </Layout>
  );
}

export default JobList;
