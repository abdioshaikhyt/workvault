import React, { useEffect, useState, useRef } from "react";
import apiBook from "../apiBook";
import { useNavigate } from "react-router-dom";
import useUserInfo from "../components/GetUsername";
import SearchablePaginatedDropdown from "../components/SearchablePaginatedDropdown";
import Layout from "../components/Layout";

function NewJob() {
  const [client, setClient] = useState("");
  const [altDescription, setAltDescription] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [partnerStaff, setPartnerStaff] = useState("");
  const [reviewerStaff, setReviewerStaff] = useState("");
  const [preparerStaff, setPreparerStaff] = useState("");
  const [jobSelection, setJobSelection] = useState("");
  const [clienterror, setClientError] = useState("");
  const [partnerstafferror, setPartnerStaffError] = useState("");
  const [reviewerstafferror, setReviewerStaffError] = useState("");
  const [preparerstafferror, setPreparerStaffError] = useState("");
  const [selectedPartnerText, setPartnerSelectedText] = useState("");
  const [selectedReviewerText, setReviewerSelectedText] = useState("");
  const [selectedPreparerText, setPreparerSelectedText] = useState("");
  const [selectedClientText, setClientSelectedText] = useState("");
  const clientInputRef = useRef();
  const partnerInputRef = useRef();
  const reviewerInputRef = useRef();
  const preparerInputRef = useRef();
  
  const [jobCategories, setJobCategories] = useState([]);
  const [periodEndError, setPeriodEndError] = useState("");
  const [submitReset, setSubmitReset] = useState(0);

  const [clients, setClients] = useState([]);
  const [staffs, setStaffs] = useState([]);

  const { userId, practice_id} = useUserInfo();
  const navigate = useNavigate();

  useEffect(() => {
    setPeriodEndError("");
    if (periodStart && periodEnd) {
      if (new Date(periodEnd) < new Date(periodStart)) {
        setPeriodEndError("Period End must be after Period Start");
      }
    }
  }, [periodStart, periodEnd]);

  useEffect(() => {
    apiBook.get("/jobs/choices/").then(res => {
      setJobCategories(res.data.job_categories);

    });
  }, []);

  const createJob = (e) => {
    e.preventDefault();
    setPartnerStaffError("");
    setReviewerStaffError("");
    setPreparerStaffError("");
    setClientError("");

    let hasError = false;
    
    console.log("partnerInputRef:", partnerInputRef.current?.value);
    console.log("reviewerInputRef:", reviewerInputRef.current?.value);
    console.log("preparerInputRef:", preparerInputRef.current?.value);
    console.log("selectedPartnerText:", selectedPartnerText);
    console.log("selectedReviewerText:", selectedReviewerText);
    console.log("selectedPreparerText:", selectedPreparerText);

    const currentClientInput = clientInputRef.current?.value || "";
    if (!client || currentClientInput.trim() !== selectedClientText) {
      setClientError("Please select a Client");
      hasError = true;
    }

    const currentPartnerInput = partnerInputRef.current?.value || "";
    if (!partnerStaff || currentPartnerInput.trim() !== selectedPartnerText) {
      setPartnerStaffError("Please select a Partner Staff");
      hasError = true;
    }
    const currentReviewerInput = reviewerInputRef.current?.value || "";
    if (!reviewerStaff || currentReviewerInput.trim() !== selectedReviewerText) {
      setReviewerStaffError("Please select a Reviewer Staff");
      hasError = true;
    }
    const currentPreparerInput = preparerInputRef.current?.value || "";
    if (!preparerStaff || currentPreparerInput.trim() !== selectedPreparerText) {
      setPreparerStaffError("Please select a Preparer Staff");
      hasError = true;
    }

    if (periodEndError){
      hasError = true;
    }

    if (hasError) {
      console.log("Validation failed - polluting inputs");
      return;
    }
    console.log("Validation succeeded - proceeding to submit");

    apiBook.post("/jobs/create/", {
      client,
      alt_description: altDescription,
      period_start: periodStart,
      period_end: periodEnd,
      partner_staff: partnerStaff,
      reviewer_staff: reviewerStaff,
      preparer_staff: preparerStaff,
      practice_id,
      job_selection: jobSelection,
      task_with_staff: userId,
    })
    .then((res) => {
      if (res.status === 201) {
        alert("Job created!");
        setClient("");
        setAltDescription("");
        setPeriodStart("");
        setPeriodEnd("");
        setPartnerStaff("");
        setReviewerStaff("");
        setPreparerStaff("");
        setJobSelection("");
        setSubmitReset(prev => prev + 1);

    } else {
        alert("Failed to create job.");
      }
    })
    .catch((err) => alert(err));
  };

  const handleClientChange = (selectedOption) => {
  setClient(selectedOption.id);
  setClientSelectedText(selectedOption.company_name);
  setClientError("");
};

  const handlePartnerStaffChange = (selectedOption) => {
  setPartnerStaff(selectedOption.staff_id); 
  setPartnerSelectedText(selectedOption.display_name);
  setPartnerStaffError("");
};

const handleReviewerStaffChange = (selectedOption) => {
  setReviewerStaff(selectedOption.staff_id); 
  setReviewerSelectedText(selectedOption.display_name);
  setReviewerStaffError("");
};

const handlePreparerStaffChange = (selectedOption) => {
  setPreparerStaff(selectedOption.staff_id); 
  setPreparerSelectedText(selectedOption.display_name);
  setPreparerStaffError("");
};

  return (
    <Layout>
      <h2>Create a Job</h2>
      <form onSubmit={createJob}>
        <label htmlFor="client">Client:</label>
        <SearchablePaginatedDropdown
          inputRef={clientInputRef}
          apiUrl="/clients/droplist/"
          value = "clients"
          onChange={handleClientChange}
          pageSize={2}
          resetTrigger={submitReset}
        />
        {clienterror && (<p style={{ color: "red" }}>Error, No Client selected.</p>)}
        <br />

        <label htmlFor="altDescription">Alt. Description:</label>
        <input type="text" id="altDescription" value={altDescription} onChange={e => setAltDescription(e.target.value)} autoComplete="off" />
        <br />

        <label htmlFor="periodStart">Period Start:</label>
        <input type="date" id="periodStart" value={periodStart} required onChange={e => setPeriodStart(e.target.value)} />
        <br />

        <label htmlFor="periodEnd">Period End:</label>
        <input type="date" id="periodEnd" value={periodEnd} required onChange={e => setPeriodEnd(e.target.value)} />
        {periodEndError && (<p style={{ color: "red" }}>Error, Period End has to be after Period Start.</p>)}
        <br />

        <label htmlFor="partnerStaff">Partner Staff:</label>
        <SearchablePaginatedDropdown
          inputRef={partnerInputRef}
          apiUrl="/staff/list/"
          value = "staff"
          onChange={handlePartnerStaffChange}
          pageSize={2}
          resetTrigger={submitReset}
         
        />
        {partnerstafferror && (<p style={{ color: "red" }}>Error, No Partner selected.</p>)}
        <br />

        <label htmlFor="reviewerStaff">Reviewer Staff:</label>
        <SearchablePaginatedDropdown
          inputRef={reviewerInputRef}
          apiUrl="/staff/list/"
          value = "staff"
          onChange={handleReviewerStaffChange}
          
          pageSize={2}
          resetTrigger={submitReset}
         
        />
        {reviewerstafferror && (<p style={{ color: "red" }}>Error, No Reviewer selected.</p>)}
        <br />

        <label htmlFor="preparerStaff">Preparer Staff:</label>
        <SearchablePaginatedDropdown
          inputRef={preparerInputRef}
          apiUrl="/staff/list/"
          value = "staff"
          onChange={handlePreparerStaffChange}
         
          pageSize={2}
          resetTrigger={submitReset}
          
        />
        {preparerstafferror && (<p style={{ color: "red" }}>Error, No Preparer selected.</p>)}
        <br />

        <label htmlFor="jobSelection">Job Category:</label>
        <select id="jobSelection" value={jobSelection} required onChange={e => setJobSelection(e.target.value)}>
          <option value="">Select category</option>
          {jobCategories.map((jc) => (
            <option key={jc.value} value={jc.value}>{jc.label}</option>
          ))}
        </select>
        <br />

        

        <br /><br />
        <button className="form-button" type="submit" style={{ marginBottom: "10px" }}>
          Add Job
        </button>
      </form>
    </Layout>
  );
}

export default NewJob;