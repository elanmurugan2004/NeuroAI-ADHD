export default function PredictionCard({ title, value, color }) {
  return (
    <div className="glass-card" style={styles.card}>
      <div style={styles.title}>{title}</div>
      <div style={{ ...styles.value, color: color || "#fff" }}>{value}</div>
    </div>
  );
}

const styles = {
  card: {
    padding: "20px",
  },
  title: {
    color: "#9fb0ca",
    fontSize: "14px",
    marginBottom: "10px",
  },
  value: {
    fontWeight: "800",
    fontSize: "26px",
  },
};