import React, { useEffect, useState, useRef } from "react";
import apiSearch from "../apiSearch"; // Your API wrapper (axios, etc)
import { useLocation, useNavigate } from "react-router-dom";
import { useSearch } from "../components/SearchContext";
import Layout from "../components/Layout";

function useQueryParams() {
  // Helper to get query params as object
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  return {
    q: params.get("q") || "",
    page: parseInt(params.get("page") || "1", 10)

  };
}

function SearchResults() {
  const location = useLocation();
  const navigate = useNavigate();
  const { setSearchTerm } = useSearch();
  const pageSize = 2; // can be changed as required
  const { q: urlQuery, page: urlPage } = useQueryParams();
  const [results, setResults] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [firstLoad, setFirstLoad] = useState(true);
  //const cacheRef = useRef({});

  // Sync search bar (global) with URL state
  useEffect(() => {
    setSearchTerm(urlQuery);
  }, [urlQuery, setSearchTerm]);

  useEffect(() => {
    setFirstLoad(true);
    //cacheRef.current = {};
  }, [urlQuery]);

  // Fetch results when query/page changes
  useEffect(() => {
    if (!urlQuery) {
      setResults([]);
      setTotalCount(0);
      return;
    }


    setError(null);
    if (firstLoad) setLoading(true);
    
    const offset = (urlPage - 1) * pageSize;
    apiSearch
      .get("/search/jobs/", { params: { q: urlQuery, limit: pageSize, offset } })
      .then((response) => {
        const results = response.data.results || [];
        const totalCount = response.data.count || 0;

        // Update state with new data
        setResults(results);
        setTotalCount(totalCount);

      })
      .catch(() => setError("Error fetching data"))
      .finally(() => {
        if (firstLoad) setLoading(false);
          setFirstLoad(false); 
      });
  }, [urlQuery, urlPage, pageSize]);

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  // Pagination: update page number in URL!
  const handlePageChange = (newPage) => {
    // Clamp page value
    if (newPage < 1 || newPage > totalPages) return;
    const params = new URLSearchParams();
    if (urlQuery) params.set("q", urlQuery);
    params.set("page", newPage);
    navigate(`/search?${params.toString()}`);
  };




  return (
    <Layout>
      <div>
        {error && <p style={{ color: "red" }}>{error}</p>}

        <ul>
          {loading && <li>Loading...</li>}

          {!loading && results.length === 0 && (
            <li>No results found</li>
          )}
          {results.map((job, idx) => (
            <li
            key={job.job_id}
            style={{ cursor: "pointer", color: "blue", textDecoration: "underline" }}
            onClick={() => navigate(`/job_detail/${job.job_id}`)} 

          >
              
              <p>
                <strong>{job.company_name} Period End: </strong>
                {new Date(job.period_end).toLocaleDateString('en-GB')}
                <strong> - </strong>{job.job_selection} - {job.alt_description}
              </p>
              
            </li>
          ))}

        </ul>
        {/* Pagination Controls */}
        {totalPages > 0 && (
          <div style={{ marginTop: "20px" }}>
            <button
              onClick={() => handlePageChange(urlPage - 1)}
              disabled={urlPage === 1}
            >
              Previous
            </button>
            <span style={{ margin: "0 10px" }}>
              Page {urlPage} of {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(urlPage + 1)}
              disabled={urlPage === totalPages}
            >
              Next
            </button>
          </div>)}
       
      </div>
    </Layout>
  );
}

export default SearchResults;