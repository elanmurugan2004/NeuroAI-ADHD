from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patient, Assessment

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_patients = db.query(Patient).count()
    total_assessments = db.query(Assessment).count()

    latest_assessment = db.query(Assessment).order_by(Assessment.id.desc()).first()

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