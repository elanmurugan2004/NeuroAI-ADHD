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
        alert(error?.response?.data?.detail || "Failed to fetch patients");
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

      const reloadPatients = async () => {
        try {
          const res = await API.get("/patients/");
          setPatients(res.data);
        } catch (error) {
          console.error("Failed to fetch patients:", error);
          alert(error?.response?.data?.detail || "Failed to fetch patients");
        }
      };
      await reloadPatients();
    } catch (error) {
      console.error("Failed to add patient:", error);
      alert(error?.response?.data?.detail || "Failed to add patient");
    }
  };

  return (
    <div className="page">
      <div className="glass-card" style={styles.headerCard}>
        <div>
          <div className="badge">Patient Management</div>
          <h1 style={styles.title}>Patients</h1>
          <p style={styles.subtitle}>
            Add and manage patient records before starting the assessment workflow.
          </p>
        </div>
      </div>

      <div style={styles.grid}>
        <div className="glass-card" style={styles.formCard}>
          <h3 style={{ marginTop: 0 }}>Add Patient</h3>

          <form onSubmit={handleAddPatient}>
            <input
              name="full_name"
              placeholder="Full Name"
              value={form.full_name}
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

            <select
              name="gender"
              value={form.gender}
              onChange={handleChange}
              required
            >
              <option value="">Select Gender</option>
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

            <textarea
              name="diagnosis_note"
              placeholder="Initial note"
              value={form.diagnosis_note}
              onChange={handleChange}
              rows="4"
            />

            <button className="primary-btn" type="submit" style={{ width: "100%" }}>
              Add Patient
            </button>
          </form>
        </div>

        <div className="glass-card" style={styles.listCard}>
          <h3 style={{ marginTop: 0 }}>Patient List</h3>

          {patients.length > 0 ? (
            <div style={styles.list}>
              {patients.map((patient) => (
                <div key={patient.id} style={styles.patientItem}>
                  <div>
                    <div style={styles.patientName}>{patient.full_name}</div>
                    <div style={styles.patientMeta}>
                      Age: {patient.age} | Gender: {patient.gender} | IQ: {patient.iq ?? "-"}
                    </div>
                  </div>
                  <div className="badge">#{patient.id}</div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: "#9fb0ca" }}>No patients found</p>
          )}
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
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "18px",
  },
  formCard: {
    padding: "22px",
  },
  listCard: {
    padding: "22px",
  },
  list: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  patientItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    padding: "14px 16px",
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "14px",
  },
  patientName: {
    fontWeight: "700",
  },
  patientMeta: {
    color: "#9fb0ca",
    fontSize: "13px",
    marginTop: "4px",
  },
};