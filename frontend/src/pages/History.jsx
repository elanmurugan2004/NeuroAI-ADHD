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
            Review previous ADHD prediction records, uploaded MRI file history,
            confidence scores, and explainable multimodal summaries.
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
                <th>Patient</th>
                <th>Prediction</th>
                <th>Confidence</th>
                <th>Uploaded File</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {assessments.length > 0 ? (
                assessments.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.patient_name || `Patient ${item.patient_id}`}</td>
                    <td>
                      <span
                        style={{
                          color: item.predicted_label === "ADHD" ? "#f87171" : "#4ade80",
                          fontWeight: "700",
                        }}
                      >
                        {item.predicted_label}
                      </span>
                    </td>
                    <td>{item.confidence}%</td>
                    <td>{item.uploaded_file || "-"}</td>
                    <td>{item.created_at ? String(item.created_at).replace("T", " ").slice(0, 19) : "-"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6">No assessments found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="glass-card" style={styles.summaryCard}>
        <h3 style={{ marginTop: 0 }}>History Notes</h3>
        <p style={styles.note}>
          This page maintains all saved assessment records for clinical review.
          Each record stores patient linkage, multimodal prediction output,
          confidence score, upload information, and time of assessment.
        </p>
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
    marginBottom: "24px",
  },
  topRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "18px",
    gap: "12px",
  },
  summaryCard: {
    padding: "22px",
  },
  note: {
    color: "#9fb0ca",
    lineHeight: 1.8,
  },
};