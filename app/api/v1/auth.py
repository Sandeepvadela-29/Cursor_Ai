"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.email_service import send_welcome_email
from app.api.dependencies import get_client_ip, get_user_agent, get_current_user
from app.schemas.auth import (
    CandidateRegister,
    EmployerRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    MessageResponse,
    EmailVerificationRequest,
    ResendVerificationRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
    RefreshTokenRequest,
    UpdateProfileRequest
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register/candidate", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_candidate(
    user_data: CandidateRegister,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new candidate
    
    - **email**: Valid email address
    - **password**: Strong password (8+ chars, uppercase, lowercase, digit, special char)
    - **first_name**: First name
    - **last_name**: Last name
    - **phone**: Phone number (optional)
    """
    auth_service = AuthService(db)
    ip_address = get_client_ip(request)
    
    user = auth_service.register_candidate(user_data, ip_address)
    
    return user


@router.post("/register/employer", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_employer(
    user_data: EmployerRegister,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new employer
    
    - **email**: Valid email address
    - **password**: Strong password (8+ chars, uppercase, lowercase, digit, special char)
    - **first_name**: First name
    - **last_name**: Last name
    - **phone**: Phone number (optional)
    - **company_name**: Company name
    """
    auth_service = AuthService(db)
    ip_address = get_client_ip(request)
    
    user = auth_service.register_employer(user_data, ip_address)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    
    Returns access token and refresh token
    """
    auth_service = AuthService(db)
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    token_response = auth_service.login(login_data, ip_address, user_agent)
    
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    auth_service = AuthService(db)
    
    token_response = auth_service.refresh_token(refresh_data.refresh_token)
    
    return token_response


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification_data: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Verify email address with token
    """
    auth_service = AuthService(db)
    
    # Get user by token first to send welcome email
    user = db.query(User).filter(User.verification_token == verification_data.token).first()
    
    auth_service.verify_email(verification_data.token)
    
    # Send welcome email in background
    if user:
        background_tasks.add_task(
            send_welcome_email,
            user.email,
            user.full_name,
            user.role.value
        )
    
    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    verification_data: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend email verification
    """
    auth_service = AuthService(db)
    
    auth_service.resend_verification_email(verification_data.email)
    
    return MessageResponse(message="Verification email sent successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    """
    auth_service = AuthService(db)
    
    auth_service.request_password_reset(reset_data.email)
    
    return MessageResponse(message="Password reset email sent if user exists")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password with token
    """
    auth_service = AuthService(db)
    
    auth_service.reset_password(reset_data.token, reset_data.new_password)
    
    return MessageResponse(message="Password reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user
    """
    auth_service = AuthService(db)
    
    # Verify current password
    from app.core.security import verify_password, get_password_hash, validate_password_strength
    
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if not validate_password_strength(password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return MessageResponse(message="Password changed successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    # Update fields if provided
    if profile_data.first_name is not None:
        current_user.first_name = profile_data.first_name
    
    if profile_data.last_name is not None:
        current_user.last_name = profile_data.last_name
    
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user
    
    Note: In a production environment, you would typically blacklist the token
    or implement a token revocation mechanism
    """
    # Here you would typically:
    # 1. Add token to blacklist
    # 2. Clear server-side session if using sessions
    # 3. Log the logout event
    
    return MessageResponse(message="Logged out successfully")