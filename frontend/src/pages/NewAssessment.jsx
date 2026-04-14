import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/axios";

const MIN_AGE = 7;
const MAX_AGE = 17;

export default function NewAssessment() {
  const navigate = useNavigate();

  const [patients, setPatients] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const [form, setForm] = useState({
    patient_id: "",
    full_name: "",
    age: "",
    gender: "Male",
    iq: "",
    handedness: "Right",
    site: "",
  });

  useEffect(() => {
    let cancelled = false;

    const loadPatients = async () => {
      try {
        const res = await API.get("/patients/");
        if (!cancelled) {
          setPatients(res.data);
        }
      } catch (error) {
        console.error("Failed to load patients:", error);
        if (!cancelled) {
          setErrorMsg(error?.response?.data?.detail || "Failed to load patients");
        }
      }
    };

    loadPatients();

    return () => {
      cancelled = true;
    };
  }, []);

  const handlePatientSelect = (e) => {
    setErrorMsg("");

    const patientId = e.target.value;
    const selected = patients.find((p) => String(p.id) === String(patientId));

    if (selected) {
      setForm((prev) => ({
        ...prev,
        patient_id: String(selected.id),
        full_name: selected.full_name || "",
        age: selected.age || "",
        gender: selected.gender || "Male",
        iq: selected.iq ?? "",
      }));

      if (Number(selected.age) < MIN_AGE || Number(selected.age) > MAX_AGE) {
        setErrorMsg(
          `This project currently supports pediatric ADHD assessment only (age ${MIN_AGE}-${MAX_AGE}).`
        );
      }
    } else {
      setForm((prev) => ({
        ...prev,
        patient_id: "",
        full_name: "",
        age: "",
        gender: "Male",
        iq: "",
      }));
    }
  };

  const handleChange = (e) => {
    setErrorMsg("");
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    setErrorMsg("");
    const file = e.target.files?.[0];

    if (!file) {
      setSelectedFile(null);
      setFileName("");
      return;
    }

    const name = file.name.toLowerCase();
    if (!(name.endsWith(".nii") || name.endsWith(".nii.gz"))) {
      setErrorMsg("Only .nii or .nii.gz files are allowed");
      setSelectedFile(null);
      setFileName("");
      return;
    }

    setSelectedFile(file);
    setFileName(file.name);
  };

  const handleAssessment = async (e) => {
    e.preventDefault();
    setErrorMsg("");

    if (!form.patient_id) {
      setErrorMsg("Please select a patient");
      return;
    }

    const ageValue = Number(form.age);
    if (Number.isNaN(ageValue) || ageValue < MIN_AGE || ageValue > MAX_AGE) {
      setErrorMsg(
        `This project currently supports pediatric ADHD assessment only (age ${MIN_AGE}-${MAX_AGE}).`
      );
      return;
    }

    if (!selectedFile) {
      setErrorMsg("Please upload a valid fMRI NIfTI file");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("patient_id", form.patient_id);
      formData.append("full_name", form.full_name);
      formData.append("age", String(ageValue));
      formData.append("gender", form.gender);
      formData.append("iq", form.iq ? String(Number(form.iq)) : "");
      formData.append("handedness", form.handedness);
      formData.append("site", form.site || "Unknown");
      formData.append("mri_file", selectedFile);

      const res = await API.post("/assessments/predict", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      localStorage.setItem("assessment_result", JSON.stringify(res.data));
      navigate("/app/results");
    } catch (error) {
      console.error("Assessment failed:", error);
      setErrorMsg(error?.response?.data?.detail || "Assessment failed");
    }
  };

  return (
    <div className="page">
      <div className="glass-card" style={styles.wrapper}>
        <div style={styles.headerRow}>
          <div>
            <div className="badge">ASSESSMENT WORKFLOW</div>
            <h1 style={styles.title}>New ADHD Assessment</h1>
            <p style={styles.subtitle}>
              Select a pediatric patient, review demographic details, upload a valid
              resting-state fMRI NIfTI file, and generate an AI-assisted multimodal result.
            </p>
            <div style={styles.infoNote}>
              Pediatric ADHD module: supported age range {MIN_AGE}-{MAX_AGE} years
            </div>
          </div>

          <div className="badge">Secure Clinical Upload</div>
        </div>

        <form onSubmit={handleAssessment}>
          <div className="glass-card" style={styles.sectionCard}>
            <h2 style={styles.sectionTitle}>Patient Selection</h2>

            <select value={form.patient_id} onChange={handlePatientSelect} required>
              <option value="">Select Patient</option>
              {patients.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.id} - {p.full_name}
                </option>
              ))}
            </select>
          </div>

          <div className="glass-card" style={styles.sectionCard}>
            <h2 style={styles.sectionTitle}>Patient Details</h2>

            <input
              name="full_name"
              placeholder="Patient Name"
              value={form.full_name}
              onChange={handleChange}
              required
            />

            <div style={styles.twoCol}>
              <input
                name="age"
                type="number"
                min={MIN_AGE}
                max={MAX_AGE}
                placeholder={`Age (${MIN_AGE}-${MAX_AGE})`}
                value={form.age}
                onChange={handleChange}
                required
              />
              <input
                name="iq"
                type="number"
                placeholder="IQ"
                value={form.iq}
                onChange={handleChange}
              />
            </div>

            <select
              name="gender"
              value={form.gender}
              onChange={handleChange}
              required
            >
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>

            <select
              name="handedness"
              value={form.handedness}
              onChange={handleChange}
              required
            >
              <option value="Right">Right</option>
              <option value="Left">Left</option>
              <option value="Ambidextrous">Ambidextrous</option>
            </select>

            <input
              name="site"
              placeholder="Site / Hospital"
              value={form.site}
              onChange={handleChange}
              required
            />
          </div>

          <div className="glass-card" style={styles.sectionCard}>
            <h2 style={styles.sectionTitle}>Imaging Upload</h2>

            <input type="file" accept=".nii,.nii.gz" onChange={handleFileChange} />

            <div style={styles.uploadInfo}>
              {fileName ? `Selected file: ${fileName}` : "No file selected"}
            </div>

            <p style={styles.note}>
              Only validated <code>.nii</code> or <code>.nii.gz</code> neuroimaging files are accepted.
              This assessment module is currently intended for pediatric ADHD screening and requires a 4D resting-state fMRI file.
            </p>
          </div>

          {errorMsg && <div style={styles.errorBox}>{errorMsg}</div>}

          <button className="primary-btn" type="submit" style={styles.submitBtn}>
            Run AI Assessment
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    padding: "28px",
    maxWidth: "980px",
    margin: "0 auto",
  },
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "16px",
    marginBottom: "24px",
    flexWrap: "wrap",
  },
  title: {
    margin: "14px 0 10px",
    fontSize: "44px",
  },
  subtitle: {
    color: "#9fb0ca",
    lineHeight: 1.8,
    maxWidth: "760px",
    fontSize: "18px",
    marginBottom: "12px",
  },
  infoNote: {
    display: "inline-block",
    background: "rgba(59, 130, 246, 0.12)",
    border: "1px solid #3b82f6",
    color: "#dbeafe",
    borderRadius: "12px",
    padding: "10px 14px",
    fontSize: "13px",
    fontWeight: "600",
  },
  sectionCard: {
    padding: "24px",
    marginBottom: "20px",
  },
  sectionTitle: {
    marginTop: 0,
    marginBottom: "18px",
    fontSize: "20px",
  },
  twoCol: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "14px",
  },
  uploadInfo: {
    marginTop: "12px",
    color: "#93c5fd",
    fontSize: "14px",
  },
  note: {
    marginTop: "12px",
    color: "#9fb0ca",
    lineHeight: 1.7,
  },
  errorBox: {
    marginBottom: "16px",
    background: "rgba(239, 68, 68, 0.14)",
    border: "1px solid #ef4444",
    color: "#fecaca",
    borderRadius: "12px",
    padding: "14px",
  },
  submitBtn: {
    width: "100%",
    marginTop: "10px",
    fontSize: "16px",
    padding: "14px 18px",
  },
};