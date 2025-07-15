"""
Authentication dependencies for FastAPI endpoints.
Includes current user, role-based access, and security dependencies.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id, check_user_permissions
from app.models.user import User, UserRole
from app.core.redis_client import redis_client

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract user ID from token
        user_id = get_current_user_id(credentials.credentials)
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        
        return user
    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current verified user.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Current verified user
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please verify your email address"
        )
    
    return current_user


def require_role(required_role: UserRole):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function that checks user role
    """
    def check_role(current_user: User = Depends(get_current_verified_user)) -> User:
        if not check_user_permissions(current_user, required_role=required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    
    return check_role


# Role-specific dependencies
get_current_candidate = require_role(UserRole.CANDIDATE)
get_current_employer = require_role(UserRole.EMPLOYER)
get_current_admin = require_role(UserRole.ADMIN)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work with or without authentication.
    
    Args:
        credentials: JWT token from Authorization header (optional)
        db: Database session
        
    Returns:
        Optional[User]: Current user if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        user_id = get_current_user_id(credentials.credentials)
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception:
        return None


async def check_rate_limit(
    request_type: str = "general",
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None
) -> bool:
    """
    Check rate limit for API requests.
    
    Args:
        request_type: Type of request for different rate limits
        user_id: User ID for user-specific rate limiting
        ip_address: IP address for IP-based rate limiting
        
    Returns:
        bool: True if within rate limit, False otherwise
    """
    # Create rate limit key based on user or IP
    if user_id:
        rate_limit_key = f"rate_limit:{request_type}:user:{user_id}"
    elif ip_address:
        rate_limit_key = f"rate_limit:{request_type}:ip:{ip_address}"
    else:
        return True  # No rate limiting if no identifier
    
    # Check current request count
    current_requests = await redis_client.get(rate_limit_key)
    
    # Different rate limits for different request types
    rate_limits = {
        "login": 5,  # 5 login attempts per minute
        "register": 3,  # 3 registration attempts per minute
        "password_reset": 2,  # 2 password reset attempts per minute
        "email_verification": 5,  # 5 email verification attempts per minute
        "general": 100,  # 100 general requests per minute
    }
    
    limit = rate_limits.get(request_type, 100)
    
    if current_requests and int(current_requests) >= limit:
        return False
    
    # Increment request count
    await redis_client.increment(rate_limit_key)
    await redis_client.expire(rate_limit_key, 60)  # 1 minute expiry
    
    return True


def rate_limit_dependency(request_type: str = "general"):
    """
    Dependency factory for rate limiting.
    
    Args:
        request_type: Type of request for different rate limits
        
    Returns:
        Dependency function that checks rate limit
    """
    async def check_limit(
        current_user: Optional[User] = Depends(get_current_user_optional),
        # request: Request  # Can be added if needed to get IP
    ) -> None:
        user_id = current_user.id if current_user else None
        
        if not await check_rate_limit(request_type, user_id=user_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {request_type} requests"
            )
    
    return check_limit