from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from nilearn.datasets import fetch_atlas_harvard_oxford
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "data" / "raw"
CACHE_DIR = ROOT_DIR / "data" / "processed" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def extract_fmri_connectivity_features(file_path: str) -> dict:
    img = nib.load(file_path)
    shape = img.shape

    atlas = fetch_atlas_harvard_oxford(
        "cort-maxprob-thr25-2mm",
        data_dir=str(RAW_DIR)
    )

    masker = NiftiLabelsMasker(
        labels_img=atlas.maps,
        standardize="zscore_sample",
        memory=str(CACHE_DIR),
        verbose=0
    )

    ts = masker.fit_transform(file_path)

    # If uploaded file is 3D MRI, ts may be 1D or single-sample.
    # Convert safely so backend does not crash.
    ts = np.asarray(ts)

    if ts.ndim == 1:
        ts = ts.reshape(1, -1)

    # If there is only one timepoint, correlation matrix is not meaningful.
    # Fall back to ROI mean features expanded into conn_* format.
    if ts.shape[0] < 2:
        row = {}
        roi_vals = ts[0]
        for j, val in enumerate(roi_vals):
            row[f"conn_{j}"] = float(val)
        return row

    connectivity = ConnectivityMeasure(kind="correlation")
    corr = connectivity.fit_transform([ts])[0]

    # Replace NaN/Inf safely
    corr = np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)

    iu = np.triu_indices_from(corr, k=1)
    feat = corr[iu]

    row = {}
    for j, val in enumerate(feat):
        row[f"conn_{j}"] = float(val)

    return row


def build_multimodal_input(payload: dict, meta: dict, fmri_features: dict) -> pd.DataFrame:
    row = {}

    for col in meta["feature_cols"]:
        key = col.lower()

        if col.startswith("conn_"):
            row[col] = fmri_features.get(col, 0.0)
        elif key == "age":
            row[col] = payload.get("age")
        elif key in ["sex", "gender"]:
            row[col] = payload.get("gender")
        elif key in ["iq", "fsiq"]:
            row[col] = payload.get("iq")
        elif key == "handedness":
            row[col] = payload.get("handedness")
        elif key == "site":
            row[col] = payload.get("site")
        elif key in ["med_status", "medication"]:
            row[col] = payload.get("medication", None)
        elif key == "subtype":
            row[col] = payload.get("subtype", None)
        else:
            row[col] = payload.get(col, None)

    return pd.DataFrame([row])