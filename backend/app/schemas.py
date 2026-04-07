from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ---------------- USER ----------------
class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "doctor"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- PATIENT ----------------
class PatientCreate(BaseModel):
    full_name: str
    age: int
    gender: str
    iq: Optional[float] = None
    diagnosis_note: Optional[str] = None


class PatientOut(BaseModel):
    id: int
    doctor_id: Optional[int]
    full_name: str
    age: int
    gender: str
    iq: Optional[float]
    diagnosis_note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- ASSESSMENT ----------------
class AssessmentCreate(BaseModel):
    patient_id: int
    age: int
    iq: Optional[float] = None
    attention_score: float
    hyperactivity_score: float
    impulsivity_score: float


class AssessmentOut(BaseModel):
    id: int
    patient_id: int
    adhd_score: float
    predicted_label: str
    confidence: float
    important_region: Optional[str]
    explanation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True