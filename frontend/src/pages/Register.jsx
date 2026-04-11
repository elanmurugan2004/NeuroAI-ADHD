import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../api/axios";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "doctor",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
  e.preventDefault();

  try {
    await API.post("/auth/register", {
      full_name: form.full_name,
      email: form.email,
      password: form.password,
      role: form.role,
    });

    alert("Registration successful");
    navigate("/login");
  } catch (error) {
    console.log(error.response?.data); // 👈 IMPORTANT DEBUG
    alert(error?.response?.data?.detail || "Registration failed");
  }
};

  return (
    <div style={styles.page}>
      <div className="glass-card" style={styles.card}>
        <h2>Create Doctor Account</h2>
        <p style={styles.sub}>Register securely for ADHD clinical workflow access</p>

        <form onSubmit={handleRegister}>
          <label>Full Name</label>
          <input
            name="full_name"
            placeholder="Dr John"
            value={form.full_name}
            onChange={handleChange}
            required
          />

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
            placeholder="Create password"
            value={form.password}
            onChange={handleChange}
            required
          />

          <label>Role</label>
          <input
            name="role"
            value={form.role}
            onChange={handleChange}
            required
          />

          <button className="primary-btn" type="submit" style={{ width: "100%", marginTop: 10 }}>
            Register
          </button>
        </form>

        <p style={styles.footer}>
          Already registered? <Link to="/login">Login</Link>
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
    maxWidth: "500px",
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