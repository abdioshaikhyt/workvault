import React, { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import apiBook from "../apiBook";
import apiFiles from "../apiFiles";
import Layout from "../components/Layout";
import useUserInfo from "../components/GetUsername";
import { refreshToken } from "../components/ProtectedRoute";
import StageFilesAccordion from "../components/StageFilesAccordion";
import SearchablePaginatedDropdown from "../components/SearchablePaginatedDropdown";
function JobDetail() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
 
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);
  const navigate = useNavigate();

  // Staff list for dropdowns
  const [staffList, setStaffList] = useState([]);

  // Editable field states
  const [altDescription, setAltDescription] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [partnerStaffId, setPartnerStaffId] = useState("");
  const [reviewerStaffId, setReviewerStaffId] = useState("");
  const [preparerStaffId, setPreparerStaffId] = useState("");
  const [clientName, setClientName] = useState("");
  const [partnerStaffName, setPartnerStaffName] = useState("");
  const [reviewerStaffName, setReviewerStaffName] = useState("");
  const [preparerStaffName, setPreparerStaffName] = useState("");
  const partnerInputRef = useRef();
  const reviewerInputRef = useRef();
  const preparerInputRef = useRef();
  const [selectedPartnerText, setPartnerSelectedText] = useState("");
  const [selectedReviewerText, setReviewerSelectedText] = useState("");
  const [selectedPreparerText, setPreparerSelectedText] = useState("");
  const [periodEndError, setPeriodEndError] = useState("");
  const [bug, setbug] = useState(0);
 

  // Display-only states
  const [jobSelection, setJobSelection] = useState("");
  const [compStage, setCompStage] = useState("");
  const [practiceId, setPracticeId] = useState("");
  const [taskWithStaff, setTaskWithStaff] = useState("");

  const [partnerstafferror, setPartnerStaffError] = useState("");
  const [reviewerstafferror, setReviewerStaffError] = useState("");
  const [preparerstafferror, setPreparerStaffError] = useState("");

  
  const [originalJob, setOriginalJob] = useState(null);

  const [files, setFiles] = useState([]);           // Files queued for upload
  const [existingFiles, setExistingFiles] = useState([]); // Already existing files from backend

  const [existingStageFiles, setExistingStageFiles] = useState([]);

  const [message, setMessage] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const { userId: jwtUserId, practice_id} = useUserInfo();
  
  const compStageToStageOptionMap = {
      
      Planning_draft: 'planning_draft_version',
      Planning_review: 'planning_review_version',
      Comp_draft: 'comp_draft_version',
      Comp_review: 'comp_review_version',
      Tax_accounting_approved: 'tax_accounting_approved_version',
      Finalisation_prep: 'finalisation_prep_version',
      Finalisation_review: 'finalisation_review_version',
      With_Client_for_approval: 'with_client_for_approval_version',
      Approved: 'approved_version',
      Submitted: 'submitted_version',
    };
  
  const stageKeys = Object.values(compStageToStageOptionMap);
    
  const [selectedStage, setSelectedStage] = useState(null);


  const fetchFiles = async () => {
  if (!id || !selectedStage && (compStage!="NA")) return;
  try {
    const res = await apiFiles.get(`/files_read/${id}/`, { params: { stage: selectedStage } });
    setExistingStageFiles(res.data);
  } catch {
    setExistingStageFiles([]);
  }
};

useEffect(() => {
  fetchFiles();
}, [id, selectedStage]);
    
  
  const fetchJob = () => {
    setLoading(true);
    setError(null);
    apiBook.get(`/jobs/${id}/`)
      .then(res => {
        const job = res.data;
        setAltDescription(job.alt_description || "");
        setPeriodStart(job.period_start || "");
        setPeriodEnd(job.period_end || "");
        setPartnerStaffId(job.partner_staff?.staff_id || "");
        setReviewerStaffId(job.reviewer_staff?.staff_id || "");
        setPreparerStaffId(job.preparer_staff?.staff_id || "");
        setPartnerStaffName(job.partner_staff?.display_name || "");
        setReviewerStaffName(job.reviewer_staff?.display_name || "");
        setPreparerStaffName(job.preparer_staff?.display_name || "");
        setPartnerSelectedText(job.partner_staff?.display_name || "");
        setReviewerSelectedText(job.reviewer_staff?.display_name || "");
        setPreparerSelectedText(job.preparer_staff?.display_name || "");
        setClientName(job.client?.company_name || "");
        setJobSelection(job.job_selection || "");
        setCompStage(job.comp_stage || "");
        setPracticeId(job.practice_id || "");
        setTaskWithStaff(job.task_with_staff?.display_name || "");
        setOriginalJob(job);  // save original for comparison
        console.log("Original job data loaded:", job);
        const initial_version = compStageToStageOptionMap[job.comp_stage];
        const currentIndex = stageKeys.indexOf(initial_version);
        const newStage = currentIndex > 0 ? (job.comp_stage==="Approved" ? stageKeys[currentIndex] : (job.comp_stage==="Submitted" ? stageKeys[currentIndex] : stageKeys[currentIndex - 1])) : stageKeys[0];
        setSelectedStage(newStage);
      })
      .catch(err => setError(err.response?.data?.detail || err.message || "Failed to load job"))
      .finally(() => setLoading(false));
  };

  

  const fetchExistingFiles = async () => {
    try {
      const res = await apiFiles.get(`/files/${id}/`);
      setExistingFiles(res.data);
    } catch {
      setExistingFiles([]);
    }
  };

  
  useEffect(() => {
      setPeriodEndError("");
      if (periodStart && periodEnd) {
        if (new Date(periodEnd) < new Date(periodStart)) {
          setPeriodEndError("Period End must be after Period Start");
        }
      }
    }, [periodStart, periodEnd]);

  useEffect(() => {
    fetchJob();
   
    fetchExistingFiles();
    const tokenExpiryMs = 1 * 60 * 1000;

    const timerId = setTimeout(() => {
      // call your refresh token API here to get a new access token
      // update access token in storage/state on success
      refreshToken();
    }, tokenExpiryMs);

    // Cleanup on unmount or token change
    return () => clearTimeout(timerId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // Stage change with updated fields and control to allow refresh afterwards
  const changeStage = (direction) => {
    if (updating) return;
    setError(null);
    setUpdating(true);
    setPartnerStaffError("");
    setReviewerStaffError("");
    setPreparerStaffError("");
   

    let hasError = false;

    const currentPartnerInput = partnerInputRef.current?.value || "";
    if (!partnerStaffId || currentPartnerInput.trim() !== selectedPartnerText) {
      setPartnerStaffError("Please select a Partner Staff");
      hasError = true;
    }
    const currentReviewerInput = reviewerInputRef.current?.value || "";
    if (!reviewerStaffId || currentReviewerInput.trim() !== selectedReviewerText) {
      setReviewerStaffError("Please select a Reviewer Staff");
      hasError = true;
    }
    const currentPreparerInput = preparerInputRef.current?.value || "";
    if (!preparerStaffId || currentPreparerInput.trim() !== selectedPreparerText) {
      setPreparerStaffError("Please select a Preparer Staff");
      hasError = true;
    }

    if (periodEndError){
      hasError = true;
    }

    if (hasError) {
      // Cancel submit if any error
      setUpdating(false);
      console.log("Validation failed - polluting inputs");
      return;
    }

    const payload = { direction };

    if (originalJob) {
      if (altDescription !== (originalJob.alt_description || "")) {
        payload.alt_description = altDescription;
      }
      if (periodStart !== (originalJob.period_start || "")) {
        payload.period_start = periodStart;
      }
      if (periodEnd !== (originalJob.period_end || "")) {
        payload.period_end = periodEnd;
      }
      if (partnerStaffId !== (originalJob.partner_staff?.staff_id || "")) {
        payload.partner_staff = partnerStaffId;
      }
      if (reviewerStaffId !== (originalJob.reviewer_staff?.staff_id || "")) {
        payload.reviewer_staff = reviewerStaffId;
      }
      if (preparerStaffId !== (originalJob.preparer_staff?.staff_id || "")) {
        payload.preparer_staff = preparerStaffId;
      }
    } else {
      // fallback send all
      payload.alt_description = altDescription;
      payload.period_start = periodStart;
      payload.period_end = periodEnd;
      payload.partner_staff = partnerStaffId;
      payload.reviewer_staff = reviewerStaffId;
      payload.preparer_staff = preparerStaffId;
    }

    apiBook.patch(`/jobs/${id}/advance/`, payload)
      .then(res => {
        const data = res.data;
        if(data.task_with_staff) setTaskWithStaff(data.task_with_staff);
        if(data.comp_stage === "Planning_review") fetchFiles(); 
        if(data.comp_stage === "Planning_draft") fetchFiles();
        const compStageKeys = Object.keys(compStageToStageOptionMap);
        let currentIndex = compStageKeys.indexOf(compStage);
        if (direction === "forward") {
          if(bug===1){setbug(0); setCompStage (compStageKeys[0]);}
          else {
          const nextIndex = Math.min(currentIndex + 1, compStageKeys.length - 1);
          setCompStage(compStageKeys[nextIndex])}
        } else if (direction === "backward") {
          const prevIndex = Math.max(currentIndex - 1, -1);
          if (prevIndex===-1) {setCompStage (compStageKeys[0]); setbug(1);}
          else setCompStage(compStageKeys[prevIndex]);
        }

        setOriginalJob(prev => ({
          ...prev,
          alt_description: payload.alt_description !== undefined ? payload.alt_description : prev.alt_description,
          period_start: payload.period_start !== undefined ? payload.period_start : prev.period_start,
          period_end: payload.period_end !== undefined ? payload.period_end : prev.period_end,
          partner_staff: payload.partner_staff !== undefined
            ? { ...prev.partner_staff, staff_id: payload.partner_staff }
            : prev.partner_staff,
          reviewer_staff: payload.reviewer_staff !== undefined
            ? { ...prev.reviewer_staff, staff_id: payload.reviewer_staff }
            : prev.reviewer_staff,
          preparer_staff: payload.preparer_staff !== undefined
            ? { ...prev.preparer_staff, staff_id: payload.preparer_staff }
            : prev.preparer_staff,
          task_with_staff: payload.task_with_staff !== undefined
            ? { ...prev.task_with_staff, staff_id: payload.task_with_staff }
            : prev.task_with_staff,  
          
        }));

      })
      .catch(err => {
        const detail = err.response?.data?.detail;
        if (detail && detail === "Cannot move further in this direction.") {
          // do nothing special
        } else {
          setError(detail || err.message || "Failed to change stage");
        }
      })
      .finally(() => setUpdating(false));
  };

  if (loading) return <Layout><p>Loading...</p></Layout>;
  if (error) return <Layout><p>Error: {error}</p></Layout>;







  
  
 

  

  // File input (click select) handler
  const handleFileChange = e => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  // Drag over
  const handleDragOver = e => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  // Drag leave
  const handleDragLeave = e => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  // Drop handler (supports folders)
  const handleDrop = e => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const items = e.dataTransfer.items;
    if (items) {
      for (let i = 0; i < items.length; i++) {
        const item = items[i].webkitGetAsEntry && items[i].webkitGetAsEntry();
        if (item) {
          readEntryFlatten(item);
        }
      }
    } else {
      // Fallback: normal files
      const droppedFiles = Array.from(e.dataTransfer.files);
      setFiles(prev => [...prev, ...droppedFiles]);
    }
  };

  // Recursively read files from directories, ignoring their folder paths
  const readEntryFlatten = (entry) => {
    if (entry.isFile) {
      entry.file(file => {
        // Ignore subfolder names, just push file
        setFiles(prev => [...prev, file]);
      });
    } else if (entry.isDirectory) {
      const dirReader = entry.createReader();
      dirReader.readEntries(entries => {
        entries.forEach(ent => readEntryFlatten(ent));
      });
    }
  };

 

  // Upload files to backend
  const handleUpload = async () => {
    if (!files || files.length === 0) {
      setMessage('Please select or drop files');
      return;
    }
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('practice_id', practice_id);

    try {
      await apiFiles.post(`/upload/${id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage('Upload successful');
      setFiles([]);
      await fetchExistingFiles();
    } catch {
      setMessage('Upload failed');
    }
  };

  // New files (before uploading) list
  const renderFiles = () => (
    <ul>
      {files.map((file, idx) => (
        <li key={idx}>{file.name}</li>
      ))}
    </ul>
  );

  // Existing files from backend (clickable)
  const renderExistingFiles = () => (
    <ul>
      {existingFiles.map(file => (
        <li key={file.id}>
          <a href={file.url} target="_blank" rel="noopener noreferrer">
            {file.name}
          </a>
        </li>
      ))}
    </ul>
  );

  



  

  // Tab click handler
  const onStageTabClick = (stage) => {
    setSelectedStage(stage);
  };

  // Render tabs
  const renderStageTabs = () => {
    const currentStageOption = compStageToStageOptionMap[compStage];
    const currentStageIndex = stageKeys.indexOf(currentStageOption);
    const previousStages =
      currentStageIndex > 0 ? stageKeys.filter((_, idx) => idx < currentStageIndex) : [];

    // Always filter out 'with_client_for_approval_version'
    const filteredStages = previousStages.filter(
      stage => stage !== 'with_client_for_approval_version'
    );

    // Extra buttons for approved/submitted stages
    const showApproved = currentStageOption === 'approved_version' || currentStageOption === 'submitted_version';
    const showSubmitted = currentStageOption === 'submitted_version';

    // Add stage buttons accordingly
    let stagesToShow = [...filteredStages];
    if (showApproved) {
      stagesToShow.push('approved_version');
    }
    if (showSubmitted) {
      stagesToShow.push('submitted_version');
    }

    // Remove duplicates in case they exist
    stagesToShow = [...new Set(stagesToShow)];

    if (!stagesToShow.length) {
      return <p>No previous stages found</p>; // Debug display if empty
    }

    return (
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        {stagesToShow.map(stage => (
          <button
            key={stage}
            style={{
              padding: '8px 16px',
              cursor: 'pointer',
              backgroundColor: stage === selectedStage ? '#2196F3' : '#eee',
              color: stage === selectedStage ? 'white' : 'black',
              border: 'none',
              borderRadius: '4px'
            }}
            onClick={() => onStageTabClick(stage)}
            type="button"
          >
            {stage.replace(/_/g, ' ')}
          </button>
        ))}
      </div>
    );
  };

  


  const handlePartnerStaffChange = (selectedOption) => {
  setPartnerStaffId(selectedOption.staff_id); // store just ID
  setPartnerSelectedText(selectedOption.display_name);
  setPartnerStaffError("");
};

const handleReviewerStaffChange = (selectedOption) => {
  setReviewerStaffId(selectedOption.staff_id); // store just ID
  setReviewerSelectedText(selectedOption.display_name);
  setReviewerStaffError("");
};

const handlePreparerStaffChange = (selectedOption) => {
  setPreparerStaffId(selectedOption.staff_id); // store just ID
  setPreparerSelectedText(selectedOption.display_name);
  setPreparerStaffError("");
};




  return (
    <Layout>
      <h2>Job Detail</h2>
      <table>
        <tbody>
          <tr>
            <th>Client Name: </th>
            <td>{clientName}</td>
          </tr>
          <tr>
            <th>Alt Description</th>
            <td>
              <textarea
                value={altDescription}
                onChange={e => setAltDescription(e.target.value)}
                rows={3}
                style={{ width: "100%" }}
                disabled={updating}
              />
            </td>
          </tr>
          <tr>
            <th>Period Start</th>
            <td>
              <input
                type="date"
                value={periodStart}
                onChange={e => setPeriodStart(e.target.value)}
                disabled={updating}
              />
            </td>
          </tr>
          <tr>
            <th>Period End</th>
            <td>
              <input
                type="date"
                value={periodEnd}
                onChange={e => setPeriodEnd(e.target.value)}
                disabled={updating}
              />
              {periodEndError && (<p style={{ color: "red" }}>Error, Period End has to be after Period Start.</p>)}
            </td>
          </tr>
          <tr>
            <th>Partner Staff</th>
            <td>
              <SearchablePaginatedDropdown
              inputRef={partnerInputRef}
          apiUrl="/staff/list/"
          value = "staff"
          onChange={handlePartnerStaffChange}
          pageSize={2}
          defaultSearchText={partnerStaffName}
        />
        {partnerstafferror && (<p style={{ color: "red" }}>Error, No Partner selected.</p>)}
            </td>
          </tr>
          <tr>
            <th>Reviewer Staff</th>
            <td>
              <SearchablePaginatedDropdown
              inputRef={reviewerInputRef}
          apiUrl="/staff/list/"
          value = "staff"
          onChange={handleReviewerStaffChange}
          pageSize={2}
          defaultSearchText={reviewerStaffName}
        />
        {reviewerstafferror && (<p style={{ color: "red" }}>Error, No Reviewer selected.</p>)}
            </td>
          </tr>
          <tr>
            <th>Preparer Staff</th>
            <td>
              <SearchablePaginatedDropdown
              inputRef={preparerInputRef}
          apiUrl="/staff/list/"
          value = "staff"
          onChange={handlePreparerStaffChange}
          pageSize={2}
          defaultSearchText={preparerStaffName}
        />
        {preparerstafferror && (<p style={{ color: "red" }}>Error, No Preparer selected.</p>)}
            </td>
          </tr>
          <tr>
            <th>Task with Staff: </th>
            <td>{taskWithStaff || "-"}</td>
          </tr>
          <tr>
            <th>Practice ID (display only)</th>
            <td>{practiceId}</td>
          </tr>
          <tr>
            <th>Job Category: </th>
            <td>{jobSelection}</td>
          </tr>
          {jobSelection === "CT_compliance" && (
          <tr>
            <th>Stage: </th>
            {compStage === "NA" ? <td>Not Started</td> :
            <td>{compStage}</td> }
          </tr>
          )}
        </tbody>
      </table>
      
      <br /><br />
      {jobSelection === "CT_compliance" && (
      <button
        disabled={updating || compStage === "Planning_draft" || compStage === "NA"}
        onClick={() => {
          changeStage("backward");
          setSelectedStage(stageKeys[0]);
        }}
        style={{ marginRight: "10px" }}
      >
        Previous Stage
      </button>
      )}
      <button
        disabled={updating}
        onClick={() => changeStage("nochange")}
        style={{ marginRight: "10px" }}
      >
        Save Changes
      </button>
      {jobSelection === "CT_compliance" && (
      <button
        disabled={updating || compStage === "Submitted"}
        onClick={() => 
          changeStage("forward")}
      >
        Next Stage
      </button>
      )}
      
      {compStage !== "Submitted" ? (
        <>
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            style={{
              border: dragActive ? "2px solid #2196F3" : "2px dashed #ccc",
              background: dragActive ? "#e3f2fd" : "#fafafa",
              padding: "32px",
              borderRadius: "12px",
              textAlign: "center",
              marginBottom: "16px"
            }}
          >
            <input
              type="file"
              multiple
              style={{ display: "none" }}
              id="fileUploadInput"
              onChange={handleFileChange}
            />
            <label htmlFor="fileUploadInput" style={{ cursor: "pointer" }}>
              <div>
                <p>Drag & drop files or folders here, or <u>click to select files</u></p>
              </div>
            </label>

            {files.length > 0 && (
              <>
                <strong>New files to upload:</strong>
                {renderFiles()}
              </>
            )}

            <div>
              <strong>Existing files:</strong>
              {renderExistingFiles()}
            </div>
          </div>

          <button onClick={handleUpload}>Upload</button>
          <p>{message}</p>
        </>
      ) : (
        <>
          
          <p style={{ color: "red" }}>No more files can be uploaded at the submitted stage.</p>
        </>
      )}

      {jobSelection === "CT_compliance" && (

      <StageFilesAccordion 
        existingStageFiles={existingStageFiles}
        renderStageTabs={renderStageTabs}
      />
    )}

    </Layout>
  );
}

export default JobDetail;