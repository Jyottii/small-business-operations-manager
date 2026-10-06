from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional
from datetime import datetime

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.payment import Payment
from app.schemas.base import ResponseModel
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    SalesAnalyticsResponse,
    ProductsAnalyticsResponse,
    CustomersAnalyticsResponse,
    InventoryAnalyticsResponse,
    PurchasesAnalyticsResponse,
    FinancialKPIs
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

ALLOWED_ANALYTICS_ROLES = (UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)

@router.get("/summary", response_model=ResponseModel[AnalyticsSummaryResponse])
def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ALLOWED_ANALYTICS_ROLES)),
    period: str = Query("last_30_days", description="today, last_7_days, last_30_days, current_month, previous_month, all_time, custom"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    summary = AnalyticsService.get_summary(
        db=db,
        business_id=current_user.business_id,
        period=period,
        start_date=start_date,
        end_date=end_date
    )
    return {"data": summary}

@router.get("/sales", response_model=ResponseModel[SalesAnalyticsResponse])
def get_sales_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ALLOWED_ANALYTICS_ROLES)),
    period: str = Query("last_30_days"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    start_dt, end_dt, days = AnalyticsService.get_date_bounds(period, start_date, end_date)
    kpis = AnalyticsService.get_sales_kpis(db, current_user.business_id, start_dt, end_dt)
    timeline = AnalyticsService.get_time_series_timeline(db, current_user.business_id, start_dt, end_dt)
    
    # Top products by sales
    prod_data = AnalyticsService.get_product_analytics(db, current_user.business_id, start_dt, end_dt, days, limit=5)
    
    # Payment method breakdown
    pay_filters = [
        Payment.business_id == current_user.business_id,
        or_(Payment.customer_id.isnot(None), Payment.order_id.isnot(None))
    ]
    pay_date_expr = func.coalesce(Payment.payment_date, Payment.created_at)
    if start_dt:
        pay_filters.append(pay_date_expr >= start_dt)
    if end_dt:
        pay_filters.append(pay_date_expr <= end_dt)

    method_rows = db.query(
        func.coalesce(Payment.payment_method, "Unspecified").label("method"),
        func.coalesce(func.sum(Payment.amount), 0).label("total"),
        func.count(Payment.id).label("count")
    ).filter(*pay_filters).group_by(Payment.payment_method).all()

    payment_methods = [
        {
            "method": m.method,
            "total": round(float(m.total or 0.0), 2),
            "count": int(m.count or 0)
        }
        for m in method_rows
    ]

    return {
        "data": SalesAnalyticsResponse(
            period=period,
            start_date=start_dt.strftime("%Y-%m-%d") if start_dt else None,
            end_date=end_dt.strftime("%Y-%m-%d") if end_dt else None,
            kpis=kpis,
            timeline=timeline,
            payment_methods=payment_methods,
            top_products=prod_data.top_by_revenue
        )
    }

@router.get("/products", response_model=ResponseModel[ProductsAnalyticsResponse])
def get_product_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ALLOWED_ANALYTICS_ROLES)),
    period: str = Query("last_30_days"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    start_dt, end_dt, days = AnalyticsService.get_date_bounds(period, start_date, end_date)
    prod_resp = AnalyticsService.get_product_analytics(
        db=db,
        business_id=current_user.business_id,
        start_dt=start_dt,
        end_dt=end_dt,
        days_count=days,
        limit=limit
    )
    return {"data": prod_resp}

@router.get("/customers", response_model=ResponseModel[CustomersAnalyticsResponse])
def get_customer_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ALLOWED_ANALYTICS_ROLES)),
    period: str = Query("last_30_days"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    start_dt, end_dt, _ = AnalyticsService.get_date_bounds(period, start_date, end_date)
    cust_resp = AnalyticsService.get_customer_analytics(
        db=db,
        business_id=current_user.business_id,
        start_dt=start_dt,
        end_dt=end_dt,
        limit=limit
    )
    return {"data": cust_resp}

@router.get("/inventory", response_model=ResponseModel[InventoryAnalyticsResponse])
def get_inventory_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ALLOWED_ANALYTICS_ROLES)),
    days: int = Query(30, ge=1, le=365)
):
    inv_resp = AnalyticsService.get_inventory_analytics(
        db=db,
        business_id=current_user.business_id,
        days_count=days
    )
    return {"data": inv_resp}

@router.get("/purchases", response_model=ResponseModel[PurchasesAnalyticsResponse])
def get_purchasing_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ALLOWED_ANALYTICS_ROLES)),
    period: str = Query("last_30_days"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    start_dt, end_dt, _ = AnalyticsService.get_date_bounds(period, start_date, end_date)
    purch_resp = AnalyticsService.get_purchasing_analytics(
        db=db,
        business_id=current_user.business_id,
        start_dt=start_dt,
        end_dt=end_dt
    )
    return {"data": purch_resp}

@router.get("/financial", response_model=ResponseModel[FinancialKPIs])
def get_financial_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ALLOWED_ANALYTICS_ROLES)),
    period: str = Query("last_30_days"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    start_dt, end_dt, _ = AnalyticsService.get_date_bounds(period, start_date, end_date)
    financial = AnalyticsService.get_financial_kpis(
        db=db,
        business_id=current_user.business_id,
        start_dt=start_dt,
        end_dt=end_dt
    )
    return {"data": financial}
