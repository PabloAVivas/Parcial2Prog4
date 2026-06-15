import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestRegister:
    def test_register_user(self, client: TestClient):
        payload = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "celular": "1122334455",
            "email": "juan.perez@test.com",
            "password": "securepass123",
        }
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] > 0
        assert data["nombre"] == "Juan"
        assert data["apellido"] == "Pérez"
        assert data["email"] == "juan.perez@test.com"
        assert data["celular"] == "1122334455"
        assert data["activo"] is True
        roles = data["roles"]
        assert any(r["codigo"] == "CLIENT" for r in roles)

    def test_register_duplicate_email(self, client: TestClient):
        payload = {
            "nombre": "Admin",
            "apellido": "Duplicate",
            "celular": "9999999999",
            "email": "admin@foodstore.com",
            "password": "whatever123",
        }
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400
        data = resp.json()
        assert "ya corresponde a un usuario registrado" in data["detail"]

    def test_register_minimal_fields(self, client: TestClient):
        payload = {
            "nombre": "Minimal",
            "apellido": "User",
            "celular": "1111111111",
            "email": "minimal.user@test.com",
            "password": "minpass123",
        }
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] > 0
        assert data["nombre"] == "Minimal"
        assert data["apellido"] == "User"
        assert data["email"] == "minimal.user@test.com"
        assert data["activo"] is True


class TestLogin:
    def test_login_success(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@foodstore.com", "password": "admin123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert resp.cookies.get("access_token") is not None
        assert resp.cookies.get("refresh_token") is not None

    def test_login_invalid_password(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@foodstore.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401
        data = resp.json()
        assert data["detail"] == "Correo o contraseña incorrectos"

    def test_login_nonexistent_email(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "noexiste@test.com", "password": "somepass123"},
        )
        assert resp.status_code == 401

    def test_login_response_structure(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@foodstore.com", "password": "admin123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        assert data["token_type"] == "bearer"
        assert data["expires_in"] is not None


class TestLogout:
    def test_logout(self, client: TestClient):
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@foodstore.com", "password": "admin123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["mensaje"] == "Session cerrada correctamente"


class TestMe:
    def test_me_authenticated(self, client: TestClient):
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@foodstore.com", "password": "admin123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "admin@foodstore.com"
        assert data["nombre"] == "Admin"
        assert data["apellido"] == "Principal"
        assert "roles" in data
        assert "direcciones" in data

    def test_me_unauthenticated(self, client: TestClient):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401
