import React, { useEffect, useState } from "react";
import apiCourses from "../apiCourses"; // import your axios instance


export default function CourseList() {
  const [courses, setCourses] = useState([]);
  const [offset, setOffset] = useState(0);
  const [ordering, setOrdering] = useState("date"); // "date" or "-date"
  const [totalCount, setTotalCount] = useState(0);
  const LIMIT = 5;

  useEffect(() => {
    async function fetchCourses() {
      try {
        const params = {
          offset,
          limit: LIMIT,
          ordering,

        };
        const response = await apiCourses.get("/courses/", { params });
        const data = response.data;

        setCourses(data.results || []);
        setTotalCount(data.count || 0);
      } catch (error) {
        console.error("Failed to fetch courses", error);
      }
    }
    fetchCourses();
  }, [offset, ordering]);

  const handleNext = () => {
    if (offset + LIMIT < totalCount) {
      setOffset(offset + LIMIT);
    }
  };

  const handleBack = () => {
    if (offset - LIMIT >= 0) {
      setOffset(offset - LIMIT);
    }
  };


  const toggleOrder = () => {
    setOrdering(ordering === "date" ? "-date" : "date");
    setOffset(0);

  };

 return (
  <div style={{ border: "1px solid #ccc", padding: 16, borderRadius: 8 }}>
    <h2>Courses</h2>
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th>Title</th>
          <th>
            Date{" "}
            <button onClick={toggleOrder} style={{ cursor: "pointer" }}>
              {ordering === "date" ? "▲" : "▼"}
            </button>
          </th>
          <th>CPD Hours</th>
          <th>Type</th>
        </tr>
      </thead>
      <tbody>
        {courses.length === 0 && (
          <tr>
            <td colSpan={4} style={{ textAlign: "center" }}>
              No courses found.
            </td>
          </tr>
        )}
        {courses.map((course, idx) => (
          <tr key={idx} style={{ borderTop: "1px solid #eee" }}>
            <td>
              <a
                href={course.link.replace(/^\[|\]$/g, "")}
                target="_blank"
                rel="noopener noreferrer"
              >
                {course.title}
              </a>
            </td>
            <td>
              {course.date
                ? new Date(course.date).toLocaleDateString()
                : course.date_special}
            </td>
            <td>{course.cpd_hours}</td>
            <td>{course.course_type}</td>
          </tr>
        ))}
      </tbody>
    </table>

    <div
      style={{
        marginTop: 16,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <button onClick={handleBack} disabled={offset === 0}>
        Back
      </button>
      <div>
        Page {Math.floor(offset / LIMIT) + 1} of{" "}
        {Math.ceil(totalCount / LIMIT)}
      </div>
      <button onClick={handleNext} disabled={offset + LIMIT >= totalCount}>
        Next
      </button>
    </div>
  </div>
);
}