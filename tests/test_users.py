import uuid

import httpx
import pytest
from asgi_lifespan import LifespanManager

from app.main import app


@pytest.fixture
async def client():
    async with LifespanManager(app) as manager:
        transport = httpx.ASGITransport(app=manager.app)
        yield httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_create_fetch_duplicate(client: httpx.AsyncClient):
    email = f"user-{uuid.uuid4()}@example.com"

    resp = await client.post("/users", json={"name": "Alice", "email": email})
    assert resp.status_code == 201, resp.text
    created = resp.json()
    assert created["name"] == "Alice"
    assert created["email"] == email
    assert created["id_user"]

    resp = await client.get(f"/users/{created['id_user']}")
    assert resp.status_code == 200, resp.text
    fetched = resp.json()
    assert fetched == created

    resp = await client.get(f"/users/{created['id_user'].upper()}")
    assert resp.status_code == 200

    # Same email, different capitalisation -> users_email_lower_key -> 409
    resp = await client.post(
        "/users",
        json={"name": "Bob", "email": email.replace("user", "USER")},
    )
    assert resp.status_code == 409, resp.text
    assert "registered" in resp.json()["detail"]

    resp = await client.get("/users/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404

    resp = await client.get("/users/not-a-uuid")
    assert resp.status_code == 422
