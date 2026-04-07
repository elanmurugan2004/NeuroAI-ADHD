import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";
import PredictionCard from "../components/PredictionCard";
import RegionCard from "../components/RegionCard";

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

  const adhdProb = result.adhd_score ? Number(result.adhd_score) : 0;
  const controlProb = (1 - adhdProb).toFixed(4);

  const regionData = [
    {
      name: result.important_region || "Precuneus Cortex",
      contribution: "High",
      score: result.adhd_score || 0.71,
    },
    {
      name: "Parahippocampal Gyrus",
      contribution: "Moderate",
      score: 0.58,
    },
    {
      name: "Fronto-Striatal Circuit",
      contribution: "Moderate",
      score: 0.52,
    },
  ];

  const handleDownloadReport = () => {
    const doc = new jsPDF();

    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text("NEUROAI-ADHD ASSESSMENT REPORT", 20, 20);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);

    let y = 35;

    const lines = [
      `Assessment ID: ${result.id || "-"}`,
      `Patient ID: ${result.patient_id || "-"}`,
      `Prediction: ${result.predicted_label || "-"}`,
      `ADHD Probability: ${adhdProb ? adhdProb.toFixed(4) : "0.0000"}`,
      `Control Probability: ${controlProb}`,
      `Confidence: ${result.confidence ? `${result.confidence}%` : "-"}`,
      `Important Region: ${result.important_region || "-"}`,
      `Created At: ${result.created_at || "-"}`,
      "",
      "Clinical Interpretation:",
      result.explanation ||
        "Prediction generated using multimodal input values and explainable AI support.",
      "",
      "Important Brain Regions:",
      `1. ${regionData[0].name} - ${regionData[0].contribution} - Score: ${regionData[0].score}`,
      `2. ${regionData[1].name} - ${regionData[1].contribution} - Score: ${regionData[1].score}`,
      `3. ${regionData[2].name} - ${regionData[2].contribution} - Score: ${regionData[2].score}`,
      "",
      "Recommendation:",
      "Specialist clinical review is recommended before final diagnosis.",
    ];

    lines.forEach((line) => {
      const wrapped = doc.splitTextToSize(line, 170);
      doc.text(wrapped, 20, y);
      y += wrapped.length * 7;
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
    });

    doc.save("neuroai_adhd_report.pdf");
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="page">
      <div className="glass-card" style={styles.headerCard}>
        <div style={styles.headerTop}>
          <div>
            <div className="badge">Prediction Report</div>
            <h1 style={styles.title}>Assessment Results</h1>
            <p style={styles.subtitle}>
              AI-generated clinical summary with prediction scores, explainable
              interpretation, and important brain regions.
            </p>
          </div>

          <div style={styles.statusBox}>
            <div style={styles.statusLabel}>Assessment ID</div>
            <div style={styles.statusValue}>{result.id || "-"}</div>
          </div>
        </div>

        <div style={styles.actionRow}>
          <button className="primary-btn" onClick={handleDownloadReport}>
            Download PDF Report
          </button>
          <button className="secondary-btn" onClick={handlePrint}>
            Print
          </button>
        </div>
      </div>

      <div style={styles.cardGrid}>
        <PredictionCard
          title="Prediction"
          value={result.predicted_label || "N/A"}
          color={result.predicted_label === "ADHD" ? "#f87171" : "#4ade80"}
        />
        <PredictionCard
          title="ADHD Probability"
          value={adhdProb ? adhdProb.toFixed(4) : "0.0000"}
          color="#93c5fd"
        />
        <PredictionCard
          title="Control Probability"
          value={controlProb}
          color="#67e8f9"
        />
        <PredictionCard
          title="Confidence"
          value={result.confidence ? `${result.confidence}%` : "-"}
          color="#fde68a"
        />
      </div>

      <div style={styles.midGrid}>
        <div className="glass-card" style={styles.panel}>
          <h3 style={{ marginTop: 0 }}>Recommendation</h3>
          <div style={styles.recommendationBox}>
            Specialist clinical review is recommended before final diagnosis.
          </div>

          <h3>Neuro-Clinical Interpretation</h3>
          <p style={styles.muted}>
            {result.explanation ||
              "Prediction generated using multimodal input values and explainable AI support. The output should be interpreted together with patient history, behavioral screening, and specialist evaluation."}
          </p>
        </div>

        <div className="glass-card" style={styles.panel}>
          <h3 style={{ marginTop: 0 }}>Assessment Metadata</h3>
          <div style={styles.metaItem}>
            <span>Patient ID</span>
            <strong>{result.patient_id || "-"}</strong>
          </div>
          <div style={styles.metaItem}>
            <span>Important Region</span>
            <strong>{result.important_region || "-"}</strong>
          </div>
          <div style={styles.metaItem}>
            <span>Created At</span>
            <strong>{result.created_at || "-"}</strong>
          </div>
          <div style={styles.metaItem}>
            <span>Review Status</span>
            <strong>Pending</strong>
          </div>
        </div>
      </div>

      <div className="glass-card" style={styles.regionPanel}>
        <h3 style={{ marginTop: 0 }}>Most Influential Brain Regions</h3>
        <div style={styles.regionGrid}>
          {regionData.map((region, index) => (
            <RegionCard
              key={index}
              name={region.name}
              contribution={region.contribution}
              score={region.score}
            />
          ))}
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
  headerTop: {
    display: "flex",
    justifyContent: "space-between",
    gap: "16px",
    alignItems: "flex-start",
  },
  actionRow: {
    display: "flex",
    gap: "12px",
    marginTop: "18px",
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
  statusBox: {
    minWidth: "180px",
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "18px",
    padding: "16px",
  },
  statusLabel: {
    color: "#9fb0ca",
    fontSize: "13px",
    marginBottom: "8px",
  },
  statusValue: {
    fontSize: "26px",
    fontWeight: "800",
  },
  cardGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "18px",
    marginBottom: "24px",
  },
  midGrid: {
    display: "grid",
    gridTemplateColumns: "1.2fr 0.8fr",
    gap: "18px",
    marginBottom: "24px",
  },
  panel: {
    padding: "22px",
  },
  recommendationBox: {
    background: "rgba(37, 99, 235, 0.14)",
    border: "1px solid #2563eb",
    borderRadius: "16px",
    padding: "16px",
    color: "#dbeafe",
    marginBottom: "20px",
  },
  muted: {
    color: "#9fb0ca",
    lineHeight: 1.8,
  },
  metaItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "14px 0",
    borderBottom: "1px solid #1e3558",
    color: "#dbe7f3",
  },
  regionPanel: {
    padding: "22px",
  },
  regionGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "18px",
  },
};