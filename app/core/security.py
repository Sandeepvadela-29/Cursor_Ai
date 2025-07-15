"""
Security utilities for authentication and authorization.
Includes JWT token handling, password hashing, and security helpers.
"""

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, UserRole, AccountStatus

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_random_token(length: int = 32) -> str:
    """Generate a random token for email verification or password reset."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            return None
        
        if datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
            return None
        
        return payload
    except JWTError:
        return None


def get_current_user_id(token: str) -> Optional[int]:
    """Extract user ID from JWT token."""
    payload = verify_token(token)
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    try:
        return int(user_id)
    except ValueError:
        return None


def create_email_verification_token(user_id: int) -> str:
    """Create a token for email verification."""
    expires_delta = timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": str(user_id), "purpose": "email_verification"},
        expires_delta=expires_delta
    )


def create_password_reset_token(user_id: int) -> str:
    """Create a token for password reset."""
    expires_delta = timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": str(user_id), "purpose": "password_reset"},
        expires_delta=expires_delta
    )


def verify_email_verification_token(token: str) -> Optional[int]:
    """Verify email verification token and return user ID."""
    payload = verify_token(token)
    if payload is None:
        return None
    
    purpose = payload.get("purpose")
    if purpose != "email_verification":
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    try:
        return int(user_id)
    except ValueError:
        return None


def verify_password_reset_token(token: str) -> Optional[int]:
    """Verify password reset token and return user ID."""
    payload = verify_token(token)
    if payload is None:
        return None
    
    purpose = payload.get("purpose")
    if purpose != "password_reset":
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    try:
        return int(user_id)
    except ValueError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def check_user_permissions(user: User, required_role: UserRole = None, required_permissions: list = None) -> bool:
    """Check if user has required permissions."""
    # Check if user is active
    if not user.is_active:
        return False
    
    # Check if account is active
    if user.status != AccountStatus.ACTIVE:
        return False
    
    # Check if user is verified
    if not user.is_verified:
        return False
    
    # Check role-based permissions
    if required_role:
        if user.role != required_role and not user.is_superuser:
            return False
    
    # Admin users have all permissions
    if user.is_superuser:
        return True
    
    # Check specific permissions (can be extended)
    if required_permissions:
        # This can be extended to check specific permissions
        # For now, we'll use simple role-based checks
        pass
    
    return True


def validate_password_strength(password: str) -> bool:
    """Validate password strength requirements."""
    # Minimum length
    if len(password) < 8:
        return False
    
    # Check for uppercase letter
    if not any(c.isupper() for c in password):
        return False
    
    # Check for lowercase letter
    if not any(c.islower() for c in password):
        return False
    
    # Check for digit
    if not any(c.isdigit() for c in password):
        return False
    
    # Check for special character
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        return False
    
    return True


def is_account_locked(user: User) -> bool:
    """Check if user account is locked due to failed login attempts."""
    if user.account_locked_until is None:
        return False
    
    return datetime.now(timezone.utc) < user.account_locked_until


def increment_failed_login_attempts(db: Session, user: User) -> None:
    """Increment failed login attempts and lock account if necessary."""
    user.failed_login_attempts += 1
    
    # Lock account after 5 failed attempts for 30 minutes
    if user.failed_login_attempts >= 5:
        user.account_locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    db.commit()


def reset_failed_login_attempts(db: Session, user: User) -> None:
    """Reset failed login attempts after successful login."""
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.last_login = datetime.now(timezone.utc)
    db.commit()


class SecurityError(Exception):
    """Base exception for security-related errors."""
    pass


class InvalidTokenError(SecurityError):
    """Exception raised when token is invalid."""
    pass


class ExpiredTokenError(SecurityError):
    """Exception raised when token is expired."""
    pass


class InsufficientPermissionsError(SecurityError):
    """Exception raised when user lacks required permissions."""
    pass