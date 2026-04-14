import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";

export default function Results() {
  const navigate = useNavigate();

  let result = null;
  try {
    result = JSON.parse(localStorage.getItem("assessment_result") || "null");
  } catch {
    result = null;
  }

  useEffect(() => {
    if (!result) {
      alert("No assessment result found. Please run an assessment first.");
      navigate("/app/assessment");
    }
  }, [result, navigate]);

  const topRegions = useMemo(() => {
    if (!result || !Array.isArray(result.top_regions)) return [];
    return result.top_regions.slice(0, 3);
  }, [result]);

  const topConnections = useMemo(() => {
    if (!result || !Array.isArray(result.top_connections)) return [];
    return result.top_connections.slice(0, 5);
  }, [result]);

  if (!result) return null;

  const lowConfidence = Number(result.confidence || 0) < 70;

  const getContributionLevel = (value) => {
    const score = Number(value || 0);
    if (score >= 20) return "High";
    if (score >= 10) return "Moderate";
    return "Mild";
  };

  const formatNumber = (value, digits = 2) => {
    const num = Number(value);
    if (Number.isNaN(num)) return "-";
    return num.toFixed(digits);
  };

  const hasOriginalPreview = Boolean(result.scan_preview_original);
  const hasOverlayPreview = Boolean(result.scan_preview_overlay);

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
      `ADHD Probability: ${formatNumber(result.adhd_probability)}`,
      `Control Probability: ${formatNumber(result.control_probability)}`,
      `BiLSTM Probability: ${formatNumber(result.bilstm_probability)}`,
      `Transformer Probability: ${formatNumber(result.transformer_probability)}`,
      `Uploaded File: ${result.uploaded_file || "-"}`,
      "",
      "Explainable AI Summary:",
      result.clinical_summary || "-",
      "",
      "Top Brain Regions:",
      ...topRegions.map(
        (r, i) =>
          `${i + 1}. ${r.region || "-"} - ${formatNumber(r.contribution)} (${r.level || getContributionLevel(r.contribution)})`
      ),
      "",
      "Top Connections:",
      ...topConnections.map(
        (c, i) =>
          `${i + 1}. ${c.connection || "-"} - ${formatNumber(c.contribution)}`
      ),
      "",
      "Scan Preview:",
      hasOriginalPreview ? "Original uploaded scan preview generated from the patient fMRI." : "Original scan preview not available.",
      hasOverlayPreview ? "AI overlay preview generated from the same uploaded scan." : "AI overlay preview not available.",
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
              Real uploaded scan preview with AI-highlighted brain regions and
              deep-learning ensemble prediction.
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
              {result.predicted_label || "-"}
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
          Low-confidence prediction detected. Please review the uploaded scan and
          AI-highlighted regions carefully.
        </div>
      )}

      <div style={styles.metricGrid}>
        <div className="glass-card" style={styles.metricCard}>
          <div style={styles.metricTitle}>Confidence</div>
          <div style={styles.metricValue}>
            {result.confidence ? `${result.confidence}%` : "-"}
          </div>
        </div>

        <div className="glass-card" style={styles.metricCard}>
          <div style={styles.metricTitle}>ADHD Probability</div>
          <div style={styles.metricValue}>{formatNumber(result.adhd_probability)}</div>
        </div>

        <div className="glass-card" style={styles.metricCard}>
          <div style={styles.metricTitle}>Control Probability</div>
          <div style={styles.metricValue}>{formatNumber(result.control_probability)}</div>
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
          <h3 style={{ ...styles.sectionTitle, marginBottom: 0 }}>
            Uploaded Scan Preview
          </h3>
        </div>

        <div style={styles.previewGrid}>
          <div style={styles.previewCard}>
            <div style={styles.previewLabel}>Original Uploaded Scan</div>
            {hasOriginalPreview ? (
              <img
                src={result.scan_preview_original}
                alt="Original uploaded brain scan preview"
                style={styles.previewImage}
              />
            ) : (
              <div style={styles.previewFallback}>
                Original scan preview not available.
              </div>
            )}
          </div>

          <div style={styles.previewCard}>
            <div style={styles.previewLabel}>AI Overlay on Uploaded Scan</div>
            {hasOverlayPreview ? (
              <img
                src={result.scan_preview_overlay}
                alt="AI overlay brain scan preview"
                style={styles.previewImage}
              />
            ) : (
              <div style={styles.previewFallback}>
                AI overlay preview not available.
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="glass-card" style={styles.sectionCard}>
        <div style={styles.sectionHeader}>
          <h3 style={{ ...styles.sectionTitle, marginBottom: 0 }}>
            AI-Highlighted Brain Regions
          </h3>
        </div>

        {topRegions.length > 0 ? (
          <div style={styles.regionGrid}>
            {topRegions.map((region, index) => {
              const level = region.level || getContributionLevel(region.contribution);

              return (
                <div key={index} style={styles.regionCard}>
                  <div>
                    <div style={styles.regionName}>
                      {region.region || `Atlas Region ${index + 1}`}
                    </div>
                    <div style={styles.regionSub}>
                      Most influential for this uploaded scan
                    </div>
                    <div style={styles.meaningText}>
                      {region.meaning ||
                        "Region identified by Explainable AI as influential for this scan."}
                    </div>
                  </div>

                  <div style={styles.regionBottom}>
                    <div style={styles.scoreText}>
                      Contribution: {formatNumber(region.contribution)}
                    </div>
                    <div style={styles.levelChip(level)}>{level}</div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p style={styles.muted}>No regional explanation available</p>
        )}
      </div>

      <div className="glass-card" style={styles.sectionCard}>
        <h3 style={styles.sectionTitle}>Top Region Connections</h3>

        {topConnections.length > 0 ? (
          <div style={styles.connectionList}>
            {topConnections.map((item, index) => (
              <div key={index} style={styles.connectionItem}>
                <div>
                  <div style={styles.connectionName}>
                    {item.connection || `Connection ${index + 1}`}
                  </div>
                  <div style={styles.connectionSub}>
                    Strongest region-to-region influence in this scan
                  </div>
                </div>

                <div style={styles.connectionScore}>
                  {formatNumber(item.contribution)}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={styles.muted}>No connection-level explanation available</p>
        )}
      </div>

      <div className="glass-card" style={styles.sectionCard}>
        <h3 style={styles.sectionTitle}>Model Output Details</h3>
        <div style={styles.metaGrid}>
          <div style={styles.metaItem}>
            <div style={styles.metaLabel}>Patient Name</div>
            <div style={styles.metaValue}>{result.patient_name || "-"}</div>
          </div>

          <div style={styles.metaItem}>
            <div style={styles.metaLabel}>Uploaded File</div>
            <div style={styles.metaValue}>{result.uploaded_file || "-"}</div>
          </div>

          <div style={styles.metaItem}>
            <div style={styles.metaLabel}>BiLSTM Probability</div>
            <div style={styles.metaValue}>{formatNumber(result.bilstm_probability)}</div>
          </div>

          <div style={styles.metaItem}>
            <div style={styles.metaLabel}>Transformer Probability</div>
            <div style={styles.metaValue}>{formatNumber(result.transformer_probability)}</div>
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
  previewGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    gap: "18px",
  },
  previewCard: {
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "18px",
    padding: "16px",
  },
  previewLabel: {
    fontSize: "14px",
    fontWeight: "700",
    marginBottom: "12px",
    color: "#dbeafe",
  },
  previewImage: {
    width: "100%",
    borderRadius: "14px",
    display: "block",
    border: "1px solid #274873",
    background: "#071321",
  },
  previewFallback: {
    minHeight: "220px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
    color: "#9fb0ca",
    background: "#071321",
    borderRadius: "14px",
    border: "1px solid #274873",
    padding: "20px",
  },
  regionGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
    gap: "16px",
  },
  regionCard: {
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "18px",
    padding: "18px",
    minHeight: "180px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
  },
  regionName: {
    fontWeight: "800",
    fontSize: "18px",
    marginBottom: "8px",
  },
  regionSub: {
    color: "#9fb0ca",
    fontSize: "13px",
    marginBottom: "10px",
  },
  meaningText: {
    color: "#dbeafe",
    fontSize: "13px",
    lineHeight: 1.6,
  },
  regionBottom: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    flexWrap: "wrap",
    marginTop: "16px",
  },
  scoreText: {
    color: "#dbeafe",
    fontSize: "13px",
    fontWeight: "600",
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
  connectionList: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  connectionItem: {
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "14px",
    padding: "16px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "14px",
  },
  connectionName: {
    fontWeight: "700",
    color: "#dbeafe",
  },
  connectionSub: {
    marginTop: "4px",
    color: "#9fb0ca",
    fontSize: "13px",
  },
  connectionScore: {
    color: "#93c5fd",
    fontWeight: "800",
    fontSize: "16px",
    whiteSpace: "nowrap",
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