from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional
import uuid
import traceback
import base64

import matplotlib
matplotlib.use("Agg")

import pandas as pd
import numpy as np
import nibabel as nib

from nilearn.datasets import fetch_atlas_harvard_oxford
from nilearn.image import mean_img, new_img_like, resample_to_img
from nilearn.plotting import plot_img, plot_roi

from app.database import get_db
from app.models import Patient, Assessment, User
from app.auth import get_current_user
from ml.preprocess import extract_fmri_connectivity_features
from ml.predictor import predict_adhd_ensemble
from ml.explainability import explain_multimodal_prediction

router = APIRouter(prefix="/assessments", tags=["Assessments"])

ROOT_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT_DIR / "uploads"
PREVIEW_DIR = UPLOAD_DIR / "previews"

UPLOAD_DIR.mkdir(exist_ok=True)
PREVIEW_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE_MB = 300
MIN_AGE = 7
MAX_AGE = 17


def _normalize_sex(gender: str) -> str:
    value = str(gender).strip().lower()
    if value == "male":
        return "M"
    if value == "female":
        return "F"
    return str(gender).strip()


def _normalize_handedness(handedness: str) -> str:
    value = str(handedness).strip().lower()
    if value == "right":
        return "R"
    if value == "left":
        return "L"
    if value in ["both", "ambidextrous"]:
        return "A"
    return str(handedness).strip()


def _extract_primary_region_name(top_regions) -> str:
    if not top_regions:
        return "AI-highlighted brain regions"

    first = top_regions[0]

    if isinstance(first, dict):
        return (
            first.get("region")
            or first.get("name")
            or first.get("label")
            or "AI-highlighted brain regions"
        )

    return str(first)


def _file_to_data_url(file_path: Path) -> Optional[str]:
    if not file_path.exists():
        return None
    encoded = base64.b64encode(file_path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def _match_region_to_atlas_value(region_name: str, atlas_labels) -> Optional[int]:
    target = str(region_name).strip().lower()
    if not target:
        return None

    # exact match
    for idx, atlas_name in enumerate(atlas_labels):
        atlas_name = str(atlas_name).strip()
        atlas_lower = atlas_name.lower()

        if idx == 0:
            continue
        if not atlas_name or atlas_lower in {"background", "unknown", "nan"}:
            continue

        if atlas_lower == target:
            return idx

    # partial match
    for idx, atlas_name in enumerate(atlas_labels):
        atlas_name = str(atlas_name).strip()
        atlas_lower = atlas_name.lower()

        if idx == 0:
            continue
        if not atlas_name or atlas_lower in {"background", "unknown", "nan"}:
            continue

        if target in atlas_lower or atlas_lower in target:
            return idx

    return None


def _build_top_region_mask(top_regions, ref_img=None):
    if not top_regions:
        return None

    atlas = fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")

    atlas_maps = atlas.maps
    if isinstance(atlas_maps, nib.spatialimages.SpatialImage):
        atlas_img = atlas_maps
    else:
        atlas_img = nib.load(str(atlas_maps))

    atlas_data = atlas_img.get_fdata()
    atlas_labels = atlas.labels

    selected_values = []
    for item in top_regions[:3]:
        region_name = item.get("region") if isinstance(item, dict) else str(item)
        value = _match_region_to_atlas_value(region_name, atlas_labels)
        if value is not None:
            selected_values.append(value)

    if not selected_values:
        return None

    mask_data = np.isin(atlas_data, selected_values).astype(np.int16)
    if np.max(mask_data) == 0:
        return None

    mask_img = new_img_like(atlas_img, mask_data)

    if ref_img is not None:
        mask_img = resample_to_img(
            mask_img,
            ref_img,
            interpolation="nearest",
            force_resample=True,
            copy_header=True,
        )

    return mask_img


def _generate_scan_preview_images(saved_file_path: Path, unique_prefix: str, top_regions):
    original_png = PREVIEW_DIR / f"{unique_prefix}_original.png"
    overlay_png = PREVIEW_DIR / f"{unique_prefix}_overlay.png"

    mean_scan = mean_img(str(saved_file_path))

    plot_img(
        mean_scan,
        display_mode="ortho",
        draw_cross=False,
        colorbar=False,
        annotate=True,
        cmap="gray",
        output_file=str(original_png),
    )

    overlay_data_url = None
    mask_img = _build_top_region_mask(top_regions, ref_img=mean_scan)

    if mask_img is not None:
        plot_roi(
            mask_img,
            bg_img=mean_scan,
            display_mode="ortho",
            draw_cross=False,
            annotate=True,
            output_file=str(overlay_png),
        )
        overlay_data_url = _file_to_data_url(overlay_png)

    return {
        "scan_preview_original": _file_to_data_url(original_png),
        "scan_preview_overlay": overlay_data_url,
    }


@router.post("/predict")
def create_assessment(
    patient_id: int = Form(...),
    full_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    iq: float = Form(None),
    handedness: str = Form("Right"),
    site: str = Form("Unknown"),
    medication: str = Form(None),
    subtype: str = Form(None),
    mri_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        patient = db.query(Patient).filter(
            Patient.id == patient_id,
            Patient.doctor_id == current_user.id
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        effective_age = int(patient.age if patient.age is not None else age)
        effective_gender = patient.gender if patient.gender else gender
        effective_iq = patient.iq if patient.iq is not None else iq
        patient_name = patient.full_name if patient.full_name else full_name

        if effective_age < MIN_AGE or effective_age > MAX_AGE:
            raise HTTPException(
                status_code=400,
                detail=f"This project currently supports pediatric ADHD assessment only (age {MIN_AGE}-{MAX_AGE})."
            )

        if not mri_file:
            raise HTTPException(status_code=400, detail="fMRI file is required")

        filename = mri_file.filename or ""
        if not filename.endswith((".nii", ".nii.gz")):
            raise HTTPException(
                status_code=400,
                detail="Only .nii or .nii.gz files are allowed"
            )

        file_bytes = mri_file.file.read()
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max allowed size is {MAX_FILE_SIZE_MB} MB"
            )

        unique_name = f"{uuid.uuid4()}_{filename}"
        saved_file_path = UPLOAD_DIR / unique_name

        with open(saved_file_path, "wb") as buffer:
            buffer.write(file_bytes)

        try:
            img = nib.load(str(saved_file_path))
            if len(img.shape) != 4:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file must be a valid 4D resting-state fMRI NIfTI image"
                )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted NIfTI file"
            )

        fmri_features, region_labels, connection_mapping = extract_fmri_connectivity_features(
            str(saved_file_path)
        )

        sex_value = _normalize_sex(effective_gender)
        hand_value = _normalize_handedness(handedness)

        row = {
            "age": float(effective_age),
            "sex": sex_value,
            "handedness": hand_value,
            "site": str(site).strip() if site else "Unknown",
        }

        if effective_iq is not None and str(effective_iq).strip() != "":
            try:
                row["iq"] = float(effective_iq)
            except Exception:
                pass

        if isinstance(fmri_features, pd.DataFrame):
            if fmri_features.empty:
                raise HTTPException(status_code=400, detail="No fMRI features extracted")
            feature_dict = fmri_features.iloc[0].to_dict()

        elif isinstance(fmri_features, pd.Series):
            feature_dict = fmri_features.to_dict()

        elif isinstance(fmri_features, dict):
            feature_dict = fmri_features

        else:
            arr = np.asarray(fmri_features, dtype=float).ravel()
            feature_dict = {f"conn_{i}": float(v) for i, v in enumerate(arr)}

        clean_feature_dict = {}
        for k, v in feature_dict.items():
            key = str(k)
            if not key.startswith("conn_"):
                key = f"conn_{key}"
            clean_feature_dict[key] = float(v)

        row.update(clean_feature_dict)

        X = pd.DataFrame([row])

        result = predict_adhd_ensemble(X)

        explain_out = explain_multimodal_prediction(
            X,
            region_labels=region_labels,
            connection_mapping=connection_mapping,
            predicted_label=result["predicted_label"],
            confidence=result["confidence"]
        )

        top_regions = explain_out.get("top_regions", [])
        top_connections = explain_out.get("top_connections", [])
        clinical_summary = explain_out.get(
            "clinical_summary",
            "AI-generated regional explanation is available for this scan."
        )

        preview_data = _generate_scan_preview_images(
            saved_file_path=saved_file_path,
            unique_prefix=unique_name.replace(".nii.gz", "").replace(".nii", ""),
            top_regions=top_regions,
        )

        primary_region = _extract_primary_region_name(top_regions)
        explanation_text = f"{clinical_summary}\nUploaded MRI file: {filename}"

        new_assessment = Assessment(
            patient_id=patient.id,
            adhd_score=result["adhd_score"],
            predicted_label=result["predicted_label"],
            confidence=result["confidence"],
            important_region=primary_region,
            explanation=explanation_text,
        )

        db.add(new_assessment)
        db.commit()
        db.refresh(new_assessment)

        return {
            "id": new_assessment.id,
            "patient_id": new_assessment.patient_id,
            "patient_name": patient_name,
            "adhd_score": result["adhd_score"],
            "predicted_label": result["predicted_label"],
            "confidence": result["confidence"],
            "control_probability": result["control_probability"],
            "bilstm_probability": result["bilstm_probability"],
            "transformer_probability": result["transformer_probability"],
            "important_region": primary_region,
            "explanation": clinical_summary,
            "created_at": new_assessment.created_at,
            "uploaded_file": filename,
            "adhd_probability": result["adhd_score"],
            "gender": effective_gender,
            "age": effective_age,
            "iq": effective_iq,
            "handedness": handedness,
            "site": site,
            "medication": medication,
            "subtype": subtype,
            "top_regions": top_regions,
            "top_connections": top_connections,
            "clinical_summary": clinical_summary,
            "scan_preview_original": preview_data.get("scan_preview_original"),
            "scan_preview_overlay": preview_data.get("scan_preview_overlay"),
        }

    except HTTPException:
        raise
    except Exception as e:
        print("\n===== MULTIMODAL PREDICTION ERROR =====")
        traceback.print_exc()
        print("=======================================\n")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/")
def get_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patients = db.query(Patient).filter(Patient.doctor_id == current_user.id).all()
    patient_ids = [p.id for p in patients]

    if not patient_ids:
        return []

    records = db.query(Assessment).filter(
        Assessment.patient_id.in_(patient_ids)
    ).order_by(Assessment.id.desc()).all()

    patient_map = {p.id: p for p in patients}

    output = []
    for item in records:
        patient = patient_map.get(item.patient_id)

        uploaded_file = None
        explanation_text = item.explanation or ""

        if "Uploaded MRI file:" in explanation_text:
            uploaded_file = explanation_text.split("Uploaded MRI file:")[-1].strip()
            explanation_text = explanation_text.split("Uploaded MRI file:")[0].strip()

        output.append({
            "id": item.id,
            "patient_id": item.patient_id,
            "patient_name": patient.full_name if patient else "Unknown",
            "adhd_score": item.adhd_score,
            "predicted_label": item.predicted_label,
            "confidence": item.confidence,
            "important_region": item.important_region,
            "explanation": explanation_text,
            "uploaded_file": uploaded_file,
            "created_at": item.created_at,
        })

    return output