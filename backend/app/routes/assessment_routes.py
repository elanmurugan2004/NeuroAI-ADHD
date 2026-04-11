from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
import traceback
import nibabel as nib

from app.database import get_db
from app.models import Patient, Assessment, User
from app.auth import get_current_user
from ml.model_loader import load_multimodal_model
from ml.preprocess import extract_fmri_connectivity_features, build_multimodal_input
from ml.predictor import predict_adhd_multimodal
from ml.explainability import explain_multimodal_prediction

router = APIRouter(prefix="/assessments", tags=["Assessments"])

ROOT_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE_MB = 300


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

        if not mri_file:
            raise HTTPException(status_code=400, detail="MRI file is required")

        filename = mri_file.filename or ""
        if not filename.endswith((".nii", ".nii.gz")):
            raise HTTPException(status_code=400, detail="Only .nii or .nii.gz files are allowed")

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

        # Validate file can be opened as NIfTI
        try:
            img = nib.load(str(saved_file_path))
            if len(img.shape) not in [3, 4]:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file must be a valid 3D or 4D NIfTI image"
                )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid or corrupted NIfTI file")

        pipeline, meta = load_multimodal_model()

        payload = {
            "full_name": full_name,
            "age": age,
            "gender": gender,
            "iq": iq,
            "handedness": handedness,
            "site": site,
            "medication": medication,
            "subtype": subtype,
        }

        fmri_features, region_labels, connection_mapping = extract_fmri_connectivity_features(
            str(saved_file_path)
        )
        X = build_multimodal_input(payload, meta, fmri_features)

        result = predict_adhd_multimodal(X)
        explain_out = explain_multimodal_prediction(
            X,
            region_labels=region_labels,
            connection_mapping=connection_mapping,
            predicted_label=result["predicted_label"],
            confidence=result["confidence"]
        )

        top_regions = explain_out["top_regions"]
        clinical_summary = explain_out["clinical_summary"]
        recommendation = explain_out["recommendation"]

        new_assessment = Assessment(
            patient_id=patient_id,
            adhd_score=result["adhd_score"],
            predicted_label=result["predicted_label"],
            confidence=result["confidence"],
            important_region="Multimodal MRI + Phenotypic Model",
            explanation=clinical_summary,
        )

        db.add(new_assessment)
        db.commit()
        db.refresh(new_assessment)

        return {
            "id": new_assessment.id,
            "patient_id": new_assessment.patient_id,
            "patient_name": full_name,
            "adhd_score": new_assessment.adhd_score,
            "predicted_label": new_assessment.predicted_label,
            "confidence": new_assessment.confidence,
            "important_region": new_assessment.important_region,
            "explanation": new_assessment.explanation,
            "created_at": new_assessment.created_at,
            "uploaded_file": filename,
            "adhd_probability": result["adhd_score"],
            "control_probability": result["control_probability"],
            "gender": gender,
            "age": age,
            "iq": iq,
            "handedness": handedness,
            "site": site,
            "top_regions": top_regions,
            "clinical_summary": clinical_summary,
            "recommendation": recommendation,
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
        if item.explanation and "Uploaded MRI file:" in item.explanation:
            uploaded_file = item.explanation.split("Uploaded MRI file:")[-1].strip()

        output.append({
            "id": item.id,
            "patient_id": item.patient_id,
            "patient_name": patient.full_name if patient else "Unknown",
            "adhd_score": item.adhd_score,
            "predicted_label": item.predicted_label,
            "confidence": item.confidence,
            "important_region": item.important_region,
            "explanation": item.explanation,
            "uploaded_file": uploaded_file,
            "created_at": item.created_at,
        })

    return output