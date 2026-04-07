export default function UploadBox({ fileName, onChange }) {
  return (
    <div className="glass-card" style={styles.box}>
      <h3 style={{ marginTop: 0 }}>MRI / fMRI Upload</h3>
      <p style={{ color: "#9fb0ca", marginTop: 0 }}>
        Upload `.nii` or `.nii.gz` file for neuroimaging-based assessment.
      </p>

      <input type="file" onChange={onChange} />

      <div style={styles.fileInfo}>
        {fileName ? `Selected file: ${fileName}` : "No file selected"}
      </div>
    </div>
  );
}

const styles = {
  box: {
    padding: "20px",
  },
  fileInfo: {
    marginTop: "12px",
    color: "#93c5fd",
    fontSize: "14px",
  },
};