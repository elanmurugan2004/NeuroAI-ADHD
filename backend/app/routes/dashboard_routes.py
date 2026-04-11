from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patient, Assessment, User
from app.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_patients = db.query(Patient).filter(Patient.doctor_id == current_user.id).count()

    patient_ids = [p.id for p in db.query(Patient).filter(Patient.doctor_id == current_user.id).all()]
    total_assessments = db.query(Assessment).filter(Assessment.patient_id.in_(patient_ids)).count() if patient_ids else 0

    latest_assessment = (
        db.query(Assessment)
        .filter(Assessment.patient_id.in_(patient_ids))
        .order_by(Assessment.id.desc())
        .first()
        if patient_ids else None
    )

    latest_prediction = latest_assessment.predicted_label if latest_assessment else "N/A"
    latest_confidence = f"{latest_assessment.confidence}%" if latest_assessment else "N/A"
    review_status = "Pending" if latest_assessment else "No Data"

    return {
        "total_patients": total_patients,
        "total_assessments": total_assessments,
        "latest_prediction": latest_prediction,
        "latest_confidence": latest_confidence,
        "review_status": review_status
    }