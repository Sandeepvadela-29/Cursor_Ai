"""
Pydantic schemas for user authentication and profile management.
Includes validation for registration, login, and profile updates.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict
from enum import Enum

from app.models.user import UserRole, AccountStatus


class UserRoleEnum(str, Enum):
    """User role enumeration for API."""
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    ADMIN = "admin"


class AccountStatusEnum(str, Enum):
    """Account status enumeration for API."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRoleEnum


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(c in special_chars for c in v):
            raise ValueError('Password must contain at least one special character')
        
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class EmailVerification(BaseModel):
    """Schema for email verification."""
    token: str


class UserResponse(UserBase):
    """Schema for user response (public information)."""
    id: int
    status: AccountStatusEnum
    is_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    profile_picture: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserProfile(UserResponse):
    """Extended user profile with additional information."""
    mfa_enabled: bool
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Candidate schemas
class CandidateBase(BaseModel):
    """Base candidate schema."""
    headline: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = None
    current_job_title: Optional[str] = Field(None, max_length=200)
    current_company: Optional[str] = Field(None, max_length=200)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    
    # Location
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    willing_to_relocate: Optional[bool] = False
    
    # Career preferences
    desired_salary_min: Optional[float] = Field(None, ge=0)
    desired_salary_max: Optional[float] = Field(None, ge=0)
    preferred_job_type: Optional[str] = Field(None, max_length=50)
    preferred_work_arrangement: Optional[str] = Field(None, max_length=50)
    
    # Skills and qualifications
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    languages: Optional[List[Dict[str, str]]] = None
    
    # Education
    education_level: Optional[str] = Field(None, max_length=50)
    university: Optional[str] = Field(None, max_length=200)
    degree: Optional[str] = Field(None, max_length=200)
    field_of_study: Optional[str] = Field(None, max_length=200)
    graduation_year: Optional[int] = Field(None, ge=1950, le=2030)
    
    # Assessment
    personality_type: Optional[str] = Field(None, max_length=50)
    work_style: Optional[str] = Field(None, max_length=50)
    communication_style: Optional[str] = Field(None, max_length=50)
    leadership_style: Optional[str] = Field(None, max_length=50)
    
    # Values and culture
    core_values: Optional[List[str]] = None
    work_environment_preference: Optional[Dict[str, Any]] = None
    team_size_preference: Optional[str] = Field(None, max_length=50)
    company_size_preference: Optional[str] = Field(None, max_length=50)
    
    # Privacy
    profile_visibility: Optional[str] = Field(default="public", max_length=20)
    search_status: Optional[str] = Field(default="active", max_length=20)


class CandidateCreate(CandidateBase):
    """Schema for creating candidate profile."""
    pass


class CandidateUpdate(CandidateBase):
    """Schema for updating candidate profile."""
    pass


class CandidateResponse(CandidateBase):
    """Schema for candidate response."""
    id: int
    user_id: int
    resume_url: Optional[str] = None
    cover_letter_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    video_intro_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Employer schemas
class EmployerBase(BaseModel):
    """Base employer schema."""
    company_name: str = Field(..., max_length=200)
    company_website: Optional[str] = Field(None, max_length=500)
    company_size: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    founded_year: Optional[int] = Field(None, ge=1800, le=2030)
    
    # Location
    headquarters_city: Optional[str] = Field(None, max_length=100)
    headquarters_state: Optional[str] = Field(None, max_length=100)
    headquarters_country: Optional[str] = Field(None, max_length=100)
    
    # Company description
    company_description: Optional[str] = None
    mission_statement: Optional[str] = None
    vision_statement: Optional[str] = None
    core_values: Optional[List[str]] = None
    
    # Culture and environment
    company_culture: Optional[Dict[str, Any]] = None
    work_environment: Optional[Dict[str, Any]] = None
    benefits_offered: Optional[List[str]] = None
    perks_offered: Optional[List[str]] = None
    
    # Diversity and inclusion
    diversity_initiatives: Optional[str] = None
    inclusion_programs: Optional[str] = None
    equal_opportunity_employer: Optional[bool] = True
    
    # Recruiter information
    recruiter_name: Optional[str] = Field(None, max_length=200)
    recruiter_title: Optional[str] = Field(None, max_length=200)
    recruiter_department: Optional[str] = Field(None, max_length=200)
    
    # Company metrics
    employee_count: Optional[int] = Field(None, ge=1)
    annual_revenue: Optional[str] = Field(None, max_length=50)
    growth_stage: Optional[str] = Field(None, max_length=50)
    
    # Hiring information
    hiring_process_description: Optional[str] = None
    average_hiring_time: Optional[int] = Field(None, ge=1)
    interview_process: Optional[List[Dict[str, str]]] = None


class EmployerCreate(EmployerBase):
    """Schema for creating employer profile."""
    pass


class EmployerUpdate(EmployerBase):
    """Schema for updating employer profile."""
    pass


class EmployerResponse(EmployerBase):
    """Schema for employer response."""
    id: int
    user_id: int
    company_logo: Optional[str] = None
    is_verified: bool
    subscription_plan: str
    office_images: Optional[List[str]] = None
    team_photos: Optional[List[str]] = None
    company_videos: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Authentication response schemas
class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


class AuthResponse(BaseModel):
    """Authentication response schema."""
    user: UserResponse
    tokens: Token
    message: str = "Authentication successful"


# API Response schemas
class ApiResponse(BaseModel):
    """Generic API response schema."""
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None