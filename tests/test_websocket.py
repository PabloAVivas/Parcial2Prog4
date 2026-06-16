import json
import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect


def _login_set_cookies(client: TestClient, email: str, password: str):
    """Login via POST /api/v1/auth/login so the client stores cookies."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200


class TestWebSocketAuth:

    def test_connect_without_auth(self, client: TestClient):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/api/v1/pedidos/cocina/ws"):
                pass

    def test_connect_as_client(self, client: TestClient):
        _login_set_cookies(client, "cliente@foodstore.com", "cliente123")
        with client.websocket_connect("/api/v1/pedidos/cocina/ws"):
            pass

    def test_connect_as_admin(self, client: TestClient):
        _login_set_cookies(client, "admin@foodstore.com", "admin123")
        with client.websocket_connect("/api/v1/pedidos/cocina/ws"):
            pass


class TestWebSocketSubscribe:

    def test_subscribe_as_admin(
        self, client: TestClient, producto_factory, pedido_factory
    ):
        _login_set_cookies(client, "admin@foodstore.com", "admin123")
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        with client.websocket_connect("/api/v1/pedidos/cocina/ws") as ws:
            ws.send_json({"action": "subscribe-order", "pedido_id": pedido.id})
            resp = ws.receive_json()
            assert resp["event"] == "SUBSCRIBED"
            assert resp["data"]["pedido_id"] == pedido.id

    def test_subscribe_own_order_as_client(
        self, client: TestClient, producto_factory, pedido_factory
    ):
        _login_set_cookies(client, "cliente@foodstore.com", "cliente123")
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        with client.websocket_connect("/api/v1/pedidos/cocina/ws") as ws:
            ws.send_json({"action": "subscribe-order", "pedido_id": pedido.id})
            resp = ws.receive_json()
            assert resp["event"] == "SUBSCRIBED"
            assert resp["data"]["pedido_id"] == pedido.id

    def test_subscribe_other_order_as_client(
        self, client: TestClient, producto_factory, pedido_factory
    ):
        _login_set_cookies(client, "cliente@foodstore.com", "cliente123")
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=1, producto_id=producto.id)

        with client.websocket_connect("/api/v1/pedidos/cocina/ws") as ws:
            ws.send_json({"action": "subscribe-order", "pedido_id": pedido.id})
            resp = ws.receive_json()
            assert resp["event"] == "ERROR"
            assert "No autorizado" in resp["data"]["detail"]

    def test_invalid_json(
        self, client: TestClient, producto_factory, pedido_factory
    ):
        _login_set_cookies(client, "admin@foodstore.com", "admin123")
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        with client.websocket_connect("/api/v1/pedidos/cocina/ws") as ws:
            ws.send_text("this is not json")
            ws.send_json({"action": "subscribe-order", "pedido_id": pedido.id})
            resp = ws.receive_json()
            assert resp["event"] == "SUBSCRIBED"
            assert resp["data"]["pedido_id"] == pedido.id
