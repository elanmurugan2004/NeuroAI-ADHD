import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";

export default function Results() {
  const navigate = useNavigate();
  const result = JSON.parse(localStorage.getItem("assessment_result") || "null");

  useEffect(() => {
    if (!result) {
      alert("No assessment result found. Please run an assessment first.");
      navigate("/app/assessment");
    }
  }, [result, navigate]);

  if (!result) return null;

  const lowConfidence = Number(result.confidence || 0) < 70;
  const topRegions = (result.top_regions || []).slice(0, 3);

  const handleDownloadReport = () => {
    const doc = new jsPDF();

    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text("NEUROAI-ADHD CLINICAL REPORT", 20, 20);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);

    let y = 35;
    const lines = [
      `Assessment ID: ${result.id || "-"}`,
      `Patient Name: ${result.patient_name || "-"}`,
      `Prediction: ${result.predicted_label || "-"}`,
      `Confidence: ${result.confidence ? `${result.confidence}%` : "-"}`,
      `ADHD Probability: ${result.adhd_probability ?? "-"}`,
      `Control Probability: ${result.control_probability ?? "-"}`,
      `Uploaded File: ${result.uploaded_file || "-"}`,
      "",
      "Explainable AI Summary:",
      result.clinical_summary || "-",
      "",
      "Top Brain Regions:",
      ...topRegions.map((r, i) => `${i + 1}. ${r.name} - ${r.level}`),
      "",
      "Clinical Recommendation:",
      result.recommendation || "-",
    ];

    lines.forEach((line) => {
      const wrapped = doc.splitTextToSize(String(line), 170);
      doc.text(wrapped, 20, y);
      y += wrapped.length * 7;
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
    });

    doc.save("neuroai_adhd_clinical_report.pdf");
  };

  return (
    <div className="page">
      <div className="glass-card" style={styles.heroCard}>
        <div style={styles.heroTop}>
          <div>
            <div className="badge">AI CLINICAL REPORT</div>
            <h1 style={styles.title}>Assessment Results</h1>
            <p style={styles.subtitle}>
              AI-assisted scan interpretation with doctor-friendly regional explanation.
            </p>
          </div>

          <div style={styles.resultBox}>
            <div style={styles.resultLabel}>Prediction</div>
            <div
              style={{
                ...styles.resultValue,
                color: result.predicted_label === "ADHD" ? "#f87171" : "#4ade80",
              }}
            >
              {result.predicted_label}
            </div>
          </div>
        </div>

        <div style={styles.actionRow}>
          <button className="primary-btn" onClick={handleDownloadReport}>
            Download PDF
          </button>
          <button className="secondary-btn" onClick={() => navigate("/app/history")}>
            View History
          </button>
        </div>
      </div>

      {lowConfidence && (
        <div style={styles.warningBox}>
          Low-confidence prediction detected. Specialist review is recommended.
        </div>
      )}

      <div style={styles.metricGrid}>
        <div className="glass-card" style={styles.metricCard}>
          <div style={styles.metricTitle}>Confidence</div>
          <div style={styles.metricValue}>{result.confidence}%</div>
        </div>

        <div className="glass-card" style={styles.metricCard}>
          <div style={styles.metricTitle}>ADHD Probability</div>
          <div style={styles.metricValue}>{result.adhd_probability}</div>
        </div>

        <div className="glass-card" style={styles.metricCard}>
          <div style={styles.metricTitle}>Control Probability</div>
          <div style={styles.metricValue}>{result.control_probability}</div>
        </div>
      </div>

      <div className="glass-card" style={styles.sectionCard}>
        <h3 style={styles.sectionTitle}>Explainable AI Summary</h3>
        <div style={styles.summaryBox}>
          {result.clinical_summary || "AI-based summary is not available."}
        </div>
      </div>

      <div className="glass-card" style={styles.sectionCard}>
        <div style={styles.sectionHeader}>
          <h3 style={styles.sectionTitle}>AI-Highlighted Brain Regions</h3>
          
        </div>

        {topRegions.length > 0 ? (
          <div style={styles.regionGrid}>
            {topRegions.map((region, index) => (
              <div key={index} style={styles.regionCard}>
                <div style={styles.regionName}>{region.name}</div>
                <div style={styles.regionSub}>AI-highlighted for this scan</div>
                <div style={styles.levelChip(region.level)}>{region.level}</div>
              </div>
            ))}
          </div>
        ) : (
          <p style={styles.muted}>No regional explanation available</p>
        )}
      </div>

      <div className="glass-card" style={styles.sectionCard}>
        <h3 style={styles.sectionTitle}>Clinical Recommendation</h3>
        <div style={styles.recommendBox}>
          {result.recommendation || "Clinical review is recommended."}
        </div>
      </div>

      <div className="glass-card" style={styles.sectionCard}>
        <h3 style={styles.sectionTitle}>Scan Details</h3>
        <div style={styles.metaGrid}>
          <div style={styles.metaItem}>
            <div style={styles.metaLabel}>Patient Name</div>
            <div style={styles.metaValue}>{result.patient_name || "-"}</div>
          </div>
          <div style={styles.metaItem}>
            <div style={styles.metaLabel}>Uploaded Scan</div>
            <div style={styles.metaValue}>{result.uploaded_file || "-"}</div>
          </div>
          <div style={styles.metaItem}>
            <div style={styles.metaLabel}>Age</div>
            <div style={styles.metaValue}>{result.age ?? "-"}</div>
          </div>
          <div style={styles.metaItem}>
            <div style={styles.metaLabel}>Gender</div>
            <div style={styles.metaValue}>{result.gender || "-"}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  heroCard: {
    padding: "24px",
    marginBottom: "24px",
  },
  heroTop: {
    display: "flex",
    justifyContent: "space-between",
    gap: "16px",
    alignItems: "flex-start",
    flexWrap: "wrap",
  },
  title: {
    margin: "14px 0 10px",
  },
  subtitle: {
    color: "#9fb0ca",
    lineHeight: 1.7,
    maxWidth: "760px",
  },
  resultBox: {
    minWidth: "210px",
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "20px",
    padding: "18px",
  },
  resultLabel: {
    color: "#9fb0ca",
    fontSize: "14px",
    marginBottom: "10px",
  },
  resultValue: {
    fontSize: "34px",
    fontWeight: "800",
  },
  actionRow: {
    display: "flex",
    gap: "12px",
    marginTop: "18px",
    flexWrap: "wrap",
  },
  warningBox: {
    marginBottom: "24px",
    background: "rgba(245, 158, 11, 0.14)",
    border: "1px solid #f59e0b",
    color: "#fde68a",
    borderRadius: "16px",
    padding: "16px",
    fontWeight: "600",
  },
  metricGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "18px",
    marginBottom: "24px",
  },
  metricCard: {
    padding: "22px",
  },
  metricTitle: {
    color: "#9fb0ca",
    fontSize: "14px",
    marginBottom: "10px",
  },
  metricValue: {
    fontWeight: "800",
    fontSize: "28px",
  },
  sectionCard: {
    padding: "22px",
    marginBottom: "24px",
  },
  sectionHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    marginBottom: "14px",
  },
  sectionTitle: {
    marginTop: 0,
    marginBottom: "14px",
  },
  summaryBox: {
    background: "rgba(37, 99, 235, 0.14)",
    border: "1px solid #2563eb",
    borderRadius: "16px",
    padding: "18px",
    color: "#dbeafe",
    lineHeight: 1.8,
  },
  regionGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "16px",
  },
  regionCard: {
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "18px",
    padding: "18px",
  },
  regionName: {
    fontWeight: "800",
    fontSize: "18px",
    marginBottom: "8px",
  },
  regionSub: {
    color: "#9fb0ca",
    fontSize: "13px",
    marginBottom: "16px",
  },
  levelChip: (level) => ({
    display: "inline-block",
    padding: "8px 14px",
    borderRadius: "999px",
    fontSize: "12px",
    fontWeight: "700",
    border: "1px solid #21406a",
    background:
      level === "High"
        ? "rgba(239, 68, 68, 0.14)"
        : level === "Moderate"
        ? "rgba(245, 158, 11, 0.14)"
        : "rgba(59, 130, 246, 0.14)",
    color:
      level === "High"
        ? "#fca5a5"
        : level === "Moderate"
        ? "#fde68a"
        : "#93c5fd",
  }),
  recommendBox: {
    background: "rgba(16, 185, 129, 0.12)",
    border: "1px solid #10b981",
    borderRadius: "16px",
    padding: "18px",
    color: "#d1fae5",
    lineHeight: 1.8,
  },
  metaGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: "14px",
  },
  metaItem: {
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "14px",
    padding: "16px",
  },
  metaLabel: {
    color: "#9fb0ca",
    fontSize: "13px",
    marginBottom: "8px",
  },
  metaValue: {
    fontWeight: "700",
  },
  muted: {
    color: "#9fb0ca",
  },
};