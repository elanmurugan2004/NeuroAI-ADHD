import { Bell, Search, UserCircle2, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Topbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("assessment_result");
    alert("Logged out successfully");
    navigate("/login");
  };

  return (
    <div style={styles.topbar}>
      <div>
        <h2 style={styles.title}>Clinical Dashboard</h2>
        <p style={styles.subtitle}>Neurodevelopmental assessment workflow</p>
      </div>

      <div style={styles.right}>
        <div style={styles.searchBox}>
          <Search size={16} color="#9fb0ca" />
          <input placeholder="Search patients, reports..." style={styles.input} />
        </div>

        <div style={styles.iconBox}>
          <Bell size={18} />
        </div>

        <div style={styles.profile}>
          <UserCircle2 size={34} />
          <div>
            <div style={{ fontSize: "14px", fontWeight: 700 }}>
              {user.full_name || "Doctor"}
            </div>
            <div style={{ fontSize: "12px", color: "#9fb0ca" }}>
              {user.role || "doctor"}
            </div>
          </div>
        </div>

        <button style={styles.logoutBtn} onClick={handleLogout}>
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </div>
  );
}

const styles = {
  topbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "16px",
    padding: "18px 24px",
    borderBottom: "1px solid #18314e",
    background: "#081426",
    flexWrap: "wrap",
  },
  title: {
    margin: 0,
    fontSize: "22px",
  },
  subtitle: {
    margin: "6px 0 0",
    color: "#9fb0ca",
    fontSize: "13px",
  },
  right: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
    flexWrap: "wrap",
  },
  searchBox: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "14px",
    padding: "8px 12px",
    minWidth: "260px",
  },
  input: {
    border: "none",
    background: "transparent",
    margin: 0,
    padding: 0,
  },
  iconBox: {
    width: "42px",
    height: "42px",
    borderRadius: "14px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#0d203d",
    border: "1px solid #21406a",
  },
  profile: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    background: "#0d203d",
    border: "1px solid #21406a",
    borderRadius: "16px",
    padding: "8px 12px",
  },
  logoutBtn: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    background: "#132743",
    color: "white",
    border: "1px solid #274873",
    borderRadius: "14px",
    padding: "10px 14px",
  },
};