from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/")
def get_reports():
    return {"message": "Report module is ready. PDF generation can be added next."}