"""
Authentication schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    role: UserRole
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class CandidateRegister(UserCreate):
    """Candidate registration schema"""
    role: UserRole = UserRole.CANDIDATE


class EmployerRegister(UserCreate):
    """Employer registration schema"""
    role: UserRole = UserRole.EMPLOYER
    company_name: str


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: UserRole
    status: UserStatus
    is_verified: bool
    profile_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    token: str


class ResendVerificationRequest(BaseModel):
    """Resend verification request schema"""
    email: EmailStr


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UpdateProfileRequest(BaseModel):
    """Update profile request schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class MessageResponse(BaseModel):
    """Generic message response schema"""
    message: str
    success: bool = True