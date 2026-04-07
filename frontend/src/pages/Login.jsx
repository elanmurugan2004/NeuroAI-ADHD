import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../api/axios";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      navigate("/app/dashboard");
    }
  }, [navigate]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post("/auth/login", form);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      alert("Login successful");
      navigate("/app/dashboard");
    } catch (error) {
      alert(error?.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div style={styles.page}>
      <div className="glass-card" style={styles.card}>
        <h2>Doctor Login</h2>
        <p style={styles.sub}>Secure access to the NeuroAI clinical dashboard</p>

        <form onSubmit={handleLogin}>
          <label>Email</label>
          <input
            type="email"
            name="email"
            placeholder="doctor@example.com"
            value={form.email}
            onChange={handleChange}
            required
          />

          <label>Password</label>
          <input
            type="password"
            name="password"
            placeholder="Enter password"
            value={form.password}
            onChange={handleChange}
            required
          />

          <button className="primary-btn" type="submit" style={{ width: "100%", marginTop: 10 }}>
            Login
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
  sub: {
    color: "#9fb0ca",
    marginBottom: "22px",
  },
  footer: {
    marginTop: "18px",
    color: "#9fb0ca",
  },
};