from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes.auth_routes import router as auth_router
from app.routes.patient_routes import router as patient_router
from app.routes.assessment_routes import router as assessment_router
from app.routes.report_routes import router as report_router
from app.routes.dashboard_routes import router as dashboard_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NEUROAI-ADHD Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(assessment_router)
app.include_router(report_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {"message": "NEUROAI-ADHD backend is running successfully"}