from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

raw_csv = Path("data/raw/adhd_phenotypic_40.csv")
fmri_csv = Path("data/processed/fmri_connectivity_features.csv")
model_dir = Path("models")
model_dir.mkdir(parents=True, exist_ok=True)

phen = pd.read_csv(raw_csv)
fmri = pd.read_csv(fmri_csv)

# sample_index is used because nilearn fetch_adhd returns aligned 40-subject sample order
phen = phen.reset_index().rename(columns={"index": "sample_index"})
df = phen.merge(fmri, on="sample_index", how="inner")

# --- find target column ---
lower_map = {c.lower(): c for c in df.columns}
target_candidates = ["adhd", "dx", "diagnosis", "label"]
target_col = None
for c in target_candidates:
    if c in lower_map:
        target_col = lower_map[c]
        break

if target_col is None:
    raise ValueError(f"Target column not found. Available columns: {list(df.columns)}")

def to_binary(v):
    s = str(v).strip().lower()
    if s in {"1", "adhd", "yes", "true", "case"}:
        return 1
    if s in {"0", "control", "no", "false", "typical"}:
        return 0
    try:
        num = float(v)
        return 1 if num == 1 else 0
    except:
        return None

y = df[target_col].apply(to_binary)
df = df.loc[y.notna()].copy()
y = y.loc[y.notna()].astype(int)

# choose phenotype columns if present
preferred = ["age", "sex", "gender", "iq", "fsiq", "handedness", "site", "med_status", "medication"]
phenotype_cols = []
for pref in preferred:
    for col in df.columns:
        if col.lower() == pref:
            phenotype_cols.append(col)
phenotype_cols = list(dict.fromkeys(phenotype_cols))

fmri_cols = [c for c in df.columns if c.startswith("conn_")]
feature_cols = phenotype_cols + fmri_cols

X = df[feature_cols].copy()

numeric_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
categorical_cols = [c for c in X.columns if c not in numeric_cols]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median"))
        ]), numeric_cols),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), categorical_cols),
    ]
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipeline.fit(X_train, y_train)

pred = pipeline.predict(X_test)
proba = pipeline.predict_proba(X_test)[:, 1]

print("Accuracy:", accuracy_score(y_test, pred))
try:
    print("ROC AUC:", roc_auc_score(y_test, proba))
except Exception as e:
    print("ROC AUC unavailable:", e)

print(classification_report(y_test, pred))

joblib.dump(pipeline, model_dir / "multimodal_pipeline.joblib")

meta = {
    "target_col": target_col,
    "phenotype_cols": phenotype_cols,
    "fmri_feature_count": len(fmri_cols),
    "feature_cols": feature_cols,
}
with open(model_dir / "multimodal_meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)

print("\nSaved models/multimodal_pipeline.joblib")
print("Saved models/multimodal_meta.json")