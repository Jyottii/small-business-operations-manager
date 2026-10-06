from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles, get_current_actor
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.security import hash_password
from app.core.exceptions import (
    NotFoundException, 
    ForbiddenException, 
    BadRequestException, 
    ConflictException
)
from app.services.system_service import AuditService

router = APIRouter(prefix="/users", tags=["Users"])

ALLOWED_ROLES = {role.value for role in UserRole}

@router.get("", response_model=PaginatedResponseModel[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    query = db.query(User).filter(User.business_id == current_user.business_id)
    if search:
        query = query.filter(User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
        }
    }

@router.get("/{user_id}", response_model=ResponseModel[UserResponse])
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    user = db.query(User).filter(
        User.id == user_id, 
        User.business_id == current_user.business_id
    ).first()
    if not user:
        raise NotFoundException("User not found")
    return {"data": user}

@router.post("", response_model=ResponseModel[UserResponse], status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    actor: str = Depends(get_current_actor)
):
    # Role validation
    if data.role not in ALLOWED_ROLES:
        raise BadRequestException(f"Invalid role. Must be one of: {', '.join(ALLOWED_ROLES)}")

    # Privilege escalation prevention: Admins cannot create Owner or Admin accounts
    if current_user.role == UserRole.ADMIN.value and data.role in (UserRole.OWNER.value, UserRole.ADMIN.value):
        raise ForbiddenException("Admins cannot create Owner or Admin accounts")

    # Email uniqueness check
    existing = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if existing:
        raise ConflictException("Email already registered")

    pwd_hash = hash_password(data.password)
    user = User(
        business_id=current_user.business_id,
        name=data.name.strip(),
        email=data.email.lower().strip(),
        password_hash=pwd_hash,
        role=data.role,
        employee_id=data.employee_id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    AuditService.log(
        db=db,
        business_id=current_user.business_id,
        action="USER_CREATED",
        entity_type="User",
        entity_id=user.id,
        description=f"User {user.email} created with role {user.role}",
        user_id=actor
    )

    return {"data": user}

@router.patch("/{user_id}", response_model=ResponseModel[UserResponse])
def update_user(
    user_id: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    actor: str = Depends(get_current_actor)
):
    target_user = db.query(User).filter(
        User.id == user_id, 
        User.business_id == current_user.business_id
    ).first()
    if not target_user:
        raise NotFoundException("User not found")

    # 1. Self-role modification prevention
    if target_user.id == current_user.id and data.role is not None and data.role != current_user.role:
        raise ForbiddenException("Users cannot modify their own role")

    # 2. Self-deactivation prevention
    if target_user.id == current_user.id and data.is_active is False:
        raise BadRequestException("Users cannot deactivate their own account")

    # 3. Privilege escalation prevention for Admins
    if current_user.role == UserRole.ADMIN.value:
        # Admins cannot edit Owner or other Admin accounts
        if target_user.role in (UserRole.OWNER.value, UserRole.ADMIN.value):
            raise ForbiddenException("Admins cannot modify Owner or Admin accounts")
        # Admins cannot promote anyone to Owner or Admin
        if data.role and data.role in (UserRole.OWNER.value, UserRole.ADMIN.value):
            raise ForbiddenException("Admins cannot promote users to Owner or Admin")

    # 4. Role validation
    if data.role:
        if data.role not in ALLOWED_ROLES:
            raise BadRequestException(f"Invalid role. Must be one of: {', '.join(ALLOWED_ROLES)}")
        target_user.role = data.role

    if data.name:
        target_user.name = data.name.strip()
    if data.is_active is not None:
        target_user.is_active = data.is_active
    if data.employee_id is not None:
        target_user.employee_id = data.employee_id

    db.commit()
    db.refresh(target_user)

    AuditService.log(
        db=db,
        business_id=current_user.business_id,
        action="USER_UPDATED",
        entity_type="User",
        entity_id=target_user.id,
        description=f"User {target_user.email} updated by {actor}",
        user_id=actor
    )

    return {"data": target_user}
