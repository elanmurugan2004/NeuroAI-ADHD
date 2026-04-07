import { useEffect, useState } from "react";
import API from "../api/axios";

export default function Patients() {
  const [patients, setPatients] = useState([]);
  const [form, setForm] = useState({
    full_name: "",
    age: "",
    gender: "",
    iq: "",
    diagnosis_note: "",
  });

  useEffect(() => {
    const loadPatients = async () => {
      try {
        const res = await API.get("/patients/");
        setPatients(res.data);
      } catch (error) {
        console.error("Failed to fetch patients:", error);
      }
    };

    loadPatients();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAddPatient = async (e) => {
    e.preventDefault();

    try {
      await API.post("/patients/", {
        full_name: form.full_name,
        age: Number(form.age),
        gender: form.gender,
        iq: form.iq ? Number(form.iq) : null,
        diagnosis_note: form.diagnosis_note,
      });

      alert("Patient added successfully");

      setForm({
        full_name: "",
        age: "",
        gender: "",
        iq: "",
        diagnosis_note: "",
      });

      const res = await API.get("/patients/");
      setPatients(res.data);
    } catch (error) {
      console.error("Failed to add patient:", error);
      alert("Failed to add patient");
    }
  };

  return (
    <div className="page">
      <div className="glass-card" style={styles.headerCard}>
        <div>
          <div className="badge">Clinical Intake Module</div>
          <h1 style={styles.title}>Patient Management</h1>
          <p style={styles.subtitle}>
            Register patient details, demographic information, and baseline notes
            before running the ADHD assessment workflow.
          </p>
        </div>
      </div>

      <div style={styles.grid}>
        <div className="glass-card" style={styles.formCard}>
          <h3 style={{ marginTop: 0 }}>Add New Patient</h3>

          <form onSubmit={handleAddPatient}>
            <label>Full Name</label>
            <input
              name="full_name"
              placeholder="Enter patient name"
              value={form.full_name}
              onChange={handleChange}
              required
            />

            <div style={styles.twoCol}>
              <div>
                <label>Age</label>
                <input
                  name="age"
                  type="number"
                  placeholder="Age"
                  value={form.age}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label>Gender</label>
                <input
                  name="gender"
                  placeholder="Male / Female"
                  value={form.gender}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <label>IQ</label>
            <input
              name="iq"
              type="number"
              placeholder="Enter IQ score"
              value={form.iq}
              onChange={handleChange}
            />

            <label>Clinical Note</label>
            <textarea
              name="diagnosis_note"
              rows="5"
              placeholder="Add attention or behavioral observations"
              value={form.diagnosis_note}
              onChange={handleChange}
            />

            <button className="primary-btn" type="submit" style={{ width: "100%" }}>
              Save Patient
            </button>
          </form>
        </div>

        <div className="glass-card" style={styles.infoCard}>
          <h3 style={{ marginTop: 0 }}>Clinical Guidance</h3>
          <p style={styles.muted}>
            Ensure correct demographic details before starting the assessment.
            Patient history improves review quality and supports longitudinal tracking.
          </p>

          <div style={styles.infoBox}>
            <strong>Recommended fields</strong>
            <ul style={styles.list}>
              <li>Age and gender</li>
              <li>IQ score if available</li>
              <li>Initial behavioral note</li>
              <li>Clinical review comments later</li>
            </ul>
          </div>

          <div className="badge">Doctor-only Access</div>
        </div>
      </div>

      <div className="glass-card" style={styles.tableCard}>
        <div style={styles.topRow}>
          <h3 style={{ margin: 0 }}>Registered Patients</h3>
          <span className="badge">Total: {patients.length}</span>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Patient Name</th>
                <th>Age</th>
                <th>Gender</th>
                <th>IQ</th>
                <th>Clinical Note</th>
              </tr>
            </thead>
            <tbody>
              {patients.length > 0 ? (
                patients.map((p) => (
                  <tr key={p.id}>
                    <td>{p.id}</td>
                    <td>{p.full_name}</td>
                    <td>{p.age}</td>
                    <td>{p.gender}</td>
                    <td>{p.iq ?? "-"}</td>
                    <td>{p.diagnosis_note || "-"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6">No patients found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

const styles = {
  headerCard: {
    padding: "24px",
    marginBottom: "24px",
  },
  title: {
    margin: "14px 0 10px",
  },
  subtitle: {
    color: "#9fb0ca",
    lineHeight: 1.7,
    maxWidth: "760px",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1.2fr 0.8fr",
    gap: "18px",
    marginBottom: "24px",
  },
  formCard: {
    padding: "22px",
  },
  infoCard: {
    padding: "22px",
  },
  twoCol: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "14px",
  },
  infoBox: {
    marginTop: "18px",
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "16px",
    padding: "16px",
  },
  list: {
    color: "#cbd5e1",
    lineHeight: 1.9,
    marginBottom: 0,
  },
  muted: {
    color: "#9fb0ca",
    lineHeight: 1.8,
  },
  tableCard: {
    padding: "22px",
  },
  topRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "18px",
    gap: "12px",
  },
};