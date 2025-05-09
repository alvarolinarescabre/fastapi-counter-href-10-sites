import pytest
from starlette.testclient import TestClient

from main import app


@pytest.fixture(autouse=True, scope="module")
def client():
    client = TestClient(app)
    return client


def test_index(client):
    """
    Test that we can get the index of the app
    :param client:
    :return:
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) > 0


def test_health_check(client):
    """
    Test that we can check the health of the app
    :param client:
    :return:
    """
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) > 0

    

def test_get_tags(client):
    """
    Test that we can get the tags from the app
    :param client:
    :return:
    """
    response = client.get("/v1/tags")
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) > 0


def test_get_tag(client):
    """
    Test that we can get the tag by id
    :param client:
    :return:
    """
    response = client.get("/v1/tags/0")
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) > 0