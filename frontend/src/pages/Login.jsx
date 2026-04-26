import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../api/axios";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      navigate("/app/dashboard");
    }
  }, [navigate]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrorMsg("");
    setSuccessMsg("");
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      const res = await API.post("/auth/login", form);

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);
      localStorage.setItem("user", JSON.stringify(res.data.user));

      setSuccessMsg("Login successful. Redirecting...");

      setTimeout(() => {
        navigate("/app/dashboard");
      }, 800);
    } catch (error) {
      setErrorMsg(error?.response?.data?.detail || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div className="glass-card" style={styles.card}>
        <h2 style={styles.title}>Doctor Login</h2>
        <p style={styles.sub}>Secure access to the NeuroAI clinical dashboard</p>

        {successMsg && <div style={styles.successBox}>{successMsg}</div>}
        {errorMsg && <div style={styles.errorBox}>{errorMsg}</div>}

        <form onSubmit={handleLogin}>
          <label style={styles.label}>Email</label>
          <input
            type="email"
            name="email"
            placeholder="doctor@example.com"
            value={form.email}
            onChange={handleChange}
            required
          />

          <label style={styles.label}>Password</label>
          <input
            type="password"
            name="password"
            placeholder="Enter password"
            value={form.password}
            onChange={handleChange}
            required
          />

          <button
            className="primary-btn"
            type="submit"
            style={{ width: "100%", marginTop: 10 }}
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p style={styles.footer}>
          Don’t have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "grid",
    placeItems: "center",
    background: "radial-gradient(circle at top, #14325f 0%, #071427 55%)",
    padding: "24px",
  },
  card: {
    width: "100%",
    maxWidth: "450px",
    padding: "28px",
  },
  title: {
    marginBottom: "8px",
  },
  sub: {
    color: "#9fb0ca",
    marginBottom: "22px",
  },
  label: {
    display: "block",
    marginBottom: "6px",
    marginTop: "10px",
    fontWeight: "600",
  },
  successBox: {
    marginBottom: "16px",
    background: "rgba(16, 185, 129, 0.14)",
    border: "1px solid #10b981",
    color: "#d1fae5",
    borderRadius: "12px",
    padding: "12px 14px",
    fontSize: "14px",
    fontWeight: "600",
  },
  errorBox: {
    marginBottom: "16px",
    background: "rgba(239, 68, 68, 0.14)",
    border: "1px solid #ef4444",
    color: "#fecaca",
    borderRadius: "12px",
    padding: "12px 14px",
    fontSize: "14px",
    fontWeight: "600",
  },
  footer: {
    marginTop: "18px",
    color: "#9fb0ca",
  },
};