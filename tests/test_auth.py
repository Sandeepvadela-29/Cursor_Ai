"""
Unit tests for authentication module
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash, verify_password
from main import app
import os

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

# Test fixtures
@pytest.fixture
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890"
    }

@pytest.fixture
def test_employer_data():
    return {
        "email": "employer@company.com",
        "password": "EmployerPass123!",
        "first_name": "John",
        "last_name": "Employer",
        "phone": "+1987654321",
        "company_name": "Test Company Inc."
    }

class TestUserRegistration:
    """Test user registration endpoints"""
    
    def test_register_candidate_success(self, setup_database, test_user_data):
        """Test successful candidate registration"""
        response = client.post("/api/v1/auth/register/candidate", json=test_user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]
        assert data["last_name"] == test_user_data["last_name"]
        assert data["role"] == "candidate"
        assert data["status"] == "pending_verification"
        assert data["is_verified"] == False
    
    def test_register_employer_success(self, setup_database, test_employer_data):
        """Test successful employer registration"""
        response = client.post("/api/v1/auth/register/employer", json=test_employer_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == test_employer_data["email"]
        assert data["first_name"] == test_employer_data["first_name"]
        assert data["last_name"] == test_employer_data["last_name"]
        assert data["role"] == "employer"
        assert data["status"] == "pending_verification"
        assert data["is_verified"] == False
    
    def test_register_candidate_duplicate_email(self, setup_database, test_user_data):
        """Test registration with duplicate email"""
        # First registration
        client.post("/api/v1/auth/register/candidate", json=test_user_data)
        
        # Second registration with same email
        response = client.post("/api/v1/auth/register/candidate", json=test_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_weak_password(self, setup_database, test_user_data):
        """Test registration with weak password"""
        test_user_data["password"] = "weak"
        response = client.post("/api/v1/auth/register/candidate", json=test_user_data)
        assert response.status_code == 400
        assert "Password must contain" in response.json()["detail"]
    
    def test_register_invalid_email(self, setup_database, test_user_data):
        """Test registration with invalid email"""
        test_user_data["email"] = "invalid-email"
        response = client.post("/api/v1/auth/register/candidate", json=test_user_data)
        assert response.status_code == 422


class TestUserLogin:
    """Test user login endpoints"""
    
    def test_login_success(self, setup_database, test_user_data):
        """Test successful login"""
        # Register user first
        client.post("/api/v1/auth/register/candidate", json=test_user_data)
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
    
    def test_login_invalid_credentials(self, setup_database, test_user_data):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/api/v1/auth/register/candidate", json=test_user_data)
        
        # Login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, setup_database):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


class TestPasswordSecurity:
    """Test password security functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Verification should work
        assert verify_password(password, hashed) == True
        
        # Wrong password should fail
        assert verify_password("wrongpassword", hashed) == False
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        from app.core.security import validate_password_strength
        
        # Strong password
        assert validate_password_strength("StrongPass123!") == True
        
        # Weak passwords
        assert validate_password_strength("weak") == False
        assert validate_password_strength("onlylowercase") == False
        assert validate_password_strength("ONLYUPPERCASE") == False
        assert validate_password_strength("NoNumbers!") == False
        assert validate_password_strength("NoSpecialChars123") == False


class TestTokenOperations:
    """Test token creation and verification"""
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        from app.core.security import create_access_token, verify_token
        
        # Create token
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        # Verify token
        payload = verify_token(token)
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
    
    def test_token_refresh(self, setup_database, test_user_data):
        """Test token refresh functionality"""
        # Register and login
        client.post("/api/v1/auth/register/candidate", json=test_user_data)
        
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


class TestEmailVerification:
    """Test email verification endpoints"""
    
    def test_resend_verification(self, setup_database, test_user_data):
        """Test resend verification email"""
        # Register user
        client.post("/api/v1/auth/register/candidate", json=test_user_data)
        
        # Resend verification
        resend_data = {"email": test_user_data["email"]}
        response = client.post("/api/v1/auth/resend-verification", json=resend_data)
        assert response.status_code == 200
        assert "sent successfully" in response.json()["message"]
    
    def test_resend_verification_nonexistent_user(self, setup_database):
        """Test resend verification for non-existent user"""
        resend_data = {"email": "nonexistent@example.com"}
        response = client.post("/api/v1/auth/resend-verification", json=resend_data)
        assert response.status_code == 404


class TestPasswordReset:
    """Test password reset endpoints"""
    
    def test_forgot_password(self, setup_database, test_user_data):
        """Test forgot password request"""
        # Register user
        client.post("/api/v1/auth/register/candidate", json=test_user_data)
        
        # Request password reset
        reset_data = {"email": test_user_data["email"]}
        response = client.post("/api/v1/auth/forgot-password", json=reset_data)
        assert response.status_code == 200
        assert "sent if user exists" in response.json()["message"]
    
    def test_forgot_password_nonexistent_user(self, setup_database):
        """Test forgot password for non-existent user"""
        reset_data = {"email": "nonexistent@example.com"}
        response = client.post("/api/v1/auth/forgot-password", json=reset_data)
        assert response.status_code == 200  # Should not reveal if user exists


class TestProtectedEndpoints:
    """Test protected endpoints"""
    
    def test_get_current_user_without_token(self, setup_database):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403
    
    def test_get_current_user_with_token(self, setup_database, test_user_data):
        """Test accessing protected endpoint with valid token"""
        # Register and login
        client.post("/api/v1/auth/register/candidate", json=test_user_data)
        
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == test_user_data["email"]


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "TrueFit" in response.json()["message"]
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_api_health_endpoint(self):
        """Test API health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__])