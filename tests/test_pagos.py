"""Tests for Pago (payment) module — MP integration, webhooks, confirmation."""

from unittest.mock import patch

from fastapi import status

from app.modules.pago.services import PagoService


class TestCreatePreference:
    """POST /api/v1/pagos/create-preference"""

    ENDPOINT = "/api/v1/pagos/create-preference"

    def test_sin_mp_configurado(self, client, pedido_factory, producto_factory):
        """Returns 400 when MP_ACCESS_TOKEN is not set."""
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        with patch.object(PagoService, "_get_mp_access_token", return_value=None):
            resp = client.post(self.ENDPOINT, json={"pedido_id": pedido.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "MercadoPago no configurado" in resp.json()["detail"]

    def test_pedido_inexistente(self, client):
        """Returns 404 when pedido does not exist."""
        resp = client.post(self.ENDPOINT, json={"pedido_id": 99999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "Pedido no encontrado" in resp.json()["detail"]


class TestWebhook:
    """POST /api/v1/pagos/webhook"""

    ENDPOINT = "/api/v1/pagos/webhook"

    def test_body_vacio(self, client):
        """Empty JSON body returns ignored with reason."""
        resp = client.post(
            self.ENDPOINT,
            json={},
            headers={"Content-Type": "application/json"},
        )
        assert resp.json() == {"status": "ignored", "reason": "No payment ID"}

    def test_topic_desconocido(self, client):
        """Unknown topic returns ignored status."""
        resp = client.post(
            self.ENDPOINT,
            json={"topic": "some_random_topic"},
            headers={"Content-Type": "application/json"},
        )
        data = resp.json()
        assert data["status"] == "ignored"

    def test_con_payment_id_sin_mp(self, client):
        """With a payment ID but MP not configured, call fails with error."""
        with patch.object(PagoService, "_get_mp_access_token", return_value=None):
            resp = client.post(
                self.ENDPOINT,
                json={"id": 12345},
                headers={"Content-Type": "application/json"},
            )
        data = resp.json()
        assert data["status"] == "error"
        assert "MP no configurado" in data["reason"]

    def test_processed_con_mock(
        self, client, pedido_factory, producto_factory
    ):
        """Mock MP API: webhook finds no local Pago → returns ignored."""
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        mp_return = {
            "mp_payment_id": 999,
            "mp_status": "approved",
            "mp_status_detail": "accredited",
            "external_reference": str(pedido.id),
            "payment_method_id": "visa",
        }

        with patch.object(PagoService, "_consultar_pago_mp", return_value=mp_return):
            resp = client.post(
                self.ENDPOINT,
                json={"id": 999},
                headers={"Content-Type": "application/json"},
            )

        data = resp.json()
        assert data["status"] == "ignored"
        assert "Pago not found in local DB" in data["reason"]

    def test_webhook_form_data(self, client):
        """Webhook also accepts form-encoded data."""
        with patch.object(PagoService, "_get_mp_access_token", return_value=None):
            resp = client.post(
                self.ENDPOINT,
                data={"id": "54321"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        data = resp.json()
        assert data["status"] == "error"
        assert "MP no configurado" in data["reason"]


class TestConfirmPayment:
    """POST /api/v1/pagos/confirm"""

    ENDPOINT = "/api/v1/pagos/confirm"

    def test_pedido_inexistente(self, client):
        """Returns 404 when pedido does not exist (pedido lookup first)."""
        resp = client.post(self.ENDPOINT, json={"pedido_id": 99999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "Pedido no encontrado" in resp.json()["detail"]

    def test_con_mp_payment_id_sin_mp(
        self, client, pedido_factory, producto_factory
    ):
        """With mp_payment_id but MP not configured → 400."""
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        with patch.object(PagoService, "_get_mp_access_token", return_value=None):
            resp = client.post(
                self.ENDPOINT,
                json={"pedido_id": pedido.id, "mp_payment_id": 12345},
            )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "MP no configurado" in resp.json()["detail"]

    def test_sin_mp_payment_id_sin_pago_local(
        self, client, pedido_factory, producto_factory
    ):
        """No mp_payment_id and no local pago → returns estado=None."""
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        resp = client.post(
            self.ENDPOINT,
            json={"pedido_id": pedido.id},
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["estado"] is None
        assert data["pedido_id"] == pedido.id
