from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_hello_world():
    response = client.get('/')
    assert response.json()['Hello'] == 'World'
