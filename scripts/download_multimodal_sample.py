from pathlib import Path
import pandas as pd
from nilearn.datasets import fetch_adhd

root = Path("data/raw")
root.mkdir(parents=True, exist_ok=True)

print("Downloading ADHD sample with phenotypic info and preprocessed fMRI...")
adhd = fetch_adhd(n_subjects=40, data_dir=str(root))

phenotypic = adhd.phenotypic
if not isinstance(phenotypic, pd.DataFrame):
    phenotypic = pd.DataFrame(phenotypic)

csv_path = root / "adhd_phenotypic_40.csv"
phenotypic.to_csv(csv_path, index=False)

print("\nDone.")
print("Phenotypic CSV:", csv_path)
print("fMRI files count:", len(adhd.func))
print("First fMRI file:", adhd.func[0] if len(adhd.func) else "None")
print("Columns:", list(phenotypic.columns))