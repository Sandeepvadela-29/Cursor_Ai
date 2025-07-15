"""
Tests for employer profile endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestEmployerProfile:
    """Test employer profile endpoints."""

    def test_get_employer_profile_not_found(self, client, employer_auth_headers):
        """Test getting employer profile when not found."""
        response = client.get("/api/v1/employers/profile", headers=employer_auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_employer_profile_success(self, client, employer_auth_headers):
        """Test creating employer profile successfully."""
        profile_data = {
            "company_name": "Tech Innovations Inc",
            "company_website": "https://techinnovations.com",
            "company_size": "medium",
            "industry": "Technology",
            "founded_year": 2015,
            "headquarters_city": "San Francisco",
            "headquarters_state": "CA",
            "headquarters_country": "USA",
            "company_description": "Leading technology company focused on innovation.",
            "mission_statement": "To innovate and transform technology for better tomorrow.",
            "core_values": ["Innovation", "Integrity", "Excellence"],
            "benefits_offered": ["Health Insurance", "401k", "Flexible Hours"],
            "recruiter_name": "Jane Smith",
            "recruiter_title": "Senior Recruiter",
            "employee_count": 250,
            "growth_stage": "growth"
        }
        
        response = client.post("/api/v1/employers/profile", 
                             headers=employer_auth_headers, 
                             json=profile_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == profile_data["company_name"]
        assert data["company_website"] == profile_data["company_website"]
        assert data["industry"] == profile_data["industry"]
        assert data["headquarters_city"] == profile_data["headquarters_city"]

    def test_update_employer_profile_success(self, client, employer_auth_headers):
        """Test updating employer profile successfully."""
        # First create a profile
        create_data = {
            "company_name": "Initial Company",
            "company_website": "https://initial.com",
            "industry": "Finance",
            "headquarters_city": "New York"
        }
        
        client.post("/api/v1/employers/profile", 
                   headers=employer_auth_headers, 
                   json=create_data)
        
        # Then update it
        update_data = {
            "company_name": "Updated Company Inc",
            "company_website": "https://updated.com",
            "industry": "Technology",
            "headquarters_city": "San Francisco",
            "employee_count": 500
        }
        
        response = client.put("/api/v1/employers/profile", 
                            headers=employer_auth_headers, 
                            json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Updated Company Inc"
        assert data["company_website"] == "https://updated.com"
        assert data["industry"] == "Technology"
        assert data["headquarters_city"] == "San Francisco"
        assert data["employee_count"] == 500

    def test_get_employer_profile_success(self, client, employer_auth_headers):
        """Test getting employer profile after creation."""
        # Create profile first
        create_data = {
            "company_name": "Test Company",
            "company_website": "https://test.com",
            "industry": "Healthcare",
            "headquarters_city": "Boston"
        }
        
        client.post("/api/v1/employers/profile", 
                   headers=employer_auth_headers, 
                   json=create_data)
        
        # Get profile
        response = client.get("/api/v1/employers/profile", headers=employer_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Test Company"
        assert data["company_website"] == "https://test.com"
        assert data["industry"] == "Healthcare"
        assert data["headquarters_city"] == "Boston"

    def test_get_verification_status_success(self, client, employer_auth_headers):
        """Test getting verification status."""
        # Create profile first
        create_data = {
            "company_name": "Test Company",
            "company_website": "https://test.com"
        }
        
        client.post("/api/v1/employers/profile", 
                   headers=employer_auth_headers, 
                   json=create_data)
        
        # Get verification status
        response = client.get("/api/v1/employers/profile/verification", headers=employer_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "is_verified" in data
        assert "verification_requirements" in data
        assert "verification_status" in data
        assert data["is_verified"] is False
        assert len(data["verification_requirements"]) > 0

    def test_request_verification_incomplete_profile(self, client, employer_auth_headers):
        """Test requesting verification with incomplete profile."""
        # Create incomplete profile
        create_data = {
            "company_name": "Test Company"
        }
        
        client.post("/api/v1/employers/profile", 
                   headers=employer_auth_headers, 
                   json=create_data)
        
        # Try to request verification
        response = client.post("/api/v1/employers/profile/verification/request", 
                             headers=employer_auth_headers)
        
        assert response.status_code == 400
        assert "complete the following fields" in response.json()["detail"]

    def test_request_verification_complete_profile(self, client, employer_auth_headers):
        """Test requesting verification with complete profile."""
        # Create complete profile
        create_data = {
            "company_name": "Test Company",
            "company_website": "https://test.com",
            "company_description": "Test description",
            "industry": "Technology",
            "headquarters_city": "San Francisco",
            "headquarters_country": "USA"
        }
        
        client.post("/api/v1/employers/profile", 
                   headers=employer_auth_headers, 
                   json=create_data)
        
        # Request verification
        response = client.post("/api/v1/employers/profile/verification/request", 
                             headers=employer_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "submitted successfully" in data["message"]

    def test_get_profile_completeness_success(self, client, employer_auth_headers):
        """Test getting profile completeness."""
        # Create partial profile
        create_data = {
            "company_name": "Test Company",
            "company_website": "https://test.com",
            "industry": "Technology",
            "headquarters_city": "San Francisco"
        }
        
        client.post("/api/v1/employers/profile", 
                   headers=employer_auth_headers, 
                   json=create_data)
        
        # Get completeness
        response = client.get("/api/v1/employers/profile/completeness", headers=employer_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "completeness_percentage" in data
        assert "completed_fields" in data
        assert "missing_fields" in data
        assert "total_fields" in data
        assert data["completeness_percentage"] >= 0
        assert data["completeness_percentage"] <= 100

    def test_get_subscription_info_success(self, client, employer_auth_headers):
        """Test getting subscription information."""
        # Create profile first
        create_data = {
            "company_name": "Test Company",
            "company_website": "https://test.com"
        }
        
        client.post("/api/v1/employers/profile", 
                   headers=employer_auth_headers, 
                   json=create_data)
        
        # Get subscription info
        response = client.get("/api/v1/employers/subscription", headers=employer_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "subscription_plan" in data
        assert "available_plans" in data
        assert data["subscription_plan"] == "free"
        assert "free" in data["available_plans"]
        assert "basic" in data["available_plans"]
        assert "premium" in data["available_plans"]
        assert "enterprise" in data["available_plans"]

    def test_candidate_cannot_access_employer_endpoints(self, client, auth_headers):
        """Test that candidates cannot access employer endpoints."""
        response = client.get("/api/v1/employers/profile", headers=auth_headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]