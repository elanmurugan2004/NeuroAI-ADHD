import { Link } from "react-router-dom";
import { Brain, ShieldCheck, Activity, FileBarChart2 } from "lucide-react";

export default function Home() {
  const features = [
    {
      icon: <Brain size={22} />,
      title: "Multimodal ADHD Analysis",
      text: "Combines behavioral and neuro-clinical inputs for AI-assisted prediction.",
    },
    {
      icon: <ShieldCheck size={22} />,
      title: "Clinical Safety Workflow",
      text: "Doctor-oriented secure system with protected medical access.",
    },
    {
      icon: <Activity size={22} />,
      title: "Explainable Prediction",
      text: "Highlights important regions and generates clear clinical interpretation.",
    },
    {
      icon: <FileBarChart2 size={22} />,
      title: "Assessment History",
      text: "Maintain longitudinal patient reports and prediction summaries.",
    },
  ];

  return (
    <div style={styles.page}>
      <div style={styles.nav}>
        <div style={styles.logo}>NeuroAI-ADHD</div>
        <div style={styles.navLinks}>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
        </div>
      </div>

      <div style={styles.hero}>
        <div style={styles.left}>
          <div className="badge">AI-Assisted Neurodevelopment Screening</div>
          <h1 style={styles.title}>
            ADHD Detection and Clinical Decision Support using Explainable AI
          </h1>
          <p style={styles.text}>
            Premium doctor-facing platform for patient management, multimodal
            assessment, prediction review, and explainable neuro-clinical output.
          </p>

          <div style={styles.actions}>
            <Link to="/login">
              <button className="primary-btn">Doctor Login</button>
            </Link>
            <Link to="/register">
              <button className="secondary-btn">Create Account</button>
            </Link>
          </div>
        </div>

        <div style={styles.right} className="glass-card">
          <h3 style={{ marginTop: 0 }}>Clinical System Highlights</h3>
          <div style={styles.grid}>
            {features.map((f, i) => (
              <div key={i} style={styles.featureCard}>
                <div style={styles.featureIcon}>{f.icon}</div>
                <div style={styles.featureTitle}>{f.title}</div>
                <div style={styles.featureText}>{f.text}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "radial-gradient(circle at top left, #0f2b55 0%, #071427 45%, #040b16 100%)",
    padding: "28px",
  },
  nav: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "40px",
  },
  logo: {
    fontSize: "22px",
    fontWeight: "800",
  },
  navLinks: {
    display: "flex",
    gap: "22px",
    color: "#cbd5e1",
  },
  hero: {
    display: "grid",
    gridTemplateColumns: "1.1fr 0.9fr",
    gap: "24px",
    alignItems: "stretch",
    minHeight: "70vh",
  },
  left: {
    padding: "40px 12px 40px 0",
  },
  title: {
    fontSize: "52px",
    lineHeight: 1.1,
    margin: "18px 0",
    maxWidth: "760px",
    letterSpacing: "-1px",
  },
  text: {
    color: "#a6b7d1",
    fontSize: "18px",
    lineHeight: 1.7,
    maxWidth: "650px",
  },
  actions: {
    display: "flex",
    gap: "14px",
    marginTop: "26px",
  },
  right: {
    padding: "24px",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "16px",
  },
  featureCard: {
    background: "#0d203b",
    border: "1px solid #1f365a",
    borderRadius: "18px",
    padding: "18px",
  },
  featureIcon: {
    color: "#60a5fa",
    marginBottom: "12px",
  },
  featureTitle: {
    fontWeight: "700",
    marginBottom: "8px",
  },
  featureText: {
    color: "#9fb0ca",
    fontSize: "14px",
    lineHeight: 1.6,
  },
};