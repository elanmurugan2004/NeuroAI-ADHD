from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
import traceback

from app.database import get_db
from app.models import Patient, Assessment
from app.schemas import AssessmentOut
from ml.model_loader import load_multimodal_model
from ml.preprocess import extract_fmri_connectivity_features, build_multimodal_input
from ml.predictor import predict_adhd_multimodal
from ml.explainability import explain_multimodal_prediction

router = APIRouter(prefix="/assessments", tags=["Assessments"])

ROOT_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


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
):
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        if not mri_file.filename.endswith((".nii", ".nii.gz")):
            raise HTTPException(status_code=400, detail="Only .nii or .nii.gz files are allowed")

        unique_name = f"{uuid.uuid4()}_{mri_file.filename}"
        saved_file_path = UPLOAD_DIR / unique_name

        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(mri_file.file, buffer)

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

        fmri_features = extract_fmri_connectivity_features(str(saved_file_path))
        X = build_multimodal_input(payload, meta, fmri_features)

        result = predict_adhd_multimodal(X)
        top_features = explain_multimodal_prediction(X)

        explanation = "Top multimodal features: " + ", ".join(
            [f"{x['feature']} ({x['impact']})" for x in top_features[:5]]
        )

        new_assessment = Assessment(
            patient_id=patient_id,
            adhd_score=result["adhd_score"],
            predicted_label=result["predicted_label"],
            confidence=result["confidence"],
            important_region="Multimodal MRI + Phenotypic Model",
            explanation=explanation,
        )

        db.add(new_assessment)
        db.commit()
        db.refresh(new_assessment)

        return {
            "id": new_assessment.id,
            "patient_id": new_assessment.patient_id,
            "adhd_score": new_assessment.adhd_score,
            "predicted_label": new_assessment.predicted_label,
            "confidence": new_assessment.confidence,
            "important_region": new_assessment.important_region,
            "explanation": new_assessment.explanation,
            "created_at": new_assessment.created_at,
            "top_features": top_features,
            "uploaded_file": mri_file.filename,
            "adhd_probability": result["adhd_score"],
            "control_probability": result["control_probability"],
        }

    except HTTPException:
        raise
    except Exception as e:
        print("\n===== MULTIMODAL PREDICTION ERROR =====")
        traceback.print_exc()
        print("=======================================\n")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/", response_model=list[AssessmentOut])
def get_assessments(db: Session = Depends(get_db)):
    return db.query(Assessment).all()