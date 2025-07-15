"""
Authentication endpoints for user registration, login, and verification.
Includes email verification, password reset, and token refresh.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    create_email_verification_token,
    verify_email_verification_token,
    create_password_reset_token,
    verify_password_reset_token,
    is_account_locked,
    increment_failed_login_attempts,
    reset_failed_login_attempts,
)
from app.core.config import settings
from app.models.user import User, UserRole, AccountStatus, Candidate, Employer
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    AuthResponse,
    Token,
    TokenRefresh,
    EmailVerification,
    PasswordReset,
    PasswordResetConfirm,
    ApiResponse,
    ErrorResponse,
)
from app.api.dependencies import (
    get_current_user,
    get_current_active_user,
    rate_limit_dependency,
)
from app.services.email import send_verification_email, send_password_reset_email
from app.core.redis_client import redis_client

router = APIRouter()


@router.post(
    "/register",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account with email verification",
)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency("register")),
) -> Any:
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Strong password meeting requirements
    - **confirm_password**: Must match password
    - **role**: User role (candidate or employer)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    - **phone**: Optional phone number
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        role=UserRole(user_data.role.value),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        status=AccountStatus.PENDING,
        is_verified=False,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create role-specific profile
    if db_user.role == UserRole.CANDIDATE:
        candidate_profile = Candidate(user_id=db_user.id)
        db.add(candidate_profile)
    elif db_user.role == UserRole.EMPLOYER:
        # Company name will be set later when creating employer profile
        employer_profile = Employer(
            user_id=db_user.id,
            company_name="Company Name Required"  # Placeholder
        )
        db.add(employer_profile)
    
    db.commit()
    
    # Send verification email
    verification_token = create_email_verification_token(db_user.id)
    background_tasks.add_task(
        send_verification_email,
        db_user.email,
        db_user.first_name or "User",
        verification_token
    )
    
    return ApiResponse(
        success=True,
        message="User registered successfully. Please check your email for verification.",
        data={"user_id": db_user.id, "email": db_user.email}
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate user and return access tokens",
)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency("login")),
) -> Any:
    """
    Authenticate user and return access tokens.
    
    - **email**: User's email address
    - **password**: User's password
    """
    # Authenticate user
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        # Check if user exists for better error message
        existing_user = db.query(User).filter(User.email == user_credentials.email).first()
        if existing_user:
            # User exists but password is wrong
            increment_failed_login_attempts(db, existing_user)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    
    # Check if account is locked
    if is_account_locked(user):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked due to multiple failed login attempts"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Reset failed login attempts on successful login
    reset_failed_login_attempts(db, user)
    
    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in Redis for session management
    await redis_client.set(
        f"refresh_token:{user.id}",
        refresh_token,
        expire=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Get new access token using refresh token",
)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
) -> Any:
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Check if refresh token exists in Redis
    stored_token = await redis_client.get(f"refresh_token:{user_id}")
    if stored_token != token_data.refresh_token:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=token_data.refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/logout",
    response_model=ApiResponse,
    summary="User logout",
    description="Logout user and invalidate refresh token",
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Logout user and invalidate refresh token.
    """
    # Remove refresh token from Redis
    await redis_client.delete(f"refresh_token:{current_user.id}")
    
    return ApiResponse(
        success=True,
        message="Successfully logged out"
    )


@router.post(
    "/verify-email",
    response_model=ApiResponse,
    summary="Verify email address",
    description="Verify user's email address using verification token",
)
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency("email_verification")),
) -> Any:
    """
    Verify user's email address.
    
    - **token**: Email verification token
    """
    # Verify email verification token
    user_id = verify_email_verification_token(verification_data.token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user.is_verified:
        return ApiResponse(
            success=True,
            message="Email already verified"
        )
    
    # Verify user
    user.is_verified = True
    user.status = AccountStatus.ACTIVE
    db.commit()
    
    return ApiResponse(
        success=True,
        message="Email verified successfully"
    )


@router.post(
    "/resend-verification",
    response_model=ApiResponse,
    summary="Resend verification email",
    description="Resend email verification token",
)
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_dependency("email_verification")),
) -> Any:
    """
    Resend email verification token.
    """
    # Check if already verified
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Send verification email
    verification_token = create_email_verification_token(current_user.id)
    background_tasks.add_task(
        send_verification_email,
        current_user.email,
        current_user.first_name or "User",
        verification_token
    )
    
    return ApiResponse(
        success=True,
        message="Verification email sent successfully"
    )


@router.post(
    "/password-reset",
    response_model=ApiResponse,
    summary="Request password reset",
    description="Send password reset email to user",
)
async def request_password_reset(
    reset_data: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency("password_reset")),
) -> Any:
    """
    Request password reset.
    
    - **email**: User's email address
    """
    # Find user by email
    user = db.query(User).filter(User.email == reset_data.email).first()
    if not user:
        # Don't reveal if email exists or not
        return ApiResponse(
            success=True,
            message="If the email exists, a password reset link has been sent"
        )
    
    # Send password reset email
    reset_token = create_password_reset_token(user.id)
    background_tasks.add_task(
        send_password_reset_email,
        user.email,
        user.first_name or "User",
        reset_token
    )
    
    return ApiResponse(
        success=True,
        message="If the email exists, a password reset link has been sent"
    )


@router.post(
    "/password-reset/confirm",
    response_model=ApiResponse,
    summary="Confirm password reset",
    description="Reset password using reset token",
)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency("password_reset")),
) -> Any:
    """
    Confirm password reset.
    
    - **token**: Password reset token
    - **new_password**: New password
    - **confirm_new_password**: Confirm new password
    """
    # Verify password reset token
    user_id = verify_password_reset_token(reset_data.token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = hash_password(reset_data.new_password)
    
    # Reset failed login attempts
    user.failed_login_attempts = 0
    user.account_locked_until = None
    
    db.commit()
    
    # Invalidate all refresh tokens for this user
    await redis_client.delete(f"refresh_token:{user.id}")
    
    return ApiResponse(
        success=True,
        message="Password reset successfully"
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current authenticated user information.
    """
    return UserResponse.model_validate(current_user)