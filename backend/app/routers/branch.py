from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.branch import Branch
from app.schemas.branch import BranchResponse, BranchCreate, BranchUpdate
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/branches", tags=["Branches"])

@router.get("", response_model=PaginatedResponseModel[BranchResponse])
def get_branches(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(None)
):
    query = db.query(Branch).filter(Branch.business_id == current_user.business_id)
    if is_active is not None:
        query = query.filter(Branch.is_active == is_active)
        
    total = query.count()
    items = query.order_by(Branch.name.asc()).offset((page - 1) * page_size).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return {
        "data": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    }

@router.get("/{item_id}", response_model=ResponseModel[BranchResponse])
def get_branch(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    branch = db.query(Branch).filter(
        Branch.id == item_id,
        Branch.business_id == current_user.business_id
    ).first()
    if not branch:
        raise NotFoundException("Branch not found")
    return {"data": branch}

@router.post("", response_model=ResponseModel[BranchResponse], status_code=status.HTTP_201_CREATED)
def create_branch(
    data: BranchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    # Check uniqueness of branch code within business
    existing = db.query(Branch).filter(
        Branch.business_id == current_user.business_id,
        Branch.code == data.code
    ).first()
    if existing:
        raise BadRequestException(f"Branch with code '{data.code}' already exists")
        
    branch_dict = data.model_dump()
    branch_dict["business_id"] = current_user.business_id
    branch = Branch(**branch_dict)
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return {"data": branch}

@router.put("/{item_id}", response_model=ResponseModel[BranchResponse])
def update_branch(
    item_id: str,
    data: BranchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    branch = db.query(Branch).filter(
        Branch.id == item_id,
        Branch.business_id == current_user.business_id
    ).first()
    if not branch:
        raise NotFoundException("Branch not found")
        
    update_data = data.model_dump(exclude_unset=True)
    if "code" in update_data and update_data["code"] != branch.code:
        existing = db.query(Branch).filter(
            Branch.business_id == current_user.business_id,
            Branch.code == update_data["code"]
        ).first()
        if existing:
            raise BadRequestException(f"Branch with code '{update_data['code']}' already exists")

    for key, value in update_data.items():
        setattr(branch, key, value)
        
    db.commit()
    db.refresh(branch)
    return {"data": branch}

@router.delete("/{item_id}")
def delete_branch(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN))
):
    branch = db.query(Branch).filter(
        Branch.id == item_id,
        Branch.business_id == current_user.business_id
    ).first()
    if not branch:
        raise NotFoundException("Branch not found")
        
    db.delete(branch)
    db.commit()
    return {"data": {"message": "Branch deleted successfully", "id": item_id}}
