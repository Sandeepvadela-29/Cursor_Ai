"""
Tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.models.user import User, UserRole, AccountStatus
from app.core.security import hash_password, create_access_token


class TestUserRegistration:
    """Test user registration endpoints."""

    def test_register_candidate_success(self, client):
        """Test successful candidate registration."""
        user_data = {
            "email": "candidate@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "role": "candidate",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890"
        }
        
        with patch('app.services.email.send_verification_email') as mock_send_email:
            mock_send_email.return_value = True
            
            response = client.post("/api/v1/auth/register", json=user_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert "verification" in data["message"]
            assert "user_id" in data["data"]
            assert data["data"]["email"] == user_data["email"]
            
            # Verify email was sent
            mock_send_email.assert_called_once()

    def test_register_employer_success(self, client):
        """Test successful employer registration."""
        user_data = {
            "email": "employer@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "role": "employer",
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        with patch('app.services.email.send_verification_email') as mock_send_email:
            mock_send_email.return_value = True
            
            response = client.post("/api/v1/auth/register", json=user_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user.email,
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "role": "candidate"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_password_mismatch(self, client):
        """Test registration with password mismatch."""
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "confirm_password": "DifferentPassword123!",
            "role": "candidate"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
        assert "Passwords do not match" in str(response.json())

    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        user_data = {
            "email": "test@example.com",
            "password": "weak",
            "confirm_password": "weak",
            "role": "candidate"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422


class TestUserLogin:
    """Test user login endpoints."""

    def test_login_success(self, client, test_user):
        """Test successful login."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "tokens" in data
        assert data["user"]["email"] == test_user.email
        assert data["tokens"]["access_token"]
        assert data["tokens"]["refresh_token"]

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "testpassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_inactive_user(self, client, test_user, db_session):
        """Test login with inactive user."""
        test_user.is_active = False
        db_session.commit()
        
        login_data = {
            "email": test_user.email,
            "password": "testpassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 400
        assert "deactivated" in response.json()["detail"]


class TestTokenOperations:
    """Test token-related operations."""

    def test_refresh_token_success(self, client, test_user):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123!"
        })
        
        refresh_token = login_response.json()["tokens"]["refresh_token"]
        
        # Refresh token
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid token."""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        
        assert response.status_code == 401

    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "logged out" in data["message"]

    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user info."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role.value


class TestEmailVerification:
    """Test email verification endpoints."""

    def test_verify_email_success(self, client, test_user, db_session):
        """Test successful email verification."""
        # Set user as unverified
        test_user.is_verified = False
        test_user.status = AccountStatus.PENDING
        db_session.commit()
        
        # Create verification token
        from app.core.security import create_email_verification_token
        token = create_email_verification_token(test_user.id)
        
        response = client.post("/api/v1/auth/verify-email", json={
            "token": token
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "verified successfully" in data["message"]

    def test_verify_email_invalid_token(self, client):
        """Test email verification with invalid token."""
        response = client.post("/api/v1/auth/verify-email", json={
            "token": "invalid_token"
        })
        
        assert response.status_code == 400
        assert "Invalid or expired" in response.json()["detail"]

    def test_resend_verification_success(self, client, test_user, db_session):
        """Test resending verification email."""
        # Set user as unverified
        test_user.is_verified = False
        db_session.commit()
        
        # Login to get auth headers
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123!"
        })
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        with patch('app.services.email.send_verification_email') as mock_send_email:
            mock_send_email.return_value = True
            
            response = client.post("/api/v1/auth/resend-verification", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            mock_send_email.assert_called_once()


class TestPasswordReset:
    """Test password reset endpoints."""

    def test_request_password_reset_success(self, client, test_user):
        """Test successful password reset request."""
        with patch('app.services.email.send_password_reset_email') as mock_send_email:
            mock_send_email.return_value = True
            
            response = client.post("/api/v1/auth/password-reset", json={
                "email": test_user.email
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "reset link" in data["message"]
            mock_send_email.assert_called_once()

    def test_request_password_reset_nonexistent_user(self, client):
        """Test password reset request for non-existent user."""
        response = client.post("/api/v1/auth/password-reset", json={
            "email": "nonexistent@example.com"
        })
        
        # Should return success for security reasons
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_confirm_password_reset_success(self, client, test_user):
        """Test successful password reset confirmation."""
        from app.core.security import create_password_reset_token
        token = create_password_reset_token(test_user.id)
        
        response = client.post("/api/v1/auth/password-reset/confirm", json={
            "token": token,
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reset successfully" in data["message"]

    def test_confirm_password_reset_invalid_token(self, client):
        """Test password reset confirmation with invalid token."""
        response = client.post("/api/v1/auth/password-reset/confirm", json={
            "token": "invalid_token",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!"
        })
        
        assert response.status_code == 400
        assert "Invalid or expired" in response.json()["detail"]