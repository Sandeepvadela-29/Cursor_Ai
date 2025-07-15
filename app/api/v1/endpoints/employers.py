"""
Employer profile management endpoints.
Includes employer profile creation, viewing, and updating.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.core.database import get_db
from app.models.user import User, Employer
from app.schemas.user import (
    EmployerResponse,
    EmployerCreate,
    EmployerUpdate,
    ApiResponse,
)
from app.api.dependencies import (
    get_current_employer,
    get_current_verified_user,
)

router = APIRouter()


@router.get(
    "/profile",
    response_model=EmployerResponse,
    summary="Get employer profile",
    description="Get detailed employer profile information",
)
async def get_employer_profile(
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get detailed employer profile information.
    """
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer profile not found"
        )
    
    return EmployerResponse.model_validate(employer)


@router.post(
    "/profile",
    response_model=EmployerResponse,
    summary="Create employer profile",
    description="Create or update employer profile",
)
async def create_or_update_employer_profile(
    profile_data: EmployerCreate,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db),
) -> Any:
    """
    Create or update employer profile.
    
    This endpoint handles both creation and updates of employer profiles.
    """
    # Check if profile already exists
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    
    if employer:
        # Update existing profile
        return await update_employer_profile_internal(employer, profile_data, db)
    else:
        # Create new profile
        employer = Employer(
            user_id=current_user.id,
            company_name=profile_data.company_name
        )
        db.add(employer)
        db.commit()
        db.refresh(employer)
        
        return await update_employer_profile_internal(employer, profile_data, db)


@router.put(
    "/profile",
    response_model=EmployerResponse,
    summary="Update employer profile",
    description="Update existing employer profile",
)
async def update_employer_profile(
    profile_data: EmployerUpdate,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update existing employer profile.
    """
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer profile not found"
        )
    
    return await update_employer_profile_internal(employer, profile_data, db)


async def update_employer_profile_internal(
    employer: Employer,
    profile_data: EmployerUpdate,
    db: Session,
) -> EmployerResponse:
    """
    Internal function to update employer profile.
    """
    # Update company information
    if profile_data.company_name is not None:
        employer.company_name = profile_data.company_name
    
    if profile_data.company_website is not None:
        employer.company_website = profile_data.company_website
    
    if profile_data.company_size is not None:
        employer.company_size = profile_data.company_size
    
    if profile_data.industry is not None:
        employer.industry = profile_data.industry
    
    if profile_data.founded_year is not None:
        employer.founded_year = profile_data.founded_year
    
    # Update location
    if profile_data.headquarters_city is not None:
        employer.headquarters_city = profile_data.headquarters_city
    
    if profile_data.headquarters_state is not None:
        employer.headquarters_state = profile_data.headquarters_state
    
    if profile_data.headquarters_country is not None:
        employer.headquarters_country = profile_data.headquarters_country
    
    # Update company description
    if profile_data.company_description is not None:
        employer.company_description = profile_data.company_description
    
    if profile_data.mission_statement is not None:
        employer.mission_statement = profile_data.mission_statement
    
    if profile_data.vision_statement is not None:
        employer.vision_statement = profile_data.vision_statement
    
    if profile_data.core_values is not None:
        employer.core_values = json.dumps(profile_data.core_values)
    
    # Update culture and environment (store as JSON)
    if profile_data.company_culture is not None:
        employer.company_culture = json.dumps(profile_data.company_culture)
    
    if profile_data.work_environment is not None:
        employer.work_environment = json.dumps(profile_data.work_environment)
    
    if profile_data.benefits_offered is not None:
        employer.benefits_offered = json.dumps(profile_data.benefits_offered)
    
    if profile_data.perks_offered is not None:
        employer.perks_offered = json.dumps(profile_data.perks_offered)
    
    # Update diversity and inclusion
    if profile_data.diversity_initiatives is not None:
        employer.diversity_initiatives = profile_data.diversity_initiatives
    
    if profile_data.inclusion_programs is not None:
        employer.inclusion_programs = profile_data.inclusion_programs
    
    if profile_data.equal_opportunity_employer is not None:
        employer.equal_opportunity_employer = profile_data.equal_opportunity_employer
    
    # Update recruiter information
    if profile_data.recruiter_name is not None:
        employer.recruiter_name = profile_data.recruiter_name
    
    if profile_data.recruiter_title is not None:
        employer.recruiter_title = profile_data.recruiter_title
    
    if profile_data.recruiter_department is not None:
        employer.recruiter_department = profile_data.recruiter_department
    
    # Update company metrics
    if profile_data.employee_count is not None:
        employer.employee_count = profile_data.employee_count
    
    if profile_data.annual_revenue is not None:
        employer.annual_revenue = profile_data.annual_revenue
    
    if profile_data.growth_stage is not None:
        employer.growth_stage = profile_data.growth_stage
    
    # Update hiring information
    if profile_data.hiring_process_description is not None:
        employer.hiring_process_description = profile_data.hiring_process_description
    
    if profile_data.average_hiring_time is not None:
        employer.average_hiring_time = profile_data.average_hiring_time
    
    if profile_data.interview_process is not None:
        employer.interview_process = json.dumps(profile_data.interview_process)
    
    db.commit()
    db.refresh(employer)
    
    return EmployerResponse.model_validate(employer)


@router.get(
    "/profile/verification",
    response_model=dict,
    summary="Get verification status",
    description="Get company verification status and requirements",
)
async def get_verification_status(
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get company verification status and requirements.
    """
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer profile not found"
        )
    
    return {
        "is_verified": employer.is_verified,
        "verification_requirements": [
            "Company website",
            "Business registration documents",
            "Valid business email address",
            "Company logo and branding",
            "Complete company profile",
        ],
        "verification_status": "verified" if employer.is_verified else "pending",
    }


@router.post(
    "/profile/verification/request",
    response_model=ApiResponse,
    summary="Request verification",
    description="Request company verification",
)
async def request_verification(
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db),
) -> Any:
    """
    Request company verification.
    
    This endpoint submits a verification request for the company.
    """
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer profile not found"
        )
    
    if employer.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company is already verified"
        )
    
    # Check if profile is complete enough for verification
    required_fields = [
        "company_name", "company_website", "company_description",
        "industry", "headquarters_city", "headquarters_country"
    ]
    
    missing_fields = []
    for field in required_fields:
        value = getattr(employer, field)
        if value is None or value == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please complete the following fields before requesting verification: {', '.join(missing_fields)}"
        )
    
    # TODO: Implement verification request logic
    # This could involve sending an email to admin, creating a verification request record, etc.
    
    return ApiResponse(
        success=True,
        message="Verification request submitted successfully. Our team will review your company profile and contact you within 2-3 business days."
    )


@router.get(
    "/profile/completeness",
    response_model=dict,
    summary="Get profile completeness",
    description="Get profile completeness percentage and missing fields",
)
async def get_profile_completeness(
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get profile completeness percentage and missing fields.
    """
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer profile not found"
        )
    
    # Define required fields for completeness
    required_fields = [
        "company_name", "company_website", "company_description", "industry",
        "headquarters_city", "headquarters_country", "company_size",
        "mission_statement", "core_values", "benefits_offered",
        "recruiter_name", "recruiter_title"
    ]
    
    completed_fields = []
    missing_fields = []
    
    for field in required_fields:
        value = getattr(employer, field)
        if value is not None and value != "":
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


@router.get(
    "/subscription",
    response_model=dict,
    summary="Get subscription information",
    description="Get current subscription plan and billing information",
)
async def get_subscription_info(
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get current subscription plan and billing information.
    """
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer profile not found"
        )
    
    return {
        "subscription_plan": employer.subscription_plan,
        "subscription_start_date": employer.subscription_start_date,
        "subscription_end_date": employer.subscription_end_date,
        "is_active": employer.subscription_end_date is None or employer.subscription_end_date > db.query(db.func.now()).scalar(),
        "available_plans": {
            "free": {
                "name": "Free",
                "price": 0,
                "features": ["Basic profile", "Limited job posts", "Basic candidate search"],
                "job_posts_limit": 2,
                "candidate_contacts_limit": 5,
            },
            "basic": {
                "name": "Basic",
                "price": 99,
                "features": ["Full profile", "Unlimited job posts", "Advanced candidate search", "Email support"],
                "job_posts_limit": None,
                "candidate_contacts_limit": 50,
            },
            "premium": {
                "name": "Premium",
                "price": 299,
                "features": ["All Basic features", "Priority support", "Advanced analytics", "Custom branding"],
                "job_posts_limit": None,
                "candidate_contacts_limit": 200,
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 599,
                "features": ["All Premium features", "Dedicated account manager", "Custom integrations", "Unlimited contacts"],
                "job_posts_limit": None,
                "candidate_contacts_limit": None,
            },
        },
    }