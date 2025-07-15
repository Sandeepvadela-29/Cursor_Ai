"""
Tests for user profile management endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_user_profile_success(self, client, auth_headers, test_user):
        """Test getting user profile successfully."""
        response = client.get("/api/v1/users/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role.value
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name

    def test_get_user_profile_unauthorized(self, client):
        """Test getting user profile without authentication."""
        response = client.get("/api/v1/users/profile")
        
        assert response.status_code == 401

    def test_update_user_profile_success(self, client, auth_headers, test_user):
        """Test updating user profile successfully."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+1987654321"
        }
        
        response = client.put("/api/v1/users/profile", 
                            headers=auth_headers, 
                            json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["phone"] == "+1987654321"

    def test_update_user_profile_partial(self, client, auth_headers):
        """Test partial update of user profile."""
        update_data = {
            "first_name": "PartialUpdate"
        }
        
        response = client.put("/api/v1/users/profile", 
                            headers=auth_headers, 
                            json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "PartialUpdate"

    def test_change_password_success(self, client, auth_headers):
        """Test changing password successfully."""
        password_data = {
            "current_password": "testpassword123!",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!"
        }
        
        response = client.post("/api/v1/users/change-password", 
                             headers=auth_headers, 
                             json=password_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "changed successfully" in data["message"]

    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password."""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!"
        }
        
        response = client.post("/api/v1/users/change-password", 
                             headers=auth_headers, 
                             json=password_data)
        
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"]

    def test_change_password_mismatch(self, client, auth_headers):
        """Test changing password with mismatched new passwords."""
        password_data = {
            "current_password": "testpassword123!",
            "new_password": "NewPassword123!",
            "confirm_new_password": "DifferentPassword123!"
        }
        
        response = client.post("/api/v1/users/change-password", 
                             headers=auth_headers, 
                             json=password_data)
        
        assert response.status_code == 422

    def test_deactivate_account_success(self, client, auth_headers):
        """Test deactivating account successfully."""
        response = client.post("/api/v1/users/deactivate", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deactivated successfully" in data["message"]

    def test_get_account_status_success(self, client, auth_headers, test_user):
        """Test getting account status successfully."""
        response = client.get("/api/v1/users/account-status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role.value
        assert data["is_active"] is True
        assert data["is_verified"] is True
        assert "created_at" in data
        assert "failed_login_attempts" in data