import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/axios";

export default function NewAssessment() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    patient_id: "",
    full_name: "",
    age: "",
    gender: "Male",
    iq: "",
    handedness: "Right",
    site: "",
  });

  const [selectedFile, setSelectedFile] = useState(null);
  const [fileName, setFileName] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setFileName(file.name);
    }
  };

  const handleAssessment = async (e) => {
    e.preventDefault();

    try {
      const formData = new FormData();
      formData.append("patient_id", form.patient_id);
      formData.append("full_name", form.full_name);
      formData.append("age", form.age);
      formData.append("gender", form.gender);
      formData.append("iq", form.iq || "");
      formData.append("handedness", form.handedness);
      formData.append("site", form.site);

      if (selectedFile) {
        formData.append("mri_file", selectedFile);
      }

      const res = await API.post("/assessments/predict", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      localStorage.setItem("assessment_result", JSON.stringify(res.data));
      alert("Assessment completed successfully");
      navigate("/app/results");
    } catch (error) {
      console.error("Assessment failed:", error);
      alert(error?.response?.data?.detail || "Assessment failed");
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
              Enter patient details and upload a valid fMRI / NIfTI file to
              generate an AI-assisted assessment result.
            </p>
          </div>

          <div className="badge">Step-Based Clinical Input</div>
        </div>

        <form onSubmit={handleAssessment}>
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
                name="patient_id"
                type="number"
                placeholder="Patient ID"
                value={form.patient_id}
                onChange={handleChange}
                required
              />
              <input
                name="age"
                type="number"
                placeholder="Age"
                value={form.age}
                onChange={handleChange}
                required
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

            <input
              name="iq"
              type="number"
              placeholder="IQ"
              value={form.iq}
              onChange={handleChange}
            />

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

            <input type="file" accept=".nii,.nii.gz,.gz" onChange={handleFileChange} />

            <div style={styles.uploadInfo}>
              {fileName ? `Selected file: ${fileName}` : "No file selected"}
            </div>

            <p style={styles.note}>
              Upload a valid structural MRI or resting-state fMRI NIfTI file for
              AI-assisted analysis.
            </p>
          </div>

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
  submitBtn: {
    width: "100%",
    marginTop: "10px",
    fontSize: "16px",
    padding: "14px 18px",
  },
};