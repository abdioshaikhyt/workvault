import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import apiAuth from "../apiAuth";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import { useState, useEffect } from "react";
import useUserInfo from "./GetUsername";

function ProtectedSuperUserStaffRoute({ children }) {
  const [isAuthorized, setIsAuthorized] = useState(null);
  const [decoded, setDecoded] = useState(null);
  const { userId: jwtUserId } = useUserInfo();
  const [forceLogout, setForceLogout] = useState(false);

  useEffect(() => {
    auth().catch(() => {
      setIsAuthorized(false);
      setIsSuperUser(false);
    });

    // Refresh auth token every 15 min
    const intervalId = setInterval(() => {
      auth().catch(() => {
        setIsAuthorized(false);
        setIsSuperUser(false);
      });
    }, 15 * 60 * 1000);

    return () => clearInterval(intervalId);
  }, []);

  const refreshToken = async () => {
    const refreshToken = sessionStorage.getItem(REFRESH_TOKEN);
    try {
      const res = await apiAuth.post("/api/token/refresh/", {
        refresh: refreshToken,
      });
      if (res.status === 200) {
        sessionStorage.setItem(ACCESS_TOKEN, res.data.access);
        sessionStorage.setItem(REFRESH_TOKEN, res.data.refresh);
        return true;
      }
    } catch (error) {
      console.log(error);
    }
    return false;
  };

  const auth = async () => {
    const token = sessionStorage.getItem(ACCESS_TOKEN);
    if (!token) {
      setIsAuthorized(false);
      return;
    }

    let decoded;
    try {
      decoded = jwtDecode(token);
      setDecoded(decoded);
    } catch (error) {
      console.error("Invalid JWT token:", error);
      setIsAuthorized(false);
      return;
    }

    const tokenExpiration = decoded.exp;
    const now = Date.now() / 1000;

    if (tokenExpiration < now) {
      const refreshed = await refreshToken();
      if (!refreshed) {
        setIsAuthorized(false);
        return;
      }
      decoded = jwtDecode(sessionStorage.getItem(ACCESS_TOKEN));
      setDecoded(decoded);
    }

    
  };

  useEffect(() => {
    if (decoded === null) return;
    if (decoded.practice_superuser === true || decoded.is_staff === true) {
      console.log("nav to admin");
      setIsAuthorized(true);
    } else {
       console.log("nav no");
      setIsAuthorized(false);
    }
  }, [decoded]);

  useEffect(() => {
        const token = sessionStorage.getItem(ACCESS_TOKEN);
        const scheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsUrl = `${scheme}://${window.location.host}/ws/currentuser/?token=${token}`; 
        const ws1 = new WebSocket(wsUrl);

  ws1.onopen = () => {
    console.log("[WS] Connected to /ws/currentuser/");
  };

  ws1.onmessage = (event) => {
    const data = JSON.parse(event.data);
   

    if (data.type === "force_logout" && Number(data.user_id) === Number(jwtUserId)) {
      setForceLogout(true);
    } else if (data.type === "force_logout") {
    }
  };

  ws1.onerror = (error) => {
    console.error("[WS] WebSocket error:", error);
  };

  ws1.onclose = () => {
    console.log("[WS] Disconnected from /ws/currentuser/");
  };

  return () => {
    ws1.close();
  };
}, [jwtUserId]);

if (forceLogout) {
        return <Navigate to = "/Logout"/>
    }

  if (isAuthorized === null) {
    return <div>Loading...</div>;
  }

  if (!isAuthorized) {
    return <Navigate to="*" />;
  }

  

  return children;
}

export default ProtectedSuperUserStaffRoute;
