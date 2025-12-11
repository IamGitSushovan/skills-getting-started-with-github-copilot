from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Should return the activities mapping
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_delete_flow():
    activity = "Chess Club"
    email = "test.user@example.com"

    # Ensure test email is not present initially
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up (POST)
    url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    resp = client.post(url)
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # Verify present in activities
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity]["participants"]

    # Duplicate signup should fail (400)
    resp_dup = client.post(url)
    assert resp_dup.status_code == 400

    # Delete the signup
    resp_del = client.delete(url)
    assert resp_del.status_code == 200
    assert f"Removed {email}" in resp_del.json().get("message", "")

    # Ensure removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_delete_nonexistent_returns_404():
    activity = "Chess Club"
    email = "not.present@example.com"
    url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    resp = client.delete(url)
    assert resp.status_code == 404
