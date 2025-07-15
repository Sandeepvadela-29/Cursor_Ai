"""
User models for candidates and employers
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base


class UserRole(enum.Enum):
    """User roles enumeration"""
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    ADMIN = "admin"


class UserStatus(enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """Base user model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION)
    
    # Common fields
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    profile_image = Column(String(255), nullable=True)
    
    # Verification fields
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    
    # Password reset fields
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Security fields
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    employer_profile = relationship("EmployerProfile", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_locked(self):
        """Check if user account is locked"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False


class CandidateProfile(Base):
    """Candidate profile model"""
    __tablename__ = "candidate_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Professional information
    title = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    current_salary = Column(Integer, nullable=True)
    expected_salary = Column(Integer, nullable=True)
    
    # Location preferences
    location = Column(String(200), nullable=True)
    is_remote_preferred = Column(Boolean, default=False)
    is_willing_to_relocate = Column(Boolean, default=False)
    
    # Skills and qualifications
    skills = Column(JSON, nullable=True)  # List of skills
    certifications = Column(JSON, nullable=True)  # List of certifications
    languages = Column(JSON, nullable=True)  # List of languages with proficiency
    
    # Documents
    resume_url = Column(String(255), nullable=True)
    cover_letter_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)
    
    # Video introduction
    video_intro_url = Column(String(255), nullable=True)
    
    # Persona and values (for matching)
    personality_traits = Column(JSON, nullable=True)
    work_values = Column(JSON, nullable=True)
    communication_style = Column(JSON, nullable=True)
    leadership_style = Column(JSON, nullable=True)
    
    # Availability
    availability_status = Column(String(50), default="open")  # open, not_looking, interviewing
    notice_period = Column(String(50), nullable=True)
    
    # Privacy settings
    is_profile_public = Column(Boolean, default=True)
    is_open_to_recruiters = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    
    def __repr__(self):
        return f"<CandidateProfile(id={self.id}, user_id={self.user_id})>"


class EmployerProfile(Base):
    """Employer profile model"""
    __tablename__ = "employer_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Company information
    company_name = Column(String(200), nullable=False)
    company_size = Column(String(50), nullable=True)  # startup, small, medium, large, enterprise
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Company description
    description = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    values = Column(JSON, nullable=True)
    
    # Location
    headquarters_location = Column(String(200), nullable=True)
    office_locations = Column(JSON, nullable=True)  # List of office locations
    
    # Company culture
    work_culture = Column(JSON, nullable=True)
    benefits = Column(JSON, nullable=True)
    perks = Column(JSON, nullable=True)
    
    # Media
    logo_url = Column(String(255), nullable=True)
    company_images = Column(JSON, nullable=True)  # List of company image URLs
    
    # Contact information
    contact_person = Column(String(200), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_documents = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="employer_profile")
    
    def __repr__(self):
        return f"<EmployerProfile(id={self.id}, company_name={self.company_name})>"


class LoginAttempt(Base):
    """Login attempt tracking for security"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv6 support
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, default=False)
    failure_reason = Column(String(200), nullable=True)
    attempted_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<LoginAttempt(email={self.email}, success={self.success})>"