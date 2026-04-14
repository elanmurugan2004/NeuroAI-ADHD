import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PHENO_PATH = ROOT / "data" / "raw" / "adhd_phenotypic_40.csv"
CONN_PATH = ROOT / "data" / "processed" / "fmri_connectivity_features.csv"
ID_PATH = ROOT / "data" / "raw" / "adhd" / "ADHD200_40subs_ID.txt"
OUT_PATH = ROOT / "data" / "processed" / "training_multimodal.csv"

# 1. Load files
pheno = pd.read_csv(PHENO_PATH)
conn = pd.read_csv(CONN_PATH)
ids = pd.read_csv(ID_PATH, header=None, names=["subject"])

# 2. Clean subject IDs
ids["subject"] = pd.to_numeric(ids["subject"], errors="coerce")
ids = ids.dropna().reset_index(drop=True)
ids["subject"] = ids["subject"].astype(int)

# 3. Sort connectivity by sample_index
conn = conn.sort_values("sample_index").reset_index(drop=True)

print("Phenotypic raw rows:", len(pheno))
print("Connectivity rows:", len(conn))
print("ID rows:", len(ids))

# 4. Make sure connectivity rows match ID rows
if len(conn) != len(ids):
    raise ValueError(
        f"Connectivity rows and ID rows mismatch: connectivity={len(conn)}, ids={len(ids)}"
    )

# 5. Attach subject IDs to connectivity file
conn.insert(0, "subject", ids["subject"])

# 6. Keep only needed phenotypic columns
keep_cols = ["Subject", "age", "sex", "handedness", "site", "adhd"]
missing = [c for c in keep_cols if c not in pheno.columns]
if missing:
    raise ValueError(f"Missing columns in phenotypic file: {missing}")

pheno_small = pheno[keep_cols].copy()
pheno_small = pheno_small.rename(columns={
    "Subject": "subject",
    "adhd": "diagnosis"
})

# 7. Clean phenotypic columns
pheno_small["subject"] = pd.to_numeric(pheno_small["subject"], errors="coerce")
pheno_small["diagnosis"] = pd.to_numeric(pheno_small["diagnosis"], errors="coerce")

pheno_small = pheno_small.dropna(subset=["subject", "diagnosis"]).reset_index(drop=True)
pheno_small["subject"] = pheno_small["subject"].astype(int)
pheno_small["diagnosis"] = pheno_small["diagnosis"].astype(int)

print("Phenotypic labeled rows:", len(pheno_small))
print("Diagnosis counts:", pheno_small["diagnosis"].value_counts().to_dict())

# 8. Merge by subject
merged = pd.merge(pheno_small, conn, on="subject", how="inner")

# 9. Drop sample_index after merge
if "sample_index" in merged.columns:
    merged = merged.drop(columns=["sample_index"])

print("Merged rows:", len(merged))
print("Merged columns:", len(merged.columns))

# 10. Check if any phenotypic subjects were not found
missing_subjects = sorted(set(pheno_small["subject"]) - set(conn["subject"]))
print("Missing subjects not found in connectivity:", missing_subjects)

# 11. Save final training file
merged.to_csv(OUT_PATH, index=False)

print(f"Saved: {OUT_PATH}")
print("First columns:", merged.columns[:12].tolist())