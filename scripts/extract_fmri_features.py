from pathlib import Path
import numpy as np
import pandas as pd
from nilearn.datasets import fetch_adhd, fetch_atlas_harvard_oxford
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure

raw_dir = Path("data/raw")
proc_dir = Path("data/processed")
roi_dir = proc_dir / "roi"
conn_dir = proc_dir / "connectivity"

roi_dir.mkdir(parents=True, exist_ok=True)
conn_dir.mkdir(parents=True, exist_ok=True)

adhd = fetch_adhd(n_subjects=40, data_dir=str(raw_dir))
phen = adhd.phenotypic
if not isinstance(phen, pd.DataFrame):
    phen = pd.DataFrame(phen)

atlas = fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm', data_dir=str(raw_dir))
masker = NiftiLabelsMasker(
    labels_img=atlas.maps,
    standardize=True,
    memory=str(proc_dir / "cache"),
    verbose=0
)

connectivity = ConnectivityMeasure(kind="correlation")

all_rows = []

for i, func_file in enumerate(adhd.func):
    try:
        ts = masker.fit_transform(func_file)   # shape: timepoints x regions
        corr = connectivity.fit_transform([ts])[0]  # regions x regions

        # summarize connectivity into upper triangle features
        iu = np.triu_indices_from(corr, k=1)
        feat = corr[iu]

        row = {"sample_index": i}
        for j, val in enumerate(feat):
            row[f"conn_{j}"] = float(val)

        all_rows.append(row)

        np.save(roi_dir / f"roi_ts_{i}.npy", ts)
        np.save(conn_dir / f"conn_{i}.npy", corr)

        print(f"Processed sample {i+1}/{len(adhd.func)}")
    except Exception as e:
        print(f"Failed sample {i}: {e}")

feat_df = pd.DataFrame(all_rows)
feat_df.to_csv(proc_dir / "fmri_connectivity_features.csv", index=False)
print("\nSaved:", proc_dir / "fmri_connectivity_features.csv")