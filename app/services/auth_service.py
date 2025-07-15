"""
Authentication service with business logic for user registration, login, and verification
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole, UserStatus, CandidateProfile, EmployerProfile, LoginAttempt
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    create_verification_token,
    verify_verification_token,
    generate_verification_token,
    validate_password_strength
)
from app.core.config import settings
from app.schemas.auth import (
    UserCreate, 
    CandidateRegister, 
    EmployerRegister, 
    UserLogin, 
    TokenResponse, 
    UserResponse
)
from app.services.email_service import send_verification_email, send_password_reset_email


class AuthService:
    """Authentication service class"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_candidate(self, user_data: CandidateRegister, ip_address: str) -> UserResponse:
        """Register a new candidate"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        if not validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least 8 characters with uppercase, lowercase, digit, and special character"
            )
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        verification_token = generate_verification_token()
        
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            role=UserRole.CANDIDATE,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            verification_token=verification_token,
            verification_token_expires=datetime.utcnow() + timedelta(minutes=settings.verification_token_expire_minutes)
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create candidate profile
        candidate_profile = CandidateProfile(user_id=user.id)
        self.db.add(candidate_profile)
        self.db.commit()
        
        # Send verification email
        send_verification_email(user.email, verification_token)
        
        return UserResponse.from_orm(user)
    
    def register_employer(self, user_data: EmployerRegister, ip_address: str) -> UserResponse:
        """Register a new employer"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        if not validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least 8 characters with uppercase, lowercase, digit, and special character"
            )
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        verification_token = generate_verification_token()
        
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            role=UserRole.EMPLOYER,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            verification_token=verification_token,
            verification_token_expires=datetime.utcnow() + timedelta(minutes=settings.verification_token_expire_minutes)
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create employer profile
        employer_profile = EmployerProfile(
            user_id=user.id,
            company_name=user_data.company_name
        )
        self.db.add(employer_profile)
        self.db.commit()
        
        # Send verification email
        send_verification_email(user.email, verification_token)
        
        return UserResponse.from_orm(user)
    
    def login(self, login_data: UserLogin, ip_address: str, user_agent: str) -> TokenResponse:
        """Authenticate user and return tokens"""
        # Check if user exists
        user = self.db.query(User).filter(User.email == login_data.email).first()
        
        # Log login attempt
        login_attempt = LoginAttempt(
            email=login_data.email,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not user:
            login_attempt.success = False
            login_attempt.failure_reason = "User not found"
            self.db.add(login_attempt)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if account is locked
        if user.is_locked():
            login_attempt.success = False
            login_attempt.failure_reason = "Account locked"
            self.db.add(login_attempt)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to multiple failed login attempts"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            # Increment login attempts
            user.login_attempts += 1
            
            # Lock account if too many attempts
            if user.login_attempts >= settings.max_login_attempts:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.lockout_duration_minutes)
            
            login_attempt.success = False
            login_attempt.failure_reason = "Invalid password"
            self.db.add(login_attempt)
            self.db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE and user.status != UserStatus.PENDING_VERIFICATION:
            login_attempt.success = False
            login_attempt.failure_reason = "Account inactive"
            self.db.add(login_attempt)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Reset login attempts on successful login
        user.login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        
        # Create tokens
        token_data = {"sub": user.email, "user_id": user.id, "role": user.role.value}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        login_attempt.success = True
        self.db.add(login_attempt)
        self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.from_orm(user)
        )
    
    def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        user = self.db.query(User).filter(User.verification_token == token).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        if user.verification_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired"
            )
        
        # Mark user as verified
        user.is_verified = True
        user.status = UserStatus.ACTIVE
        user.verification_token = None
        user.verification_token_expires = None
        
        self.db.commit()
        return True
    
    def resend_verification_email(self, email: str) -> bool:
        """Resend verification email"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Generate new verification token
        verification_token = generate_verification_token()
        user.verification_token = verification_token
        user.verification_token_expires = datetime.utcnow() + timedelta(minutes=settings.verification_token_expire_minutes)
        
        self.db.commit()
        
        # Send verification email
        send_verification_email(user.email, verification_token)
        return True
    
    def request_password_reset(self, email: str) -> bool:
        """Request password reset"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if user exists or not
            return True
        
        # Generate reset token
        reset_token = generate_verification_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(minutes=settings.verification_token_expire_minutes)
        
        self.db.commit()
        
        # Send reset email
        send_password_reset_email(user.email, reset_token)
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token"""
        user = self.db.query(User).filter(User.reset_token == token).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        if user.reset_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Validate password strength
        if not validate_password_strength(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least 8 characters with uppercase, lowercase, digit, and special character"
            )
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.login_attempts = 0
        user.locked_until = None
        
        self.db.commit()
        return True
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        try:
            payload = verify_token(refresh_token)
            
            # Check if it's a refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("user_id")
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Create new tokens
            token_data = {"sub": user.email, "user_id": user.id, "role": user.role.value}
            access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token(token_data)
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=settings.access_token_expire_minutes * 60,
                user=UserResponse.from_orm(user)
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    def get_current_user(self, token: str) -> User:
        """Get current user from token"""
        try:
            payload = verify_token(token)
            user_id = payload.get("user_id")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            return user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )