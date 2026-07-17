import { useState } from 'react'
import { Suspense, lazy, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom"
import Login from "./pages/Login"
import Register from './pages/Register'
import Home from './pages/Home'
import NotFound from './pages/NotFound'
import NewPractice from './pages/NewPractice'
import NewJob from './pages/NewJob'
import NewClient from './pages/NewClient'
import PasswordResetRequest from './components/PasswordResetRequest'
import ProtectedRoute from './components/ProtectedRoute'
import ProtectedSuperUserStaffRoute from './components/ProtectedSuperUserStaffRoute'
import ChangePassword from './pages/ChangePassword'
import JobList from './pages/JobList'
import SearchProvider from './components/SearchContext'
import ClientList from "./pages/ClientList"
import LandingPage from './pages/LandingPage'
import AdminList from './pages/AdminList'
import ProtectedStaffRoute from './components/ProtectedStaffRoute'
import JobDetail from './pages/JobDetail'
import SearchResults from './pages/SearchResults'
import PasswordReset from './components/PasswordReset'
import Logout from "./components/Logout"

function ClearCacheAndRegister() {
  sessionStorage.clear()
  return <Register />
}


function App() {
  const navigate = useNavigate();

  useEffect(() => {
    const syncLogout = (event) => {
      if (event.key === "logout") {
        console.log("Logged out from another tab");
        // Clear any in-memory auth state here if present

        // Redirect to logout page
        navigate("/Logout");
        localStorage.clear();
      }
    };

    window.addEventListener("storage", syncLogout);
    return () => window.removeEventListener("storage", syncLogout);
  }, [navigate]);

  return (
   
      
    <Routes>
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <SearchProvider>
              <Suspense>
                <Home />
              </Suspense>
            </SearchProvider>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/change-password/:userId"
        element={
          <ProtectedSuperUserStaffRoute>
            <SearchProvider>
              <Suspense>
                <ChangePassword />
              </Suspense>
            </SearchProvider>
          </ProtectedSuperUserStaffRoute>
        }
      />

      <Route
        path="/admin_panel"
        element={
          <ProtectedSuperUserStaffRoute>
            <SearchProvider>
              <Suspense>
                <AdminList />
              </Suspense>
            </SearchProvider>
          </ProtectedSuperUserStaffRoute>
        }
      />

      <Route
        path="/new_practice"
        element={
          <ProtectedStaffRoute>
            <SearchProvider>
              <Suspense>
                <NewPractice />
              </Suspense>
            </SearchProvider>
          </ProtectedStaffRoute>
        }
      />

      <Route
        path="/new_client"
        element={
          <ProtectedRoute>
            <SearchProvider>
              <Suspense>
                <NewClient />
              </Suspense>
            </SearchProvider>
          </ProtectedRoute>
        }
      />

      <Route
        path="/new_job"
        element={
          <ProtectedRoute>
            <SearchProvider>
              <Suspense>
                <NewJob />
              </Suspense>
            </SearchProvider>
          </ProtectedRoute>
        }
      />

      <Route
        path="/job_detail/:id"
        element={
          <ProtectedRoute>
            <SearchProvider>
              <Suspense>
                <JobDetail />
              </Suspense>
            </SearchProvider>
          </ProtectedRoute>
        }
      />

      <Route
        path="/client_list"
        element={
          <ProtectedRoute>
            <SearchProvider>
              <Suspense>
                <ClientList />
              </Suspense>
            </SearchProvider>
          </ProtectedRoute>
        }
      />

      <Route
        path="/job_list"
        element={
          <ProtectedRoute>
            <SearchProvider>
              <Suspense>
                <JobList />
              </Suspense>
            </SearchProvider>
          </ProtectedRoute>
        }
      />

      <Route
        path="/search"
        element={
          <ProtectedRoute>
            <SearchProvider>
              <Suspense>
                <SearchResults />
              </Suspense>
            </SearchProvider>
          </ProtectedRoute>
        }
      />

      <Route
        path="/"
        element={
          <Suspense>
            <LandingPage />
          </Suspense>
        }
      />

       <Route
        path="/login"
        element={
          <Suspense>
            <Login />
          </Suspense>
        }
      />

      <Route
        path="/Logout"
        element={
          <Suspense fallback={<div>Loading...</div>}>
            <Logout />
          </Suspense>
        }
      />

      <Route
        path="/Register"
        element={
          <Suspense>
            <ClearCacheAndRegister />
          </Suspense>
        }
      />

      <Route
        path="/request/password_reset"
        element={
          <Suspense>
            <PasswordResetRequest />
          </Suspense>
        }
      />

      <Route
        path="/password-reset/:token"
        element={
          <Suspense>
            <PasswordReset />
          </Suspense>
        }
      />

      <Route
        path="*"
        element={
          <Suspense fallback={<div>Loading...</div>}>
            <NotFound />
          </Suspense>
        }
      />
    

      </Routes>

    
  );
}

export default App;
