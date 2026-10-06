from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.expense import Expense
from app.schemas.expense import ExpenseResponse, ExpenseCreate, ExpenseUpdate
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.get("", response_model=PaginatedResponseModel[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(Expense).filter(Expense.business_id == current_user.business_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": items,
        "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}
    }

@router.get("/{item_id}", response_model=ResponseModel[ExpenseResponse])
def get_expense(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item = db.query(Expense).filter(Expense.id == item_id, Expense.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Expense not found")
    return {"data": item}

@router.post("", response_model=ResponseModel[ExpenseResponse])
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item_data = data.model_dump()
    item_data["business_id"] = current_user.business_id
    item = Expense(**item_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"data": item}

@router.patch("/{item_id}", response_model=ResponseModel[ExpenseResponse])
def update_expense(
    item_id: str,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item = db.query(Expense).filter(Expense.id == item_id, Expense.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Expense not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return {"data": item}
