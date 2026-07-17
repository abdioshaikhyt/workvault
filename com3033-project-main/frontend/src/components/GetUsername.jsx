//GetUsername.jsx
import { useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";

export default function useUserInfo() {
  const [userInfo, setUserInfo] = useState({
    username: null,
    isStaff: null,
    userId: null,
    practice_superuser: null,
    practice_id: null,
  });

  useEffect(() => {
    const token = sessionStorage.getItem("access");
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setUserInfo({
          username: decoded.username || decoded.user || decoded.sub || null,
          isStaff: typeof decoded.is_staff !== "undefined" ? decoded.is_staff : null,
          userId: decoded.user_id || decoded.id || null,
          practice_superuser: typeof decoded.practice_superuser !== "undefined" ? decoded.practice_superuser : null,
          practice_id: decoded.practice_id || null,
        });
      } catch (e) {
        setUserInfo({ username: null, isStaff: null, userId: null, practice_superuser: null, practice_id: null});
      }
    } else {
      setUserInfo({ username: null, isStaff: null, userId: null, practice_superuser: null, practice_id: null });
    }
  }, []);

  return userInfo;
}

