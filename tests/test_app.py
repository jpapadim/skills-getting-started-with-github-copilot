import pytest
from copy import deepcopy
from urllib.parse import quote
from fastapi.testclient import TestClient

import src.app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Preserve original in-memory activities and restore after each test
    orig = deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(orig))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Tennis Club" in data


def test_signup_and_duplicate():
    activity = "Tennis Club"
    email = "tester@example.com"
    url = f"/activities/{quote(activity)}/signup?email={email}"

    # First signup should succeed
    r1 = client.post(url)
    assert r1.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Second signup should fail with 400
    r2 = client.post(url)
    assert r2.status_code == 400


def test_unregister():
    activity = "Basketball Team"
    email = "remove_me@example.com"
    signup_url = f"/activities/{quote(activity)}/signup?email={email}"

    # Sign up then remove
    r_signup = client.post(signup_url)
    assert r_signup.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    r_delete = client.delete(signup_url)
    assert r_delete.status_code == 200
    assert email not in app_module.activities[activity]["participants"]
