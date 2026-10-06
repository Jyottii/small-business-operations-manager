from fastapi import Request, Header, Depends
from sqlalchemy.orm import Session
from typing import Optional, Union, Sequence

from app.dependencies.database import get_db
from app.models.user import User, UserRole
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Strict dependency: requires an authenticated active user.
    Raises 401 Unauthorized if missing, invalid, expired, or inactive.
    """
    token = None
    
    # 1. Check Authorization header: Bearer <token>
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    
    # 2. Check HttpOnly cookie
    if not token and "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    if not token:
        raise UnauthorizedException("Authentication required")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("Account is inactive")

    return user

def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Extracts and validates current user if present.
    Returns None if unauthenticated, token invalid, or user inactive.
    """
    try:
        return get_current_user(request, db)
    except UnauthorizedException:
        return None

def require_roles(*allowed_roles: Union[str, UserRole]):
    """
    Centralized RBAC authorization dependency factory.
    1. Authenticates user (401 if unauthenticated, invalid token, or inactive).
    2. Authorizes user (403 if user role is not in allowed_roles).
    3. Returns authenticated User object.
    """
    role_names = {r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles}

    def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.is_active:
            raise UnauthorizedException("Account is inactive")
        if current_user.role not in role_names:
            raise ForbiddenException("Access forbidden: insufficient permissions")
        return current_user

    return role_checker

def get_current_business_id(
    request: Request,
    db: Session = Depends(get_db),
    x_business_id: Optional[str] = Header(None, alias="X-Business-ID")
) -> str:
    """
    Resolves authoritative business_id:
    - If user is authenticated, user's business_id is ALWAYS used (client header is ignored).
    - If user is not authenticated, falls back to X-Business-ID for backward compatibility.
    """
    user = get_optional_current_user(request, db)
    if user:
        return user.business_id

    if x_business_id and x_business_id.strip():
        return x_business_id.strip()

    raise UnauthorizedException("Authentication required")

def get_current_actor(
    request: Request,
    db: Session = Depends(get_db)
) -> str:
    """
    Returns identifier of acting user for audit logs, or 'SYSTEM' if unauthenticated.
    """
    user = get_optional_current_user(request, db)
    if user:
        return user.name or user.id
    return "SYSTEM"
