"""
User models for the TrueFit platform.
Includes base user, candidate, and employer models with comprehensive fields.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class UserRole(enum.Enum):
    """User roles for role-based access control."""
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    ADMIN = "admin"


class AccountStatus(enum.Enum):
    """Account status for user verification and management."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class User(Base):
    """Base user model for authentication and common fields."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(AccountStatus), default=AccountStatus.PENDING)
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    profile_picture = Column(String(500))  # URL to profile picture
    
    # Account management
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Multi-factor authentication
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(32))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Login tracking
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True))
    
    # Relationships
    candidate_profile = relationship("Candidate", back_populates="user", uselist=False)
    employer_profile = relationship("Employer", back_populates="user", uselist=False)
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_candidate(self) -> bool:
        """Check if user is a candidate."""
        return self.role == UserRole.CANDIDATE
    
    @property
    def is_employer(self) -> bool:
        """Check if user is an employer."""
        return self.role == UserRole.EMPLOYER
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN
    
    def __repr__(self):
        return f"<User {self.email}>"


class Candidate(Base):
    """Extended profile for job seekers."""
    
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Personal Information
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    nationality = Column(String(50))
    
    # Location
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    willing_to_relocate = Column(Boolean, default=False)
    
    # Professional Information
    headline = Column(String(200))  # Professional headline
    summary = Column(Text)  # Professional summary
    current_job_title = Column(String(200))
    current_company = Column(String(200))
    experience_years = Column(Integer, default=0)
    
    # Career Preferences
    desired_salary_min = Column(Float)
    desired_salary_max = Column(Float)
    preferred_job_type = Column(String(50))  # full-time, part-time, contract, etc.
    preferred_work_arrangement = Column(String(50))  # remote, hybrid, on-site
    availability_start_date = Column(DateTime)
    
    # Skills and Qualifications
    skills = Column(Text)  # JSON array of skills
    certifications = Column(Text)  # JSON array of certifications
    languages = Column(Text)  # JSON array of languages with proficiency
    
    # Education
    education_level = Column(String(50))
    university = Column(String(200))
    degree = Column(String(200))
    field_of_study = Column(String(200))
    graduation_year = Column(Integer)
    
    # Career Assessment (for matching)
    personality_type = Column(String(50))
    work_style = Column(String(50))
    communication_style = Column(String(50))
    leadership_style = Column(String(50))
    
    # Values and Culture Assessment
    core_values = Column(Text)  # JSON array of core values
    work_environment_preference = Column(Text)  # JSON object with preferences
    team_size_preference = Column(String(50))
    company_size_preference = Column(String(50))
    
    # Documents
    resume_url = Column(String(500))
    cover_letter_url = Column(String(500))
    portfolio_url = Column(String(500))
    video_intro_url = Column(String(500))
    
    # Privacy Settings
    profile_visibility = Column(String(20), default="public")  # public, private, employers_only
    search_status = Column(String(20), default="active")  # active, passive, not_looking
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    
    def __repr__(self):
        return f"<Candidate {self.user.email}>"


class Employer(Base):
    """Extended profile for employers and companies."""
    
    __tablename__ = "employers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Company Information
    company_name = Column(String(200), nullable=False)
    company_website = Column(String(500))
    company_logo = Column(String(500))
    company_size = Column(String(50))  # startup, small, medium, large, enterprise
    industry = Column(String(100))
    founded_year = Column(Integer)
    
    # Location
    headquarters_city = Column(String(100))
    headquarters_state = Column(String(100))
    headquarters_country = Column(String(100))
    
    # Company Description
    company_description = Column(Text)
    mission_statement = Column(Text)
    vision_statement = Column(Text)
    core_values = Column(Text)  # JSON array of company values
    
    # Culture and Environment
    company_culture = Column(Text)  # JSON object describing culture
    work_environment = Column(Text)  # JSON object describing work environment
    benefits_offered = Column(Text)  # JSON array of benefits
    perks_offered = Column(Text)  # JSON array of perks
    
    # Diversity and Inclusion
    diversity_initiatives = Column(Text)
    inclusion_programs = Column(Text)
    equal_opportunity_employer = Column(Boolean, default=True)
    
    # Recruiter Information
    recruiter_name = Column(String(200))
    recruiter_title = Column(String(200))
    recruiter_department = Column(String(200))
    
    # Company Metrics
    employee_count = Column(Integer)
    annual_revenue = Column(String(50))
    growth_stage = Column(String(50))  # startup, growth, mature, declining
    
    # Hiring Information
    hiring_process_description = Column(Text)
    average_hiring_time = Column(Integer)  # days
    interview_process = Column(Text)  # JSON array describing interview stages
    
    # Company Images and Media
    office_images = Column(Text)  # JSON array of office image URLs
    team_photos = Column(Text)  # JSON array of team photo URLs
    company_videos = Column(Text)  # JSON array of company video URLs
    
    # Verification Status
    is_verified = Column(Boolean, default=False)
    verification_documents = Column(Text)  # JSON array of verification document URLs
    
    # Subscription and Billing
    subscription_plan = Column(String(50), default="free")  # free, basic, premium, enterprise
    subscription_start_date = Column(DateTime)
    subscription_end_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="employer_profile")
    
    def __repr__(self):
        return f"<Employer {self.company_name}>"


class EmailVerification(Base):
    """Email verification tokens."""
    
    __tablename__ = "email_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(255), unique=True, index=True)
    expires_at = Column(DateTime(timezone=True))
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PasswordReset(Base):
    """Password reset tokens."""
    
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(255), unique=True, index=True)
    expires_at = Column(DateTime(timezone=True))
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserSession(Base):
    """Track user sessions for security."""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(255), unique=True, index=True)
    refresh_token = Column(String(500))
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())