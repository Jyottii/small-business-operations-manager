from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(tags=["System"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        return {
            "status": "degraded",
            "app": "healthy",
            "database": f"error: {str(e)}"
        }
        
    return {
        "status": "ok",
        "app": "healthy",
        "database": db_status
    }
