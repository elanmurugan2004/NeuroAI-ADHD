import { useEffect, useState } from "react";
import API from "../api/axios";
import StatCard from "../components/StatCard";

export default function Dashboard() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const [stats, setStats] = useState({
    total_patients: 0,
    total_assessments: 0,
    latest_prediction: "N/A",
    latest_confidence: "N/A",
    review_status: "No Data",
  });

  const [recentAssessments, setRecentAssessments] = useState([]);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const statsRes = await API.get("/dashboard/stats");
        setStats(statsRes.data);

        const assessmentRes = await API.get("/assessments/");
        setRecentAssessments(assessmentRes.data.slice(0, 5));
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
      }
    };

    loadDashboardData();
  }, []);

  const lowConfidence =
    stats.latest_confidence !== "N/A" &&
    parseFloat(String(stats.latest_confidence).replace("%", "")) < 70;

  return (
    <div className="page">
      <div className="glass-card" style={styles.hero}>
        <div>
          <div className="badge">Doctor Workspace</div>
          <h1 style={styles.title}>Welcome back, {user.full_name || "Doctor"}</h1>
          <p style={styles.subtitle}>
            Manage patients, run AI-powered ADHD assessments, review explainable outputs,
            and maintain structured clinical records from one dashboard.
          </p>

          <div style={styles.heroActions}>
            <div className="badge">Explainable AI Enabled</div>
            <div className="badge">Secure Clinical Access</div>
            <div className="badge">Assessment Workflow Ready</div>
          </div>
        </div>
      </div>

      <div style={styles.statsGrid}>
        <StatCard title="Total Patients" value={stats.total_patients} hint="Registered patient records" />
        <StatCard title="Total Assessments" value={stats.total_assessments} hint="All saved AI predictions" />
        <StatCard title="Latest Prediction" value={stats.latest_prediction} hint={`Confidence: ${stats.latest_confidence}`} />
        <StatCard title="Review Status" value={stats.review_status} hint="Latest assessment state" />
      </div>

      {lowConfidence && (
        <div style={styles.warningBox}>
          Low-confidence latest prediction detected. Specialist review is strongly recommended.
        </div>
      )}

      <div style={styles.lowerGrid}>
        <div className="glass-card" style={styles.panel}>
          <h3 style={{ marginTop: 0 }}>Recent Assessments</h3>

          {recentAssessments.length > 0 ? (
            <div style={styles.activityList}>
              {recentAssessments.map((item) => (
                <div key={item.id} style={styles.activityRow}>
                  <div>
                    <div style={styles.activityTitle}>
                      {item.patient_name || `Patient ${item.patient_id}`}
                    </div>
                    <div style={styles.activitySub}>
                      Prediction: {item.predicted_label} • Confidence: {item.confidence}%
                    </div>
                  </div>
                  <div className="badge">#{item.id}</div>
                </div>
              ))}
            </div>
          ) : (
            <p style={styles.muted}>No recent assessments found</p>
          )}
        </div>

        <div className="glass-card" style={styles.panel}>
          <h3 style={{ marginTop: 0 }}>Clinical Readiness</h3>
          <p style={styles.muted}>
            The interface is designed for hospital-style presentation with patient
            workflow support, explainable AI summaries, and diagnostic assistance.
          </p>

          <div style={styles.notice}>
            <strong>Important:</strong>
            <p style={{ margin: "8px 0 0", color: "#cbd5e1", lineHeight: 1.7 }}>
              AI output supports doctors and should always be reviewed with behavioral,
              imaging, and clinical evaluation before final decision making.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  hero: {
    padding: "24px",
    marginBottom: "24px",
  },
  title: {
    margin: "14px 0 10px",
  },
  subtitle: {
    color: "#9fb0ca",
    lineHeight: 1.7,
    maxWidth: "800px",
  },
  heroActions: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap",
    marginTop: "18px",
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "18px",
    marginBottom: "24px",
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
  lowerGrid: {
    display: "grid",
    gridTemplateColumns: "1.1fr 0.9fr",
    gap: "18px",
  },
  panel: {
    padding: "22px",
  },
  activityList: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  activityRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    padding: "14px 16px",
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "14px",
  },
  activityTitle: {
    fontWeight: "700",
  },
  activitySub: {
    color: "#9fb0ca",
    fontSize: "13px",
    marginTop: "4px",
  },
  muted: {
    color: "#9fb0ca",
    lineHeight: 1.8,
  },
  notice: {
    marginTop: "18px",
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "16px",
    padding: "16px",
  },
};