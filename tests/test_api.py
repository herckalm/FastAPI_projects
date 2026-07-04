import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, pool

from app.db import get_session
from app.main import app

sqlite_url = "sqlite:///:memory:"
engine = create_engine(
    sqlite_url, connect_args={"check_same_thread": False}, poolclass=pool.StaticPool
)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# 1. Test register user
def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register", json={"username": "batman", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "batman"


# 2. Test login returns token
def test_login_returns_token(client: TestClient):
    client.post(
        "/auth/register", json={"username": "superman", "password": "clarkkentpassword"}
    )
    response = client.post(
        "/auth/login", data={"username": "superman", "password": "clarkkentpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


# 3. Test create hero requires authentication
def test_create_hero_requires_authentication(client: TestClient):
    response = client.post(
        "/heroes", json={"name": "Wolverine", "power": "Regeneration", "level": 50}
    )
    assert response.status_code == 401


# 4. Test create hero with token
def test_create_hero_with_token(client: TestClient):
    client.post(
        "/auth/register", json={"username": "ironman", "password": "jarvispassword"}
    )
    login_resp = client.post(
        "/auth/login", data={"username": "ironman", "password": "jarvispassword"}
    )
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/heroes",
        json={"name": "Iron Man", "power": "Exosuit", "level": 85},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Iron Man"


# 5. Test create mission for missing hero returns 404
def test_create_mission_for_missing_hero_returns_404(client: TestClient):
    client.post("/auth/register", json={"username": "thor", "password": "odinpassword"})
    login_resp = client.post(
        "/auth/login", data={"username": "thor", "password": "odinpassword"}
    )
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/missions",
        json={"title": "Save Asgard", "difficulty": 9, "hero_id": 999},
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Hero not found"


# 6. Test normal user cannot delete hero
def test_normal_user_cannot_delete_hero(client: TestClient):
    # Registering first user -> automatically an admin in our registration rule
    client.post(
        "/auth/register", json={"username": "admin_user", "password": "adminpassword"}
    )

    # Registering second user -> regular user
    client.post(
        "/auth/register", json={"username": "normal_user", "password": "userpassword"}
    )
    login_resp = client.post(
        "/auth/login", data={"username": "normal_user", "password": "userpassword"}
    )
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/heroes/1", headers=headers)
    assert response.status_code == 403


# 7. Test admin can delete mission
def test_admin_can_delete_mission(client: TestClient):
    # First registered user becomes admin
    client.post("/auth/register", json={"username": "boss", "password": "bosspassword"})
    login_resp = client.post(
        "/auth/login", data={"username": "boss", "password": "bosspassword"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Hero and Mission
    client.post(
        "/heroes",
        json={"name": "Flash", "power": "Speed", "level": 70},
        headers=headers,
    )
    client.post(
        "/missions",
        json={"title": "Stop Reverse Flash", "difficulty": 8, "hero_id": 1},
        headers=headers,
    )

    # Admin deletion
    del_resp = client.delete("/missions/1", headers=headers)
    assert del_resp.status_code == 204
