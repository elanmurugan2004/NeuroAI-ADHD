from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patient, User
from app.schemas import PatientCreate, PatientOut
from app.auth import get_current_user

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientOut)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_patient = Patient(
        doctor_id=current_user.id,
        full_name=patient.full_name,
        age=patient.age,
        gender=patient.gender,
        iq=patient.iq,
        diagnosis_note=patient.diagnosis_note
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


@router.get("/", response_model=list[PatientOut])
def get_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Patient).filter(Patient.doctor_id == current_user.id).all()