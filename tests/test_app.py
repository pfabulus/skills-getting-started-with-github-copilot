import copy

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


# Keep a pristine copy of the initial in-memory data and reset before each test
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities():
    reset_activities()
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity checks
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_adds_participant():
    reset_activities()
    before = len(activities["Chess Club"]["participants"])
    resp = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert resp.status_code == 200
    assert "Signed up test@example.com for Chess Club" in resp.json()["message"]
    assert len(activities["Chess Club"]["participants"]) == before + 1
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_duplicate_behavior():
    reset_activities()
    email = "dup@example.com"
    resp1 = client.post(f"/activities/Programming%20Class/signup?email={email}")
    assert resp1.status_code == 200
    resp2 = client.post(f"/activities/Programming%20Class/signup?email={email}")
    # Application rejects duplicate signups; assert that behavior
    assert resp2.status_code == 400
    participants = activities["Programming Class"]["participants"]
    assert participants.count(email) == 1


def test_delete_removes_participant():
    reset_activities()
    # john@mergington.edu is initially in Gym Class according to the sample data
    email = "john@mergington.edu"
    assert email in activities["Gym Class"]["participants"]
    resp = client.delete(f"/activities/Gym%20Class/participants?email={email}")
    assert resp.status_code == 200
    assert email not in activities["Gym Class"]["participants"]
