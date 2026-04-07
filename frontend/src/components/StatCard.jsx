export default function StatCard({ title, value, hint }) {
  return (
    <div className="glass-card" style={styles.card}>
      <div style={styles.title}>{title}</div>
      <div style={styles.value}>{value}</div>
      <div style={styles.hint}>{hint}</div>
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
    fontSize: "28px",
    fontWeight: "800",
    marginBottom: "8px",
  },
  hint: {
    color: "#7dd3fc",
    fontSize: "13px",
  },
};