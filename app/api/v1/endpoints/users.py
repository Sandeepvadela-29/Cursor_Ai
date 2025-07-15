"""
User profile management endpoints.
Includes profile viewing, updating, and account management.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import (
    UserProfile,
    UserUpdate,
    PasswordChange,
    ApiResponse,
)
from app.api.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
)

router = APIRouter()


@router.get(
    "/profile",
    response_model=UserProfile,
    summary="Get user profile",
    description="Get detailed profile information for the current user",
)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get detailed profile information for the current user.
    """
    return UserProfile.model_validate(current_user)


@router.put(
    "/profile",
    response_model=UserProfile,
    summary="Update user profile",
    description="Update user profile information",
)
async def update_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update user profile information.
    
    - **first_name**: First name
    - **last_name**: Last name
    - **phone**: Phone number
    """
    # Update user fields
    if profile_data.first_name is not None:
        current_user.first_name = profile_data.first_name
    
    if profile_data.last_name is not None:
        current_user.last_name = profile_data.last_name
    
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    
    db.commit()
    db.refresh(current_user)
    
    return UserProfile.model_validate(current_user)


@router.post(
    "/change-password",
    response_model=ApiResponse,
    summary="Change password",
    description="Change user password",
)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Change user password.
    
    - **current_password**: Current password
    - **new_password**: New password
    - **confirm_new_password**: Confirm new password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    
    return ApiResponse(
        success=True,
        message="Password changed successfully"
    )


@router.post(
    "/deactivate",
    response_model=ApiResponse,
    summary="Deactivate account",
    description="Deactivate user account",
)
async def deactivate_account(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Deactivate user account.
    This will set the account to inactive status.
    """
    current_user.is_active = False
    db.commit()
    
    return ApiResponse(
        success=True,
        message="Account deactivated successfully"
    )


@router.get(
    "/account-status",
    response_model=dict,
    summary="Get account status",
    description="Get current account status and statistics",
)
async def get_account_status(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current account status and statistics.
    """
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "status": current_user.status.value,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "mfa_enabled": current_user.mfa_enabled,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login,
        "failed_login_attempts": current_user.failed_login_attempts,
        "account_locked": current_user.account_locked_until is not None,
    }