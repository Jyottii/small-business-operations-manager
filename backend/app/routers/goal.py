from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.goal import BusinessGoal
from app.models.order import Order
from app.models.customer import Customer
from app.models.expense import Expense
from app.schemas.goal import (
    BusinessGoalResponse,
    BusinessGoalCreate,
    BusinessGoalUpdate
)
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/goals", tags=["Goals"])

def _calculate_goal_progress(goal: BusinessGoal, db: Session) -> dict:
    biz_id = goal.business_id
    current_value = 0.0

    if goal.metric == "TOTAL_REVENUE":
        q = db.query(func.coalesce(func.sum(Order.total), 0.0)).filter(
            Order.business_id == biz_id,
            Order.status != "CANCELLED"
        )
        if goal.start_date:
            q = q.filter(Order.created_at >= goal.start_date)
        if goal.end_date:
            q = q.filter(Order.created_at <= goal.end_date)
        current_value = float(q.scalar() or 0.0)

    elif goal.metric == "ORDER_COUNT":
        q = db.query(func.count(Order.id)).filter(
            Order.business_id == biz_id,
            Order.status != "CANCELLED"
        )
        if goal.start_date:
            q = q.filter(Order.created_at >= goal.start_date)
        if goal.end_date:
            q = q.filter(Order.created_at <= goal.end_date)
        current_value = float(q.scalar() or 0.0)

    elif goal.metric == "CUSTOMER_COUNT":
        q = db.query(func.count(Customer.id)).filter(
            Customer.business_id == biz_id
        )
        if goal.start_date:
            q = q.filter(Customer.created_at >= goal.start_date)
        if goal.end_date:
            q = q.filter(Customer.created_at <= goal.end_date)
        current_value = float(q.scalar() or 0.0)

    elif goal.metric == "PROFIT":
        rev_q = db.query(func.coalesce(func.sum(Order.total), 0.0)).filter(
            Order.business_id == biz_id,
            Order.status != "CANCELLED"
        )
        exp_q = db.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
            Expense.business_id == biz_id
        )
        if goal.start_date:
            rev_q = rev_q.filter(Order.created_at >= goal.start_date)
            exp_q = exp_q.filter(Expense.created_at >= goal.start_date)
        if goal.end_date:
            rev_q = rev_q.filter(Order.created_at <= goal.end_date)
            exp_q = exp_q.filter(Expense.created_at <= goal.end_date)
        rev = float(rev_q.scalar() or 0.0)
        exp = float(exp_q.scalar() or 0.0)
        current_value = max(0.0, rev - exp)

    target = float(goal.target_value or 0.0)
    progress_pct = min(100.0, round((current_value / target) * 100, 1)) if target > 0 else 0.0
    
    if progress_pct >= 100.0:
        goal_status = "COMPLETED"
    elif progress_pct >= 70.0:
        goal_status = "ON_TRACK"
    else:
        goal_status = "AT_RISK"

    return {
        "id": goal.id,
        "business_id": goal.business_id,
        "title": goal.title,
        "metric": goal.metric,
        "target_value": target,
        "period": goal.period,
        "start_date": goal.start_date,
        "end_date": goal.end_date,
        "is_active": goal.is_active,
        "current_value": round(current_value, 2),
        "progress_percent": progress_pct,
        "status": goal_status,
        "created_at": goal.created_at,
        "updated_at": goal.updated_at
    }

@router.get("", response_model=PaginatedResponseModel[BusinessGoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(BusinessGoal).filter(BusinessGoal.business_id == current_user.business_id)
    if is_active is not None:
        query = query.filter(BusinessGoal.is_active == is_active)

    total = query.count()
    goals = query.order_by(BusinessGoal.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    formatted = [_calculate_goal_progress(g, db) for g in goals]
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return {
        "data": formatted,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    }

@router.get("/{item_id}", response_model=ResponseModel[BusinessGoalResponse])
def get_goal(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    goal = db.query(BusinessGoal).filter(
        BusinessGoal.id == item_id,
        BusinessGoal.business_id == current_user.business_id
    ).first()
    if not goal:
        raise NotFoundException("Goal not found")
    return {"data": _calculate_goal_progress(goal, db)}

@router.post("", response_model=ResponseModel[BusinessGoalResponse], status_code=status.HTTP_201_CREATED)
def create_goal(
    data: BusinessGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    valid_metrics = {"TOTAL_REVENUE", "ORDER_COUNT", "CUSTOMER_COUNT", "PROFIT"}
    if data.metric.upper() not in valid_metrics:
        raise BadRequestException(f"Invalid metric. Allowed metrics: {', '.join(sorted(valid_metrics))}")

    goal_dict = data.model_dump()
    goal_dict["metric"] = goal_dict["metric"].upper()
    goal_dict["period"] = goal_dict["period"].upper()
    goal_dict["business_id"] = current_user.business_id

    goal = BusinessGoal(**goal_dict)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return {"data": _calculate_goal_progress(goal, db)}

@router.put("/{item_id}", response_model=ResponseModel[BusinessGoalResponse])
def update_goal(
    item_id: str,
    data: BusinessGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    goal = db.query(BusinessGoal).filter(
        BusinessGoal.id == item_id,
        BusinessGoal.business_id == current_user.business_id
    ).first()
    if not goal:
        raise NotFoundException("Goal not found")

    update_dict = data.model_dump(exclude_unset=True)
    if "metric" in update_dict:
        m = update_dict["metric"].upper()
        if m not in {"TOTAL_REVENUE", "ORDER_COUNT", "CUSTOMER_COUNT", "PROFIT"}:
            raise BadRequestException("Invalid metric")
        update_dict["metric"] = m
    if "period" in update_dict:
        update_dict["period"] = update_dict["period"].upper()

    for key, value in update_dict.items():
        setattr(goal, key, value)

    db.commit()
    db.refresh(goal)
    return {"data": _calculate_goal_progress(goal, db)}

@router.delete("/{item_id}")
def delete_goal(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN))
):
    goal = db.query(BusinessGoal).filter(
        BusinessGoal.id == item_id,
        BusinessGoal.business_id == current_user.business_id
    ).first()
    if not goal:
        raise NotFoundException("Goal not found")

    db.delete(goal)
    db.commit()
    return {"data": {"message": "Goal deleted successfully", "id": item_id}}
