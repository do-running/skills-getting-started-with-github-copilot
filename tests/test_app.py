import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities as app_activities

client = TestClient(app)
initial_activities = copy.deepcopy(app_activities)

@pytest.fixture(autouse=True)
def reset_activities():
    app_activities.clear()
    app_activities.update(copy.deepcopy(initial_activities))
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newuser@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    all_activities = client.get("/activities").json()
    assert email in all_activities[activity_name]["participants"]


def test_signup_duplicate_fails():
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity_404():
    # Arrange
    activity_name = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "x@y.com"})

    # Assert
    assert response.status_code == 404


def test_remove_signup_success():
    # Arrange
    activity_name = "Basketball Team"
    email = "alex@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}

    all_activities = client.get("/activities").json()
    assert email not in all_activities[activity_name]["participants"]


def test_remove_signup_not_registered_fails():
    # Arrange
    activity_name = "Basketball Team"
    email = "ghost@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"