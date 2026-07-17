import React, { useState } from "react";

function StageFilesAccordion({ existingStageFiles, renderStageTabs }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    
      <div>

      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          background: "none",
          border: "none",
          padding: 0,
          cursor: "pointer",
          fontWeight: "bold",
          fontSize: "18px",
          display: "flex",
          alignItems: "center",
          gap: "6px",
          userSelect: "none",
        }}
        aria-expanded={isOpen}
      >
        <span
          style={{
            transform: isOpen ? "rotate(90deg)" : "rotate(0)",
            display: "inline-block",
            transition: "transform 0.3s ease",
          }}
        >
          ▶
        </span>
        Stage file versions
      </button>
      
    {isOpen && (
        <>
      <div
      style={{
        border: "2px dashed #ccc",
        background: "#fafafa",
        padding: "32px",
        borderRadius: "12px",
        textAlign: "center",
        marginBottom: "16px"
      }}
    >
        <>

      {/* Render the stage tabs */}
      <div>{renderStageTabs()}</div>

      
        <ul style={{ marginTop: "12px", paddingLeft: "20px" }}>
          {existingStageFiles.map((file) => (
            <li key={file.id}>
              <a href={file.url} target="_blank" rel="noopener noreferrer">
                {file.name}
              </a>
            </li>
          ))}
        </ul>
        </>
        </div>
        </>
      )}
    </div>
    
  );
}

export default StageFilesAccordion;
