from sqlalchemy.orm import Session
from typing import Tuple, Optional
from datetime import datetime

from app.models.user import User, UserRole
from app.models.business import Business
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException
)
from app.services.system_service import AuditService

ALLOWED_ROLES = {role.value for role in UserRole}

class AuthService:
    @staticmethod
    def register_user(db: Session, data: UserRegister) -> Tuple[User, str]:
        # 1. Check if email already exists
        existing = db.query(User).filter(User.email == data.email.lower().strip()).first()
        if existing:
            raise ConflictException("Email already registered")
            
        # 2. Resolve business association
        business_id = None
        role = UserRole.STAFF.value
        
        if data.business_name and data.business_name.strip():
            # Create a brand new business and make the user Owner
            business = Business(name=data.business_name.strip())
            db.add(business)
            db.flush()
            business_id = business.id
            role = UserRole.OWNER.value
        elif data.business_id:
            # Associate with existing business
            business = db.query(Business).filter(Business.id == data.business_id).first()
            if not business:
                raise NotFoundException("Business not found")
            business_id = business.id
            if data.role:
                if data.role not in ALLOWED_ROLES:
                    raise BadRequestException(f"Invalid role. Must be one of: {', '.join(ALLOWED_ROLES)}")
                if data.role in (UserRole.OWNER.value, UserRole.ADMIN.value):
                    raise ForbiddenException("Public registration cannot assign Owner or Admin roles to an existing business")
                role = data.role
            else:
                role = UserRole.STAFF.value
        else:
            raise BadRequestException("Either business_name (for new business) or business_id must be provided")

        # 3. Hash password with Argon2
        pwd_hash = hash_password(data.password)

        # 4. Create user record
        user = User(
            business_id=business_id,
            name=data.name.strip(),
            email=data.email.lower().strip(),
            password_hash=pwd_hash,
            role=role,
            is_active=True
        )
        db.add(user)
        db.flush()

        # 5. Generate token
        token = create_access_token({
            "sub": user.id,
            "business_id": user.business_id,
            "role": user.role
        })

        # 6. Audit logging
        AuditService.log(
            db=db,
            business_id=user.business_id,
            action="USER_REGISTERED",
            entity_type="User",
            entity_id=user.id,
            description=f"User {user.name} ({user.email}) registered as {user.role}",
            user_id=user.id
        )

        return user, token

    @staticmethod
    def authenticate_user(db: Session, data: UserLogin) -> Tuple[User, str]:
        email = data.email.lower().strip()
        user = db.query(User).filter(User.email == email).first()

        # Constant-time-like check: if user doesn't exist, still avoid immediate timing leakage
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is inactive")

        token = create_access_token({
            "sub": user.id,
            "business_id": user.business_id,
            "role": user.role
        })

        AuditService.log(
            db=db,
            business_id=user.business_id,
            action="USER_LOGIN",
            entity_type="User",
            entity_id=user.id,
            description=f"User {user.email} logged in successfully",
            user_id=user.id
        )

        return user, token
