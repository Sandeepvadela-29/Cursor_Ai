"""
Candidate profile management endpoints.
Includes candidate profile creation, viewing, and updating.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.core.database import get_db
from app.models.user import User, Candidate
from app.schemas.user import (
    CandidateResponse,
    CandidateCreate,
    CandidateUpdate,
    ApiResponse,
)
from app.api.dependencies import (
    get_current_candidate,
    get_current_verified_user,
)

router = APIRouter()


@router.get(
    "/profile",
    response_model=CandidateResponse,
    summary="Get candidate profile",
    description="Get detailed candidate profile information",
)
async def get_candidate_profile(
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get detailed candidate profile information.
    """
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )
    
    return CandidateResponse.model_validate(candidate)


@router.post(
    "/profile",
    response_model=CandidateResponse,
    summary="Create candidate profile",
    description="Create or update candidate profile",
)
async def create_or_update_candidate_profile(
    profile_data: CandidateCreate,
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
) -> Any:
    """
    Create or update candidate profile.
    
    This endpoint handles both creation and updates of candidate profiles.
    """
    # Check if profile already exists
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    
    if candidate:
        # Update existing profile
        return await update_candidate_profile_internal(candidate, profile_data, db)
    else:
        # Create new profile
        candidate = Candidate(user_id=current_user.id)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        return await update_candidate_profile_internal(candidate, profile_data, db)


@router.put(
    "/profile",
    response_model=CandidateResponse,
    summary="Update candidate profile",
    description="Update existing candidate profile",
)
async def update_candidate_profile(
    profile_data: CandidateUpdate,
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update existing candidate profile.
    """
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )
    
    return await update_candidate_profile_internal(candidate, profile_data, db)


async def update_candidate_profile_internal(
    candidate: Candidate,
    profile_data: CandidateUpdate,
    db: Session,
) -> CandidateResponse:
    """
    Internal function to update candidate profile.
    """
    # Update basic information
    if profile_data.headline is not None:
        candidate.headline = profile_data.headline
    
    if profile_data.summary is not None:
        candidate.summary = profile_data.summary
    
    if profile_data.current_job_title is not None:
        candidate.current_job_title = profile_data.current_job_title
    
    if profile_data.current_company is not None:
        candidate.current_company = profile_data.current_company
    
    if profile_data.experience_years is not None:
        candidate.experience_years = profile_data.experience_years
    
    # Update location
    if profile_data.city is not None:
        candidate.city = profile_data.city
    
    if profile_data.state is not None:
        candidate.state = profile_data.state
    
    if profile_data.country is not None:
        candidate.country = profile_data.country
    
    if profile_data.postal_code is not None:
        candidate.postal_code = profile_data.postal_code
    
    if profile_data.willing_to_relocate is not None:
        candidate.willing_to_relocate = profile_data.willing_to_relocate
    
    # Update career preferences
    if profile_data.desired_salary_min is not None:
        candidate.desired_salary_min = profile_data.desired_salary_min
    
    if profile_data.desired_salary_max is not None:
        candidate.desired_salary_max = profile_data.desired_salary_max
    
    if profile_data.preferred_job_type is not None:
        candidate.preferred_job_type = profile_data.preferred_job_type
    
    if profile_data.preferred_work_arrangement is not None:
        candidate.preferred_work_arrangement = profile_data.preferred_work_arrangement
    
    # Update skills and qualifications (store as JSON)
    if profile_data.skills is not None:
        candidate.skills = json.dumps(profile_data.skills)
    
    if profile_data.certifications is not None:
        candidate.certifications = json.dumps(profile_data.certifications)
    
    if profile_data.languages is not None:
        candidate.languages = json.dumps(profile_data.languages)
    
    # Update education
    if profile_data.education_level is not None:
        candidate.education_level = profile_data.education_level
    
    if profile_data.university is not None:
        candidate.university = profile_data.university
    
    if profile_data.degree is not None:
        candidate.degree = profile_data.degree
    
    if profile_data.field_of_study is not None:
        candidate.field_of_study = profile_data.field_of_study
    
    if profile_data.graduation_year is not None:
        candidate.graduation_year = profile_data.graduation_year
    
    # Update assessment information
    if profile_data.personality_type is not None:
        candidate.personality_type = profile_data.personality_type
    
    if profile_data.work_style is not None:
        candidate.work_style = profile_data.work_style
    
    if profile_data.communication_style is not None:
        candidate.communication_style = profile_data.communication_style
    
    if profile_data.leadership_style is not None:
        candidate.leadership_style = profile_data.leadership_style
    
    # Update values and culture (store as JSON)
    if profile_data.core_values is not None:
        candidate.core_values = json.dumps(profile_data.core_values)
    
    if profile_data.work_environment_preference is not None:
        candidate.work_environment_preference = json.dumps(profile_data.work_environment_preference)
    
    if profile_data.team_size_preference is not None:
        candidate.team_size_preference = profile_data.team_size_preference
    
    if profile_data.company_size_preference is not None:
        candidate.company_size_preference = profile_data.company_size_preference
    
    # Update privacy settings
    if profile_data.profile_visibility is not None:
        candidate.profile_visibility = profile_data.profile_visibility
    
    if profile_data.search_status is not None:
        candidate.search_status = profile_data.search_status
    
    db.commit()
    db.refresh(candidate)
    
    return CandidateResponse.model_validate(candidate)


@router.get(
    "/profile/visibility",
    response_model=dict,
    summary="Get profile visibility settings",
    description="Get current profile visibility and privacy settings",
)
async def get_profile_visibility(
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get current profile visibility and privacy settings.
    """
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )
    
    return {
        "profile_visibility": candidate.profile_visibility,
        "search_status": candidate.search_status,
    }


@router.put(
    "/profile/visibility",
    response_model=ApiResponse,
    summary="Update profile visibility",
    description="Update profile visibility and privacy settings",
)
async def update_profile_visibility(
    visibility_data: dict,
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update profile visibility and privacy settings.
    
    - **profile_visibility**: public, private, or employers_only
    - **search_status**: active, passive, or not_looking
    """
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )
    
    # Validate visibility options
    valid_visibility = ["public", "private", "employers_only"]
    valid_search_status = ["active", "passive", "not_looking"]
    
    if "profile_visibility" in visibility_data:
        if visibility_data["profile_visibility"] not in valid_visibility:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid profile visibility option"
            )
        candidate.profile_visibility = visibility_data["profile_visibility"]
    
    if "search_status" in visibility_data:
        if visibility_data["search_status"] not in valid_search_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid search status option"
            )
        candidate.search_status = visibility_data["search_status"]
    
    db.commit()
    
    return ApiResponse(
        success=True,
        message="Profile visibility updated successfully"
    )


@router.get(
    "/profile/completeness",
    response_model=dict,
    summary="Get profile completeness",
    description="Get profile completeness percentage and missing fields",
)
async def get_profile_completeness(
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get profile completeness percentage and missing fields.
    """
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )
    
    # Define required fields for completeness
    required_fields = [
        "headline", "summary", "current_job_title", "experience_years",
        "city", "country", "skills", "education_level", "desired_salary_min",
        "preferred_job_type", "preferred_work_arrangement"
    ]
    
    completed_fields = []
    missing_fields = []
    
    for field in required_fields:
        value = getattr(candidate, field)
        if value is not None and value != "" and value != 0:
            completed_fields.append(field)
        else:
            missing_fields.append(field)
    
    completeness_percentage = (len(completed_fields) / len(required_fields)) * 100
    
    return {
        "completeness_percentage": round(completeness_percentage, 2),
        "completed_fields": completed_fields,
        "missing_fields": missing_fields,
        "total_fields": len(required_fields),
    }