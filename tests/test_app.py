"""
FastAPI Tests for Mergington High School Activities API
Using Arrange-Act-Assert (AAA) Testing Pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Arrange: Create test client for making HTTP requests"""
    return TestClient(app)


@pytest.fixture
def initial_activities():
    """Arrange: Store initial state of activities"""
    return copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities(initial_activities):
    """Reset activities to initial state before and after each test for isolation"""
    # Reset before test
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


# ============================================================================
# GET /activities Tests
# ============================================================================

class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test: Successfully retrieve all activities with status 200"""
        # Arrange - activities already exist in the system
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Test: Response contains required activity fields"""
        # Arrange - endpoint ready
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_shows_participant_count(self, client):
        """Test: Activities display current participants"""
        # Arrange - activities with known participants
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success_adds_student(self, client):
        """Test: Student successfully signs up for activity - AAA Pattern"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_success_response_message(self, client):
        """Test: Successful signup returns correct message"""
        # Arrange
        activity_name = "Programming Class"
        email = "alex@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_duplicate_registration_fails(self, client):
        """Test: Student cannot sign up twice for same activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_full_fails(self, client):
        """Test: Cannot sign up for activity at capacity"""
        # Arrange
        activity_name = "Chess Club"
        current_count = len(activities[activity_name]["participants"])
        activities[activity_name]["max_participants"] = current_count
        new_email = "newcomer@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"]
        assert new_email not in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test: Signup fails for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_multiple_students_increases_count(self, client):
        """Test: Multiple signup requests increase participant count correctly"""
        # Arrange
        activity_name = "Art Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        initial_count = len(activities[activity_name]["participants"])
        
        # Act - Sign up first student
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": emails[0]}
        )
        
        # Act - Sign up second student
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": emails[1]}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count + 2
        assert all(email in activities[activity_name]["participants"] for email in emails)


# ============================================================================
# DELETE /activities/{activity_name}/signup Tests
# ============================================================================

class TestRemoveFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint"""

    def test_remove_success_removes_student(self, client):
        """Test: Student successfully removed from activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_success_response_message(self, client):
        """Test: Removal returns correct message"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_remove_not_registered_fails(self, client):
        """Test: Cannot remove student not registered for activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_remove_activity_not_found(self, client):
        """Test: Cannot remove from non-existent activity"""
        # Arrange
        activity_name = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_remove_allows_signup_after_removal(self, client):
        """Test: Student can sign up again after being removed"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Remove student
        response_delete = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Sign up again
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response_delete.status_code == 200
        assert response_signup.status_code == 200
        assert email in activities[activity_name]["participants"]


# ============================================================================
# GET / (Root) Tests
# ============================================================================

class TestRootRedirect:
    """Test suite for GET / endpoint"""

    def test_root_returns_redirect(self, client):
        """Test: Root endpoint returns redirect status"""
        # Arrange - root endpoint available
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code in [301, 302, 307, 308]  # Redirect status codes

    def test_root_redirect_to_index(self, client):
        """Test: Root redirects to static/index.html"""
        # Arrange
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == 200


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_signup_and_remove_workflow(self, client):
        """Test: Complete workflow of signup then remove"""
        # Arrange
        activity_name = "Art Club"
        email = "workflow@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert signup
        assert signup_response.status_code == 200
        
        # Act - Retrieve to verify
        get_response = client.get("/activities")
        assert email in get_response.json()[activity_name]["participants"]
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert remove
        assert remove_response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_activity_capacity_workflow(self, client):
        """Test: Fill activity to capacity and verify no more signups"""
        # Arrange
        activity_name = "Science Club"
        activities[activity_name]["max_participants"] = len(activities[activity_name]["participants"]) + 1
        new_email1 = "final@mergington.edu"
        new_email2 = "overflow@mergington.edu"
        
        # Act - Fill to capacity
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email1}
        )
        
        # Act - Try to exceed capacity
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert new_email1 in activities[activity_name]["participants"]
        assert new_email2 not in activities[activity_name]["participants"]
