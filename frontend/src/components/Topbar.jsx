import { Bell, Search, UserCircle2, LogOut } from "lucide-react";
import { useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function Topbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const inputRef = useRef(null);

  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const currentSearch = new URLSearchParams(location.search).get("search") || "";

  const goToSearch = (rawValue) => {
    const query = String(rawValue || "").trim();

    if (!query) {
      navigate("/app/patients");
      return;
    }

    navigate(`/app/patients?search=${encodeURIComponent(query)}`);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    goToSearch(inputRef.current?.value || "");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    localStorage.removeItem("assessment_result");
    navigate("/login");
  };

  return (
    <div style={styles.topbar}>
      <div>
        <h2 style={styles.title}>Clinical Dashboard</h2>
        <p style={styles.subtitle}>Neurodevelopmental assessment workflow</p>
      </div>

      <div style={styles.right}>
        <form style={styles.searchBox} onSubmit={handleSubmit}>
          <button
            type="submit"
            style={styles.searchBtn}
            title="Search patients"
          >
            <Search size={16} color="#9fb0ca" />
          </button>

          <input
            key={`${location.pathname}-${currentSearch}`}
            ref={inputRef}
            defaultValue={currentSearch}
            placeholder="Search patients by name, ID, age..."
            style={styles.input}
          />
        </form>

        <div style={styles.iconBox} title="No new alerts">
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
    minWidth: "320px",
  },
  searchBtn: {
    background: "transparent",
    border: "none",
    color: "inherit",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    padding: 0,
  },
  input: {
    border: "none",
    outline: "none",
    background: "transparent",
    margin: 0,
    padding: 0,
    color: "white",
    width: "100%",
    fontSize: "14px",
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
    color: "#dbeafe",
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
    cursor: "pointer",
  },
};