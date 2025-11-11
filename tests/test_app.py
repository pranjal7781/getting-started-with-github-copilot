"""
Tests for the Mergington High School Activities API

This module contains comprehensive tests for all API endpoints including:
- Viewing activities
- Signing up for activities
- Unregistering from activities
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a known state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer team practicing tactics and fitness",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["alex@mergington.edu", "maria@mergington.edu"]
        },
        "Track and Field": {
            "description": "Running, jumping, and throwing events training",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["liam@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops and productions for stage performance",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Practice public speaking and competitive debating skills",
            "schedule": "Tuesdays, 5:00 PM - 6:30 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu", "mia@mergington.edu"]
        },
        "Math Club": {
            "description": "Problem solving, math competitions, and enrichment",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["sophia@mergington.edu", "oliver@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that getting activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activity_has_correct_structure(self, client, reset_activities):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_participants_list_is_array(self, client, reset_activities):
        """Test that participants list is an array"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signup fails if student is already signed up"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test that signup fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up for the same activity"""
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "student2@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
    
    def test_signup_updates_participant_count(self, client, reset_activities):
        """Test that signup updates participant count"""
        response_before = client.get("/activities")
        count_before = len(response_before.json()["Gym Class"]["participants"])
        
        client.post(
            "/activities/Gym%20Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response_after = client.get("/activities")
        count_after = len(response_after.json()["Gym Class"]["participants"])
        assert count_after == count_before + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregister fails if student is not signed up"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test that unregister fails for non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_updates_participant_count(self, client, reset_activities):
        """Test that unregister updates participant count"""
        response_before = client.get("/activities")
        count_before = len(response_before.json()["Chess Club"]["participants"])
        
        client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        response_after = client.get("/activities")
        count_after = len(response_after.json()["Chess Club"]["participants"])
        assert count_after == count_before - 1
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can sign up again after unregistering"""
        # Unregister
        client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        # Try to sign up again - should succeed
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_full_signup_unregister_flow(self, client, reset_activities):
        """Test complete flow: signup, verify, unregister, verify"""
        email = "integration_test@mergington.edu"
        activity = "Programming%20Class"
        
        # Signup
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        data = response.json()
        assert email in data["Programming Class"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Programming Class"]["participants"]
    
    def test_multiple_activities_independent(self, client, reset_activities):
        """Test that activities are independent"""
        email = "student@mergington.edu"
        
        # Sign up for two activities
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        client.post(
            "/activities/Art%20Club/signup",
            params={"email": email}
        )
        
        # Unregister from one
        client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": email}
        )
        
        # Verify only unregistered from Chess Club
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
        assert email in data["Art Club"]["participants"]
