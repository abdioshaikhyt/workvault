import React, { useEffect, useState } from "react";
import apiAuth from "../apiAuth"; 
import Layout from "../components/Layout";
import { useLocation, useNavigate } from "react-router-dom";
import useUserInfo from "../components/GetUsername"; 
function AdminList() {
  const [users, setUsers] = useState([]);
  const [practices, setPractices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [nextUrlusers, setNextUrlusers] = useState(null);
  const [prevUrlusers, setPrevUrlusers] = useState(null);
  const [totalCountusers, setTotalCountusers] = useState(0);
  const [nextUrlpractices, setNextUrlpractices] = useState(null);
  const [prevUrlpractices, setPrevUrlpractices] = useState(null);
  const [totalCountpractices, setTotalCountpractices] = useState(0);
  const [pageusers, setPageUsers] = useState(1);
  const [pagepractices, setPagePractices] = useState(1);
  const navigate = useNavigate();

  const pageSize = 10; 

  // Modal state
  const [modal, setModal] = useState({
    visible: false,
    userId: null,
    field: null,
    newValue: null,
  });

  // Get logged-in user's ID from JWT
  const { userId: jwtUserId, isStaff} = useUserInfo();

  useEffect(() => {
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${scheme}://${window.location.host}/ws/users/`);

  ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.event === "user_updated" && data.user) {
    setUsers(prev =>
      prev.map(user =>
        user.id === data.user.id
          ? { ...user, ...data.user }
          : user
      )
    );
  } else if (data.event === "user_created" && data.user) {
    setUsers(prev => {
      // Only add if not already present
      if (prev.some(user => user.id === data.user.id)) return prev;
      return [...prev, data.user];
    });
  }
  else if (data.event === "practice_created" && data.practice) {
    setPractices(prev => {
      // Only add if not already present
      if (prev.some(practice => practice.id === data.practice.id)) return prev;
      return [...prev, data.practice];
    });
  }
};
  return () => ws.close();
}, []);


  useEffect(() => {
    setLoading(true);
    setError(null);

    const fetchUsers = apiAuth.get("/api/users/", { params: { page: pageusers, page_size: pageSize } });
    let fetchPractices = Promise.resolve({ data: { results: [], next: null, previous: null, count: 0 } });
    if (isStaff) {
      fetchPractices = apiAuth.get("/api/practices/", { params: { page: pagepractices, page_size: pageSize } });
    }

    Promise.all([fetchUsers, fetchPractices])
      .then(([resUsers, resPractices]) => {
        setUsers(resUsers.data.results || []);
        setNextUrlusers(resUsers.data.next);
        setPrevUrlusers(resUsers.data.previous);
        setTotalCountusers(resUsers.data.count || 0);

        if (isStaff) {
          setPractices(resPractices.data.results || []);
          setNextUrlpractices(resPractices.data.next);
          setPrevUrlpractices(resPractices.data.previous);
          setTotalCountpractices(resPractices.data.count || 0);
        }
      })
      .catch(err => setError(err.response?.data?.detail || err.message || "Failed to fetch data"))
      .finally(() => setLoading(false));
  }, [pageusers, pagepractices, isStaff]);

  const totalPagesusers = Math.max(1, Math.ceil(totalCountusers / pageSize));
  const totalPagespractices = Math.max(1, Math.ceil(totalCountpractices / pageSize));

  // Handlers update local state directly (no URL)
  const handlePageChangeusers = (newPage) => {
    if (newPage < 1 || newPage > totalPagesusers) return;
    setPageUsers(newPage);
  };

  const handlePageChangepractices = (newPage) => {
    if (newPage < 1 || newPage > totalPagespractices) return;
    setPagePractices(newPage);
  };

  // Helper to PATCH user and update local state
  const patchUser = async (userId, data) => {
    try {
      await apiAuth.patch(`/api/users/${userId}/update/`, data);
      setUsers((prev) =>
        prev.map((user) =>
          user.id === userId ? { ...user, ...data } : user
        )
      );
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Failed to update user"
      );
    }
  };

  // Handle toggling is_active
  const handleActiveToggle = (userId, currentActive) => {
    console.log("handleActiveToggle called:", { userId, currentActive, jwtUserId });
    // Only show modal if user is unticking their own checkbox
    if (Number(jwtUserId) === Number(userId) && currentActive) {
      console.log("Showing modal for deactivating self");
      setModal({
        visible: true,
        userId,
        field: "is_active",
        newValue: false,
      });
    } else {
      console.log("Patching user (active toggle)");
      patchUser(userId, { is_active: !currentActive });
    }
  };

  // Handle toggling is_staff
  const handleStaffToggle = (userId, currentStaff) => {
    console.log("handleStaffToggle called:", { userId, currentStaff, jwtUserId });
    if (Number(jwtUserId) === Number(userId) && currentStaff) {
      console.log("Showing modal for removing own staff");
      setModal({
        visible: true,
        userId,
        field: "is_staff",
        newValue: false,
      });
    } else {
      console.log("Patching user (staff toggle)");
      patchUser(userId, { is_staff: !currentStaff });
    }
  };

  // Handle toggling practice_superuser
  const handlePracticeSuperuserToggle = (userId, currentValue) => {
    console.log("handlePracticeSuperuserToggle called:", { userId, currentValue, jwtUserId });

    // Example: if you want modal confirmation when user tries to remove their own superuser
    if (Number(jwtUserId) === Number(userId) && currentValue) {
      console.log("Showing modal for removing own practice_superuser");
      setModal({
        visible: true,
        userId,
        field: "practice_superuser",
        newValue: false,
      });
    } else {
      console.log("Patching user (practice_superuser toggle)");
      patchUser(userId, { practice_superuser: !currentValue });
    }
  };

  // Modal handlers
  const handleConfirm = async () => {
    console.log("Modal confirmed", modal);
    const { userId, field, newValue } = modal;
    setModal({ visible: false, userId: null, field: null, newValue: null });
    await patchUser(userId, { [field]: newValue });

    if (
    Number(jwtUserId) === Number(userId) && 
    field && 
    newValue === false && 
    (field === "is_active" || field === "is_staff" || field === "practice_superuser")
  ) {
    console.log("Navigating to Logout");
    navigate("/Logout");
  }
  };

  const handleCancel = () => {
    console.log("Modal canceled");
    setModal({ visible: false, userId: null, field: null, newValue: null });
  };

  if (loading) return <p>Loading users...</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error}</p>;

  const staffUsers = users.filter(user => user.is_staff && user.is_active);
  const staffCount = staffUsers.length;
  const activeCount = users.filter((user) => user.is_active).length;

  let lastActiveUserId = null;
  if (staffCount === 1) {
    lastActiveUserId = staffUsers[0].id;
  }

  return (
    <Layout>
      <ConfirmModal
        visible={modal.visible}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
        field={modal.field}
      />
      <>
        <div>
          <h2>User Admin List</h2>
          <table>
            <thead>
              <tr>
                <th>User ID</th>
                <th>Username</th>
                <th>First name</th>
                <th>Last name</th>
                <th>Practice</th>
                <th>Active</th>
                {isStaff && <th>Staff</th>}
                <th>Practice_Superuser</th>
                
              </tr>
            </thead>
            <tbody>
              {users
                .slice()
                .sort((a, b) => a.id - b.id)
                .map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.username}</td>
                    <td>{user.first_name}</td>
                    <td>{user.last_name}</td>
                    <td>{user.practice_display_name}</td>
                    <td>
                      <input
                        type="checkbox"
                        checked={user.is_active}
                        onChange={() =>
                          handleActiveToggle(user.id, user.is_active)
                        }
                      />
                    </td>
                    {isStaff && (
                      <td>
                        <input
                          type="checkbox"
                          checked={user.is_staff}
                          onChange={() =>
                            handleStaffToggle(user.id, user.is_staff)
                          }
                        />
                      </td>
                    )}
                    <td>
                      <input
                        type="checkbox"
                        checked={user.practice_superuser}
                        onChange={() =>
                          handlePracticeSuperuserToggle(
                            user.id,
                            user.practice_superuser
                          )
                        }
                      />
                    </td>
                    <td>
                      <button
                        onClick={() =>
                          navigate(`/admin/change-password/${user.id}`)
                        }
                      >
                        Change Password
                      </button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          <div>
           
            <table>
            </table>
            <div style={{ marginTop: "1em" }}>
              <button onClick={() => handlePageChangeusers(pageusers - 1)} disabled={!prevUrlusers || loading}>Previous</button>
              <span style={{ margin: "0 1em" }}>Page {pageusers} of {totalPagesusers}</span>
              <button onClick={() => handlePageChangeusers(pageusers + 1)} disabled={!nextUrlusers || loading}>Next</button>
            </div>
          </div>
        </div>
        {isStaff && (
        
        <div>
          <h2>Practice List</h2>
          <table>
            <thead>
              <tr>
                <th>Practice ID</th>
                <th>Practice name</th>
              </tr>
            </thead>
            <tbody>
              {practices
                .slice()
                .sort((a, b) => a.id - b.id)
                .map((practice) => (
                  <tr key={practice.id}>
                    <td>{practice.id}</td>
                    <td>{practice.practice_name}</td>
                  </tr>
                ))}
            </tbody>
          </table>
          
            <div>
              
              <table>
              </table>
              <div style={{ marginTop: "1em" }}>
                <button onClick={() => handlePageChangepractices(pagepractices - 1)} disabled={!prevUrlpractices || loading}>Previous</button>
                <span style={{ margin: "0 1em" }}>Page {pagepractices} of {totalPagespractices}</span>
                <button onClick={() => handlePageChangepractices(pagepractices + 1)} disabled={!nextUrlpractices || loading}>Next</button>
              </div>
              <button onClick={() => navigate("/new_practice")}>Add Practice</button>
            </div>
          
          
        </div>
        )}
      </>
    </Layout>
  );
}

function ConfirmModal({ visible, onConfirm, onCancel, field }) {
  console.log("ConfirmModal visible?", visible);
  if (!visible) return null;
  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
      }}
    >
      <div
        style={{
          background: "white",
          padding: 24,
          borderRadius: 8,
          minWidth: 300,
          textAlign: "center",
        }}
      >
        <p>
          Are you sure you want to set your own <b>{field}</b> to <b>false</b>?<br />
          You will be logged out!
        </p>
        <button onClick={onConfirm} style={{ marginRight: 16 }}>
          Yes
        </button>
        <button onClick={onCancel}>No</button>
      </div>
    </div>
  );
}

export default AdminList;