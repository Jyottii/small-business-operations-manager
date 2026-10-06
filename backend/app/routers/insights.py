from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.schemas.base import ResponseModel
from app.schemas.insights import InsightsData
from app.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["Insights"])

ALLOWED_INSIGHTS_ROLES = (UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)

@router.get("", response_model=ResponseModel[InsightsData])
def get_business_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ALLOWED_INSIGHTS_ROLES)),
    period: str = Query("last_30_days", description="today, last_7_days, last_30_days, current_month, previous_month, all_time, custom"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Generate deterministic, explainable Smart Business Insights.
    Restricted to Owner, Admin, and Manager roles.
    Strictly isolated to current_user.business_id.
    """
    insights_data = InsightsService.generate_insights(
        db=db,
        business_id=current_user.business_id,
        period=period,
        start_date=start_date,
        end_date=end_date
    )
    return {"data": insights_data}
