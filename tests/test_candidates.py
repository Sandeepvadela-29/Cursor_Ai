"""
Tests for candidate profile endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestCandidateProfile:
    """Test candidate profile endpoints."""

    def test_get_candidate_profile_not_found(self, client, auth_headers):
        """Test getting candidate profile when not found."""
        response = client.get("/api/v1/candidates/profile", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_candidate_profile_success(self, client, auth_headers):
        """Test creating candidate profile successfully."""
        profile_data = {
            "headline": "Software Engineer",
            "summary": "Experienced software engineer with 5 years of experience.",
            "current_job_title": "Senior Software Engineer",
            "current_company": "Tech Corp",
            "experience_years": 5,
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "desired_salary_min": 80000,
            "desired_salary_max": 120000,
            "preferred_job_type": "full-time",
            "preferred_work_arrangement": "remote",
            "skills": ["Python", "JavaScript", "React", "SQL"],
            "education_level": "Bachelor's",
            "university": "Stanford University",
            "degree": "Computer Science",
            "core_values": ["Innovation", "Work-life balance", "Growth"],
            "profile_visibility": "public",
            "search_status": "active"
        }
        
        response = client.post("/api/v1/candidates/profile", 
                             headers=auth_headers, 
                             json=profile_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["headline"] == profile_data["headline"]
        assert data["summary"] == profile_data["summary"]
        assert data["experience_years"] == profile_data["experience_years"]
        assert data["city"] == profile_data["city"]

    def test_update_candidate_profile_success(self, client, auth_headers):
        """Test updating candidate profile successfully."""
        # First create a profile
        create_data = {
            "headline": "Software Engineer",
            "summary": "Initial summary",
            "experience_years": 3,
            "city": "New York"
        }
        
        client.post("/api/v1/candidates/profile", 
                   headers=auth_headers, 
                   json=create_data)
        
        # Then update it
        update_data = {
            "headline": "Senior Software Engineer",
            "summary": "Updated summary with more experience",
            "experience_years": 5,
            "city": "San Francisco"
        }
        
        response = client.put("/api/v1/candidates/profile", 
                            headers=auth_headers, 
                            json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["headline"] == "Senior Software Engineer"
        assert data["summary"] == "Updated summary with more experience"
        assert data["experience_years"] == 5
        assert data["city"] == "San Francisco"

    def test_get_candidate_profile_success(self, client, auth_headers):
        """Test getting candidate profile after creation."""
        # Create profile first
        create_data = {
            "headline": "Data Scientist",
            "summary": "Data scientist with ML expertise",
            "experience_years": 4
        }
        
        client.post("/api/v1/candidates/profile", 
                   headers=auth_headers, 
                   json=create_data)
        
        # Get profile
        response = client.get("/api/v1/candidates/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["headline"] == "Data Scientist"
        assert data["summary"] == "Data scientist with ML expertise"
        assert data["experience_years"] == 4

    def test_get_profile_visibility_success(self, client, auth_headers):
        """Test getting profile visibility settings."""
        # Create profile first
        create_data = {
            "headline": "Test Engineer",
            "profile_visibility": "employers_only",
            "search_status": "passive"
        }
        
        client.post("/api/v1/candidates/profile", 
                   headers=auth_headers, 
                   json=create_data)
        
        # Get visibility settings
        response = client.get("/api/v1/candidates/profile/visibility", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["profile_visibility"] == "employers_only"
        assert data["search_status"] == "passive"

    def test_update_profile_visibility_success(self, client, auth_headers):
        """Test updating profile visibility settings."""
        # Create profile first
        create_data = {"headline": "Test Engineer"}
        client.post("/api/v1/candidates/profile", 
                   headers=auth_headers, 
                   json=create_data)
        
        # Update visibility
        visibility_data = {
            "profile_visibility": "private",
            "search_status": "not_looking"
        }
        
        response = client.put("/api/v1/candidates/profile/visibility", 
                            headers=auth_headers, 
                            json=visibility_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "updated successfully" in data["message"]

    def test_update_profile_visibility_invalid(self, client, auth_headers):
        """Test updating profile visibility with invalid values."""
        # Create profile first
        create_data = {"headline": "Test Engineer"}
        client.post("/api/v1/candidates/profile", 
                   headers=auth_headers, 
                   json=create_data)
        
        # Try to update with invalid visibility
        visibility_data = {
            "profile_visibility": "invalid_option"
        }
        
        response = client.put("/api/v1/candidates/profile/visibility", 
                            headers=auth_headers, 
                            json=visibility_data)
        
        assert response.status_code == 400
        assert "Invalid profile visibility" in response.json()["detail"]

    def test_get_profile_completeness_success(self, client, auth_headers):
        """Test getting profile completeness."""
        # Create partial profile
        create_data = {
            "headline": "Test Engineer",
            "summary": "Test summary",
            "experience_years": 3,
            "city": "Test City",
            "country": "Test Country"
        }
        
        client.post("/api/v1/candidates/profile", 
                   headers=auth_headers, 
                   json=create_data)
        
        # Get completeness
        response = client.get("/api/v1/candidates/profile/completeness", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "completeness_percentage" in data
        assert "completed_fields" in data
        assert "missing_fields" in data
        assert "total_fields" in data
        assert data["completeness_percentage"] >= 0
        assert data["completeness_percentage"] <= 100

    def test_employer_cannot_access_candidate_endpoints(self, client, employer_auth_headers):
        """Test that employers cannot access candidate endpoints."""
        response = client.get("/api/v1/candidates/profile", headers=employer_auth_headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]