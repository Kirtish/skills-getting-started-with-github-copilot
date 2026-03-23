import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial activities data for resetting
initial_activities = {
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
    "Art Studio": {
        "description": "Explore various art mediums including painting, drawing, and sculpture",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["isabella@mergington.edu"]
    },
    "Music Band": {
        "description": "Learn instruments and perform in school concerts",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["ava@mergington.edu", "noah@mergington.edu"]
    },
    "Debate Club": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 14,
        "participants": ["lucas@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging math problems and compete in competitions",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 12,
        "participants": ["sophie@mergington.edu", "james@mergington.edu"]
    },
    "Science Fair": {
        "description": "Prepare and present science projects",
        "schedule": "Mondays, 3:30 PM - 4:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Drama Club": {
        "description": "Act in plays and improve theatrical skills",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["lucas@mergington.edu"]
    }
}

@pytest.fixture
def reset_activities():
    """Fixture to reset activities data before each test"""
    # Arrange: Save original and reset to initial state
    original = activities.copy()
    activities.clear()
    activities.update(initial_activities)
    yield
    # Cleanup: Restore original after test
    activities.clear()
    activities.update(original)

@pytest.fixture
def client():
    """Fixture to provide TestClient"""
    return TestClient(app)

def test_get_activities(client, reset_activities):
    """Test GET /activities returns all activities"""
    # Arrange: Activities are reset via fixture
    
    # Act: Make request
    response = client.get("/activities")
    
    # Assert: Check response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert len(data) == 9  # Number of activities

def test_signup_success(client, reset_activities):
    """Test successful signup for an activity"""
    # Arrange: Choose an activity and new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act: Make signup request
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check response and data update
    assert response.status_code == 200
    assert f"Signed up {email} for {activity_name}" in response.json()["message"]
    # Verify participant was added
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity_name]["participants"]

def test_signup_duplicate(client, reset_activities):
    """Test signup fails for duplicate participant"""
    # Arrange: Use existing participant
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    
    # Act: Attempt signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Should fail with 400
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found(client, reset_activities):
    """Test signup fails for non-existent activity"""
    # Arrange: Invalid activity name
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"
    
    # Act: Attempt signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Should fail with 404
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_delete_participant_success(client, reset_activities):
    """Test successful participant removal"""
    # Arrange: Choose activity and existing participant
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act: Delete participant
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert: Check response and data update
    assert response.status_code == 200
    assert f"Removed {email} from {activity_name}" in response.json()["message"]
    # Verify participant was removed
    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]

def test_delete_participant_not_found(client, reset_activities):
    """Test delete fails for non-existent participant"""
    # Arrange: Valid activity, invalid participant
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"
    
    # Act: Attempt delete
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert: Should fail with 404
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]

def test_delete_activity_not_found(client, reset_activities):
    """Test delete fails for non-existent activity"""
    # Arrange: Invalid activity, valid email
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"
    
    # Act: Attempt delete
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert: Should fail with 404
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
