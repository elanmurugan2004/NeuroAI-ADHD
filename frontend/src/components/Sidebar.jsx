import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  FilePlus2,
  History,
  BrainCircuit,
  Home,
} from "lucide-react";

export default function Sidebar() {
  const location = useLocation();

  const items = [
    { label: "Home", to: "/", icon: <Home size={18} /> },
    { label: "Dashboard", to: "/app/dashboard", icon: <LayoutDashboard size={18} /> },
    { label: "Patients", to: "/app/patients", icon: <Users size={18} /> },
    { label: "New Assessment", to: "/app/assessment", icon: <FilePlus2 size={18} /> },
    { label: "History", to: "/app/history", icon: <History size={18} /> },
    { label: "Results", to: "/app/results", icon: <BrainCircuit size={18} /> },
  ];

  return (
    <aside style={styles.sidebar}>
      <div>
        <div style={styles.logoBox}>
          <div style={styles.logoIcon}>N</div>
          <div>
            <div style={styles.logoTitle}>NeuroAI-ADHD</div>
            <div style={styles.logoSub}>Clinical AI Suite</div>
          </div>
        </div>

        <div style={styles.menu}>
          {items.map((item) => {
            const active = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                style={{
                  ...styles.link,
                  ...(active ? styles.activeLink : {}),
                }}
              >
                {item.icon}
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>

      <div style={styles.footerCard}>
        <div className="badge">Hospital Mode</div>
        <p style={{ margin: "12px 0 0", color: "#9fb0ca", fontSize: "13px", lineHeight: 1.7 }}>
          AI-assisted ADHD analysis with explainable clinical support and patient workflow management.
        </p>
      </div>
    </aside>
  );
}

const styles = {
  sidebar: {
    width: "270px",
    background: "#081426",
    borderRight: "1px solid #193251",
    padding: "22px 16px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
  },
  logoBox: {
    display: "flex",
    gap: "12px",
    alignItems: "center",
    marginBottom: "28px",
  },
  logoIcon: {
    width: "42px",
    height: "42px",
    borderRadius: "14px",
    background: "linear-gradient(135deg, #2563eb, #60a5fa)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "800",
    color: "white",
  },
  logoTitle: {
    fontWeight: "700",
    fontSize: "16px",
  },
  logoSub: {
    color: "#8ba1c2",
    fontSize: "12px",
  },
  menu: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  link: {
    display: "flex",
    gap: "12px",
    alignItems: "center",
    padding: "14px 14px",
    borderRadius: "14px",
    color: "#c7d2e5",
    border: "1px solid transparent",
  },
  activeLink: {
    background: "linear-gradient(180deg, #0d213d 0%, #102849 100%)",
    border: "1px solid #244574",
    color: "#ffffff",
  },
  footerCard: {
    background: "#0c1c34",
    border: "1px solid #1e3558",
    borderRadius: "18px",
    padding: "16px",
  },
};