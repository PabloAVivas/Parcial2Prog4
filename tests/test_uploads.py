"""Tests for the images/uploads module.

Endpoints (no auth required):
    GET    /api/v1/uploads/
    GET    /api/v1/uploads/{imagen_id}
    POST   /api/v1/uploads/imagen    (multipart: files[])
    DELETE /api/v1/uploads/imagen/{imagen_id}
"""

from itertools import count
from unittest.mock import patch

from fastapi.testclient import TestClient

_unique_id = count()


def _fake_cloudinary_response():
    i = next(_unique_id)
    return {
        "public_id": f"foodStore/test_{i}",
        "secure_url": "https://res.cloudinary.com/demo/image/upload/v1/foodStore/test.jpg",
        "format": "jpg",
        "width": 800,
        "height": 600,
        "bytes": 12345,
    }


def _fake_jpeg_bytes() -> bytes:
    """Return minimal valid JPEG bytes for testing."""
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \"#\x1c\x1c(7),01444\x17\xf7\'9\x82\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x00\x00\x00\x00\x01\x02\x03\x00\x04\x11\x05\x12!1\x06\x13AQa\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xd9\xff\xd9"


class TestListarImagenes:
    def test_listar_vacio(self, client: TestClient):
        resp = client.get("/api/v1/uploads/")
        assert resp.status_code == 200
        assert resp.json() == []


class TestObtenerImagen:
    def test_obtener_inexistente(self, client: TestClient):
        resp = client.get("/api/v1/uploads/999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Imagen no encontrada"


class TestSubirImagenes:
    def test_subir_tipo_invalido(self, client: TestClient):
        resp = client.post(
            "/api/v1/uploads/imagen",
            files={"files": ("test.txt", b"not an image", "text/plain")},
        )
        assert resp.status_code == 400
        assert "Tipo de archivo no permitido" in resp.json()["detail"]

    def test_subir_una_imagen(self, client: TestClient):
        with patch(
            "app.modules.images.service.cloudinary.uploader.upload"
        ) as mock_upload:
            fake = _fake_cloudinary_response()
            mock_upload.return_value = fake
            resp = client.post(
                "/api/v1/uploads/imagen",
                files={"files": ("test.jpg", _fake_jpeg_bytes(), "image/jpeg")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        img = data[0]
        assert img["public_id"] == fake["public_id"]
        assert img["url"] == fake["secure_url"]
        assert img["format"] == "jpg"
        assert img["width"] == 800
        assert img["height"] == 600
        assert img["bytes"] == 12345
        assert img["id"] > 0

    def test_subir_multiples_imagenes(self, client: TestClient):
        with patch(
            "app.modules.images.service.cloudinary.uploader.upload"
        ) as mock_upload:
            fake_a = _fake_cloudinary_response()
            fake_b = _fake_cloudinary_response()
            mock_upload.side_effect = [fake_a, fake_b]
            resp = client.post(
                "/api/v1/uploads/imagen",
                files=[
                    ("files", ("img1.jpg", _fake_jpeg_bytes(), "image/jpeg")),
                    ("files", ("img2.jpg", _fake_jpeg_bytes(), "image/jpeg")),
                ],
            )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["public_id"] == fake_a["public_id"]
        assert data[1]["public_id"] == fake_b["public_id"]


class TestEliminarImagen:
    def test_eliminar_inexistente(self, client: TestClient):
        resp = client.delete("/api/v1/uploads/imagen/999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Imagen no encontrada"

    def test_eliminar_existente(self, client: TestClient):
        with patch(
            "app.modules.images.service.cloudinary.uploader.upload"
        ) as mock_upload:
            mock_upload.return_value = _fake_cloudinary_response()
            resp = client.post(
                "/api/v1/uploads/imagen",
                files={"files": ("test.jpg", _fake_jpeg_bytes(), "image/jpeg")},
            )
            assert resp.status_code == 200
            imagen_id = resp.json()[0]["id"]

        with patch("app.modules.images.service.cloudinary.uploader.destroy"):
            resp = client.delete(f"/api/v1/uploads/imagen/{imagen_id}")
            assert resp.status_code == 204

        resp = client.get(f"/api/v1/uploads/{imagen_id}")
        assert resp.status_code == 404
