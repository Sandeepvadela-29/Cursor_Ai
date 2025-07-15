"""
User profile schemas for candidates and employers
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class CandidateProfileBase(BaseModel):
    """Base candidate profile schema"""
    title: Optional[str] = None
    summary: Optional[str] = None
    experience_years: Optional[int] = None
    current_salary: Optional[int] = None
    expected_salary: Optional[int] = None
    location: Optional[str] = None
    is_remote_preferred: Optional[bool] = False
    is_willing_to_relocate: Optional[bool] = False
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    languages: Optional[List[Dict[str, str]]] = None
    notice_period: Optional[str] = None
    availability_status: Optional[str] = "open"
    is_profile_public: Optional[bool] = True
    is_open_to_recruiters: Optional[bool] = True


class CandidateProfileCreate(CandidateProfileBase):
    """Candidate profile creation schema"""
    pass


class CandidateProfileUpdate(CandidateProfileBase):
    """Candidate profile update schema"""
    pass


class CandidateProfileResponse(CandidateProfileBase):
    """Candidate profile response schema"""
    id: int
    user_id: int
    resume_url: Optional[str] = None
    cover_letter_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    video_intro_url: Optional[str] = None
    personality_traits: Optional[Dict[str, Any]] = None
    work_values: Optional[Dict[str, Any]] = None
    communication_style: Optional[Dict[str, Any]] = None
    leadership_style: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class EmployerProfileBase(BaseModel):
    """Base employer profile schema"""
    company_name: str
    company_size: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: Optional[List[str]] = None
    headquarters_location: Optional[str] = None
    office_locations: Optional[List[str]] = None
    work_culture: Optional[Dict[str, Any]] = None
    benefits: Optional[List[str]] = None
    perks: Optional[List[str]] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class EmployerProfileCreate(EmployerProfileBase):
    """Employer profile creation schema"""
    pass


class EmployerProfileUpdate(EmployerProfileBase):
    """Employer profile update schema"""
    pass


class EmployerProfileResponse(EmployerProfileBase):
    """Employer profile response schema"""
    id: int
    user_id: int
    logo_url: Optional[str] = None
    company_images: Optional[List[str]] = None
    is_verified: Optional[bool] = False
    verification_documents: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class PersonalityAssessment(BaseModel):
    """Personality assessment schema"""
    openness: int  # 1-10 scale
    conscientiousness: int
    extraversion: int
    agreeableness: int
    neuroticism: int
    
    @validator('openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism')
    def validate_score(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Score must be between 1 and 10')
        return v


class WorkValuesAssessment(BaseModel):
    """Work values assessment schema"""
    work_life_balance: int  # 1-10 scale
    career_growth: int
    compensation: int
    job_security: int
    autonomy: int
    social_impact: int
    creativity: int
    teamwork: int
    
    @validator('work_life_balance', 'career_growth', 'compensation', 'job_security', 
               'autonomy', 'social_impact', 'creativity', 'teamwork')
    def validate_score(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Score must be between 1 and 10')
        return v


class CommunicationStyleAssessment(BaseModel):
    """Communication style assessment schema"""
    directness: int  # 1-10 scale
    formality: int
    detail_orientation: int
    feedback_preference: int
    
    @validator('directness', 'formality', 'detail_orientation', 'feedback_preference')
    def validate_score(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Score must be between 1 and 10')
        return v


class LeadershipStyleAssessment(BaseModel):
    """Leadership style assessment schema"""
    democratic: int  # 1-10 scale
    autocratic: int
    laissez_faire: int
    transformational: int
    transactional: int
    
    @validator('democratic', 'autocratic', 'laissez_faire', 'transformational', 'transactional')
    def validate_score(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Score must be between 1 and 10')
        return v