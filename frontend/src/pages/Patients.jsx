import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import API from "../api/axios";

const MIN_AGE = 7;
const MAX_AGE = 17;

export default function Patients() {
  const location = useLocation();
  const navigate = useNavigate();

  const [patients, setPatients] = useState([]);
  const [form, setForm] = useState({
    full_name: "",
    age: "",
    gender: "",
    iq: "",
    diagnosis_note: "",
  });

  const searchTerm = useMemo(() => {
    const params = new URLSearchParams(location.search);
    return params.get("search") || "";
  }, [location.search]);

  useEffect(() => {
    let cancelled = false;

    const fetchPatients = async () => {
      try {
        const res = await API.get("/patients/");
        if (!cancelled) {
          setPatients(res.data);
        }
      } catch (error) {
        console.error("Failed to fetch patients:", error);
        if (!cancelled) {
          alert(error?.response?.data?.detail || "Failed to fetch patients");
        }
      }
    };

    fetchPatients();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredPatients = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();

    if (!q) return patients;

    return patients.filter((patient) => {
      const fullName = String(patient.full_name || "").toLowerCase();
      const gender = String(patient.gender || "").toLowerCase();
      const id = String(patient.id || "");
      const age = String(patient.age || "");
      const iq = String(patient.iq ?? "");

      return (
        fullName.includes(q) ||
        gender.includes(q) ||
        id.includes(q) ||
        age.includes(q) ||
        iq.includes(q)
      );
    });
  }, [patients, searchTerm]);

  const handleSearchChange = (value) => {
    const trimmed = value.trim();

    if (!trimmed) {
      navigate("/app/patients", { replace: true });
      return;
    }

    navigate(`/app/patients?search=${encodeURIComponent(value)}`, { replace: true });
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAddPatient = async (e) => {
    e.preventDefault();

    const ageValue = Number(form.age);

    if (Number.isNaN(ageValue) || ageValue < MIN_AGE || ageValue > MAX_AGE) {
      alert(
        `This project currently supports pediatric ADHD assessment only (age ${MIN_AGE}-${MAX_AGE}).`
      );
      return;
    }

    try {
      await API.post("/patients/", {
        full_name: form.full_name.trim(),
        age: ageValue,
        gender: form.gender,
        iq: form.iq ? Number(form.iq) : null,
        diagnosis_note: form.diagnosis_note,
      });

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
            Add and manage pediatric patient records before starting the ADHD assessment workflow.
          </p>
          <div style={styles.infoNote}>
            This module currently supports pediatric ADHD screening only ({MIN_AGE}-{MAX_AGE} years).
          </div>
        </div>
      </div>

      <div className="glass-card" style={styles.searchCard}>
        <input
          type="text"
          placeholder="Search by patient name, ID, age, gender, or IQ"
          value={searchTerm}
          onChange={(e) => handleSearchChange(e.target.value)}
        />
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
              min={MIN_AGE}
              max={MAX_AGE}
              placeholder={`Age (${MIN_AGE}-${MAX_AGE})`}
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
          <div style={styles.listHeader}>
            <h3 style={{ marginTop: 0, marginBottom: 0 }}>Patient List</h3>
            <span style={styles.countBadge}>
              {filteredPatients.length} result{filteredPatients.length !== 1 ? "s" : ""}
            </span>
          </div>

          {filteredPatients.length > 0 ? (
            <div style={styles.list}>
              {filteredPatients.map((patient) => (
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
            <p style={{ color: "#9fb0ca" }}>No matching patients found</p>
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
  searchCard: {
    padding: "18px",
    marginBottom: "24px",
  },
  title: {
    margin: "14px 0 10px",
  },
  subtitle: {
    color: "#9fb0ca",
    lineHeight: 1.7,
    marginBottom: "10px",
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
  listHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "14px",
    gap: "12px",
  },
  countBadge: {
    fontSize: "12px",
    fontWeight: "700",
    color: "#dbeafe",
    background: "rgba(59, 130, 246, 0.12)",
    border: "1px solid #3b82f6",
    borderRadius: "999px",
    padding: "6px 12px",
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