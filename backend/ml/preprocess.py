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


def get_harvard_oxford_atlas():
    atlas = fetch_atlas_harvard_oxford(
        "cort-maxprob-thr25-2mm",
        data_dir=str(RAW_DIR)
    )
    labels = list(atlas.labels)

    # remove background if present at first position
    if labels and str(labels[0]).lower() in ["background", "0"]:
        labels = labels[1:]

    return atlas, labels


def build_connection_index_mapping(n_regions: int):
    """
    Maps conn_k -> (region_i, region_j)
    based on upper triangle indexing.
    """
    mapping = {}
    k = 0
    for i in range(n_regions):
        for j in range(i + 1, n_regions):
            mapping[f"conn_{k}"] = (i, j)
            k += 1
    return mapping


def extract_fmri_connectivity_features(file_path: str):
    """
    Returns:
      - fmri_features: dict of conn_* features
      - region_labels: list of atlas region names
      - connection_mapping: dict conn_k -> (i, j)
    """
    img = nib.load(file_path)

    atlas, region_labels = get_harvard_oxford_atlas()

    masker = NiftiLabelsMasker(
        labels_img=atlas.maps,
        standardize="zscore_sample",
        memory=str(CACHE_DIR),
        verbose=0
    )

    ts = masker.fit_transform(file_path)
    ts = np.asarray(ts)

    if ts.ndim == 1:
        ts = ts.reshape(1, -1)

    n_regions = ts.shape[1]
    connection_mapping = build_connection_index_mapping(n_regions)

    # fallback for 3D / single-timepoint case
    if ts.shape[0] < 2:
        roi_vals = ts[0]
        fmri_features = {}
        # fill only first n_regions as pseudo-features if needed
        for j, val in enumerate(roi_vals):
            fmri_features[f"conn_{j}"] = float(val)
        return fmri_features, region_labels, connection_mapping

    connectivity = ConnectivityMeasure(kind="correlation")
    corr = connectivity.fit_transform([ts])[0]
    corr = np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)

    iu = np.triu_indices_from(corr, k=1)
    feat = corr[iu]

    fmri_features = {}
    for j, val in enumerate(feat):
        fmri_features[f"conn_{j}"] = float(val)

    return fmri_features, region_labels, connection_mapping


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