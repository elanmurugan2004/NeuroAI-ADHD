export default function RegionCard({ name, contribution, score }) {
  return (
    <div className="glass-card" style={styles.card}>
      <div style={styles.name}>{name}</div>
      <div style={styles.row}>
        <span className="badge">{contribution}</span>
        <span style={styles.score}>Score: {score}</span>
      </div>
    </div>
  );
}

const styles = {
  card: {
    padding: "18px",
  },
  name: {
    fontSize: "16px",
    fontWeight: "700",
    marginBottom: "12px",
  },
  row: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  score: {
    color: "#9fb0ca",
    fontSize: "14px",
  },
};