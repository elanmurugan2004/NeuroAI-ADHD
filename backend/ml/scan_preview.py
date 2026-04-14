from io import BytesIO
import base64
import numpy as np
import nibabel as nib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nilearn.datasets import fetch_atlas_harvard_oxford
from nilearn.image import resample_to_img


def _normalize_slice(slice_2d: np.ndarray) -> np.ndarray:
    arr = np.nan_to_num(slice_2d.astype(float), nan=0.0, posinf=0.0, neginf=0.0)

    if np.all(arr == 0):
        return arr

    low, high = np.percentile(arr, [1, 99])
    if high <= low:
        low = np.min(arr)
        high = np.max(arr)

    if high <= low:
        return np.zeros_like(arr)

    arr = np.clip((arr - low) / (high - low + 1e-8), 0, 1)
    return arr


def _fig_to_base64(fig) -> str:
    buf = BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=110,
        bbox_inches="tight",
        pad_inches=0.02,
        facecolor="#071321"
    )
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def _find_top_region_indices(region_labels, top_regions, max_regions=3):
    if not region_labels or not top_regions:
        return []

    indices = []
    lower_labels = [str(x).strip().lower() for x in region_labels]

    for item in top_regions[:max_regions]:
        if isinstance(item, dict):
            target = str(item.get("region", "")).strip().lower()
        else:
            target = str(item).strip().lower()

        if not target:
            continue

        found_idx = None

        for i, label in enumerate(lower_labels):
            if target == label:
                found_idx = i
                break

        if found_idx is None:
            for i, label in enumerate(lower_labels):
                if target in label or label in target:
                    found_idx = i
                    break

        if found_idx is not None and found_idx not in indices:
            indices.append(found_idx)

    return indices


def generate_scan_previews(file_path: str, region_labels=None, top_regions=None):
    img = nib.load(file_path)
    data = img.get_fdata()

    if data.ndim == 4:
        volume = np.nanmean(data, axis=3)
    elif data.ndim == 3:
        volume = data
    else:
        raise ValueError("Expected 3D or 4D NIfTI image for preview generation")

    volume = np.nan_to_num(volume, nan=0.0, posinf=0.0, neginf=0.0)

    z_idx = volume.shape[2] // 2
    base_slice = np.rot90(volume[:, :, z_idx])
    base_slice = _normalize_slice(base_slice)

    fig1, ax1 = plt.subplots(figsize=(4.2, 4.2), facecolor="#071321")
    ax1.imshow(base_slice, cmap="gray")
    ax1.axis("off")
    original_base64 = _fig_to_base64(fig1)

    atlas = fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    mean_img = nib.Nifti1Image(volume, img.affine, img.header)

    atlas_img = resample_to_img(
        atlas.maps,
        mean_img,
        interpolation="nearest",
        force_resample=True,
        copy_header=True,
    )
    atlas_data = atlas_img.get_fdata()

    region_indices = _find_top_region_indices(region_labels, top_regions, max_regions=3)

    overlay_mask = np.zeros_like(atlas_data[:, :, z_idx], dtype=bool)
    for region_idx in region_indices:
        atlas_value = region_idx + 1
        overlay_mask |= (atlas_data[:, :, z_idx] == atlas_value)

    overlay_mask = np.rot90(overlay_mask)

    fig2, ax2 = plt.subplots(figsize=(4.2, 4.2), facecolor="#071321")
    ax2.imshow(base_slice, cmap="gray")
    if np.any(overlay_mask):
        ax2.imshow(overlay_mask, cmap="autumn", alpha=0.45)
    ax2.axis("off")
    overlay_base64 = _fig_to_base64(fig2)

    return original_base64, overlay_base64