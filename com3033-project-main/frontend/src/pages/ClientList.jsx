import React, { Fragment } from "react";
import { useEffect, useState } from "react";
import Layout from "../components/Layout"
import { useLocation, useNavigate } from "react-router-dom";
import apiBook from "../apiBook";

function useQueryParams() {
    const location = useLocation();
    const params = new URLSearchParams(location.search);
    return {
        page: parseInt(params.get("page") || "1", 10),
    };
}

function ClientList(){
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [nextUrl, setNextUrl] = useState(null);
    const [prevUrl, setPrevUrl] = useState(null);
    const [totalCount, setTotalCount] = useState(0);

    const navigate = useNavigate();
    const {page} = useQueryParams();
    const pageSize = 3; //Change according to backend pagination page_size

    useEffect(() => {
        setLoading(true);
        setError(null);

        apiBook.get("/clients/list", {params: {page, page_size: pageSize}}).
        then((res) => {
            const data = res.data;
            setClients(data.results || []);
            setNextUrl(data.next);
            setPrevUrl(data.previous);
            setTotalCount(data.count || 0);
        }).catch((err) => {setError(err.response?.data?.detail || err.message || "Failed to fetch data");

        }).finally(() => setLoading(false));
    },[page]);

    const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

    const handlePageChange = (newPage) =>{
        if (newPage < 1 || newPage > totalPages) return;
        const params = new URLSearchParams();
        params.set("page", newPage);
        navigate(`?${params.toString()}`)
    };

    return (
        <Layout>
                <div>
                    {loading && <p>Loading...</p>}
                    {error && <p style={{color : "red"}}>{error}</p>}

                    {!loading && !error && (
                        <Fragment>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Company name</th>
                                        <th>Contact name</th>
                                        <th>Contact email</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {clients.length > 0 ? (
                                        clients.map((client) => (
                                        <tr key={client.id}>
                                            <td>{client.company_name}</td>
                                            <td>{client.contact_name}</td>
                                            <td>{client.contact_email}</td>
                                        </tr>
                                        ))
                                    ) : (
                                        <tr>
                                        <td colSpan="3">No results found</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                                                
                                <div style={{ marginTop: "1em" }}>

                                    <button onClick={() => handlePageChange(page - 1)} disabled={!prevUrl || loading}>
                                        Previous
                                    </button>

                                    <span style={{ margin: "0 1em" }}>
                                        Page {page} of {totalPages}
                                    </span>

                                    <button onClick={() => handlePageChange(page + 1)} disabled={!nextUrl || loading}>
                                        Next
                                    </button>
                                </div>

                                <button onClick={() => navigate("/new_client")}>Add Client</button>

                    </Fragment>
                    )}
                </div>

        </Layout>
    );
}

export default ClientList;