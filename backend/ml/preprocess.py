import numpy as np
from nilearn.datasets import fetch_atlas_harvard_oxford
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure


def _to_clean_label(x):
    if isinstance(x, bytes):
        x = x.decode("utf-8", errors="ignore")
    return str(x).strip()


def _clean_region_labels(raw_labels, n_regions):
    labels = [_to_clean_label(x) for x in raw_labels]

    labels = [
        x for x in labels
        if x and x.lower() not in ["background", "unknown", "nan"]
    ]

    if len(labels) > n_regions:
        labels = labels[:n_regions]
    elif len(labels) < n_regions:
        labels += [f"Atlas Region {i}" for i in range(len(labels), n_regions)]

    return labels


def extract_fmri_connectivity_features(file_path: str):
    """
    Extract ROI-wise functional connectivity features from uploaded 4D fMRI NIfTI.

    Returns:
    - fmri_features: 1D numpy array of connectivity values
    - region_labels: list[str]
    - connection_mapping: dict[int, tuple[int, int]]
    """

    atlas = fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")

    masker = NiftiLabelsMasker(
        labels_img=atlas.maps,
        standardize="zscore_sample"
    )

    ts = masker.fit_transform(file_path)

    if ts is None or len(ts.shape) != 2 or ts.shape[1] == 0:
        raise ValueError("Could not extract ROI time series from uploaded fMRI scan.")

    region_labels = _clean_region_labels(atlas.labels, ts.shape[1])

    connectivity = ConnectivityMeasure(
        kind="correlation",
        standardize="zscore_sample"
    )
    corr = connectivity.fit_transform([ts])[0]

    tri_upper = np.triu_indices(corr.shape[0], k=1)
    fmri_features = corr[tri_upper].astype(float)

    connection_mapping = {
        idx: (int(i), int(j))
        for idx, (i, j) in enumerate(zip(tri_upper[0], tri_upper[1]))
    }

    return fmri_features, region_labels, connection_mapping