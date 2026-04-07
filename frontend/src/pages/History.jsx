import { useEffect, useState } from "react";
import API from "../api/axios";

export default function History() {
  const [assessments, setAssessments] = useState([]);

  useEffect(() => {
    const loadAssessments = async () => {
      try {
        const res = await API.get("/assessments/");
        setAssessments(res.data);
      } catch (error) {
        console.error("Failed to fetch assessments:", error);
      }
    };

    loadAssessments();
  }, []);

  return (
    <div className="page">
      <div className="glass-card" style={styles.headerCard}>
        <div>
          <div className="badge">Assessment Archive</div>
          <h1 style={styles.title}>Assessment History</h1>
          <p style={styles.subtitle}>
            Review previous ADHD prediction records, confidence scores, and
            explainable region-based results.
          </p>
        </div>
      </div>

      <div className="glass-card" style={styles.tableCard}>
        <div style={styles.topRow}>
          <h3 style={{ margin: 0 }}>Previous Assessments</h3>
          <span className="badge">Total: {assessments.length}</span>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Patient ID</th>
                <th>Prediction</th>
                <th>ADHD Score</th>
                <th>Confidence</th>
                <th>Region</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {assessments.length > 0 ? (
                assessments.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.patient_id}</td>
                    <td>{item.predicted_label}</td>
                    <td>{item.adhd_score}</td>
                    <td>{item.confidence}%</td>
                    <td>{item.important_region}</td>
                    <td>
                      <span className="badge">Reviewed</span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7">No assessments found</td>
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