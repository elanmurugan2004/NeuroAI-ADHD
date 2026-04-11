from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "doctor"

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\];']", value):
            raise ValueError("Password must contain at least one special character")
        return value


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