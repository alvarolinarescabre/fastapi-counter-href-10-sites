import pytest
from starlette.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    """
    Test that we can check the health of the app
    :param client:
    :return:
    """
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"success": "pong!"}