"""Tests for Pedidos (Orders) module — FSM, UoW, snapshots, audit trail."""

from fastapi import status


class TestCrearPedido:
    """POST /api/v1/pedidos/ — order creation."""

    def test_crear_pedido_ok(self, client, client_headers, producto_factory):
        producto = producto_factory(precio_base=100.0, stock_cantidad=50)
        payload = {
            "forma_pago_codigo": "EFECTIVO",
            "descuento": 0.0,
            "costo_envio": 50.0,
            "notas": "Integration test",
            "detalle_pedidos": [
                {
                    "producto_id": producto.id,
                    "cantidad": 2,
                    "personalizacion": [],
                }
            ],
        }
        resp = client.post("/api/v1/pedidos/", json=payload, headers=client_headers)
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["estado_codigo"] == "PENDIENTE"
        assert data["subtotal"] == 200.0
        assert data["total"] == 250.0
        assert len(data["historial_estado"]) == 1
        assert data["historial_estado"][0]["estado_hasta"] == "PENDIENTE"
        assert data["historial_estado"][0]["estado_desde"] is None

    def test_crear_pedido_sin_stock(self, client, client_headers, producto_factory):
        producto = producto_factory(precio_base=100.0, stock_cantidad=1)
        payload = {
            "forma_pago_codigo": "EFECTIVO",
            "descuento": 0.0,
            "costo_envio": 50.0,
            "notas": "",
            "detalle_pedidos": [
                {
                    "producto_id": producto.id,
                    "cantidad": 5,
                    "personalizacion": [],
                }
            ],
        }
        resp = client.post("/api/v1/pedidos/", json=payload, headers=client_headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "No hay stock suficiente" in resp.json()["detail"]

    def test_crear_pedido_sin_items(self, client, client_headers):
        payload = {
            "forma_pago_codigo": "EFECTIVO",
            "descuento": 0.0,
            "costo_envio": 50.0,
            "notas": "",
            "detalle_pedidos": [],
        }
        resp = client.post("/api/v1/pedidos/", json=payload, headers=client_headers)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "detalle pedido como minimo" in resp.json()["detail"].lower()


class TestFSM:
    """PATCH /api/v1/pedidos/{pedido_id} — state machine transitions."""

    def test_avanzar_estado_valido_admin(
        self, client, admin_headers, producto_factory, pedido_factory
    ):
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        resp = client.patch(
            f"/api/v1/pedidos/{pedido.id}",
            json={"estado_bool": True},
            headers=admin_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["estado_codigo"] == "CONFIRMADO"

        resp = client.patch(
            f"/api/v1/pedidos/{pedido.id}",
            json={"estado_bool": True},
            headers=admin_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["estado_codigo"] == "EN_PREPARACION"

        resp = client.patch(
            f"/api/v1/pedidos/{pedido.id}",
            json={"estado_bool": True},
            headers=admin_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["estado_codigo"] == "ENTREGADO"

    def test_avanzar_estado_invalido_terminal(
        self, client, admin_headers, producto_factory, pedido_factory
    ):
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        for _ in range(3):
            resp = client.patch(
                f"/api/v1/pedidos/{pedido.id}",
                json={"estado_bool": True},
                headers=admin_headers,
            )
            assert resp.status_code == status.HTTP_200_OK

        resp = client.patch(
            f"/api/v1/pedidos/{pedido.id}",
            json={"estado_bool": True},
            headers=admin_headers,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "No se puede avanzar" in resp.json()["detail"]

    def test_avanzar_estado_valido_pedidos_role(
        self, client, admin_headers, pedidos_headers, producto_factory, pedido_factory
    ):
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        resp = client.patch(
            f"/api/v1/pedidos/{pedido.id}",
            json={"estado_bool": True},
            headers=admin_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["estado_codigo"] == "CONFIRMADO"

        resp = client.patch(
            f"/api/v1/pedidos/{pedido.id}",
            json={"estado_bool": True},
            headers=pedidos_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["estado_codigo"] == "EN_PREPARACION"

        resp = client.patch(
            f"/api/v1/pedidos/{pedido.id}",
            json={"estado_bool": True},
            headers=pedidos_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["estado_codigo"] == "ENTREGADO"

    def test_cancelar_pedido_propio(
        self, client, client_headers, producto_factory, pedido_factory
    ):
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        resp = client.patch(
            f"/api/v1/pedidos/{pedido.id}",
            json={"estado_bool": False, "motivo": "Ya no lo quiero"},
            headers=client_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["estado_codigo"] == "CANCELADO"


class TestObtenerPedidos:
    """GET endpoints for pedidos."""

    def test_obtener_pedidos_admin(
        self, client, admin_headers, producto_factory, pedido_factory
    ):
        p1 = producto_factory(nombre="Prod A")
        p2 = producto_factory(nombre="Prod B")
        pedido_factory(usuario_id=4, producto_id=p1.id)
        pedido_factory(usuario_id=4, producto_id=p2.id)

        resp = client.get("/api/v1/pedidos/", headers=admin_headers)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()) >= 2

    def test_obtener_pedido_por_id(
        self, client, client_headers, admin_headers, producto_factory, pedido_factory
    ):
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        resp = client.get(
            f"/api/v1/pedidos/{pedido.id}", headers=client_headers
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["id"] == pedido.id
        assert data["estado_codigo"] == "PENDIENTE"

        resp = client.get(
            f"/api/v1/pedidos/{pedido.id}", headers=admin_headers
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == pedido.id


class TestHistorial:
    """Audit trail verification."""

    def test_historial_append_only(
        self, client, admin_headers, producto_factory, pedido_factory
    ):
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        for _ in range(3):
            resp = client.patch(
                f"/api/v1/pedidos/{pedido.id}",
                json={"estado_bool": True},
                headers=admin_headers,
            )
            assert resp.status_code == status.HTTP_200_OK

        data = resp.json()
        historiales = sorted(data["historial_estado"], key=lambda h: h["id"])

        assert len(historiales) == 4

        assert historiales[0]["estado_desde"] is None
        assert historiales[0]["estado_hasta"] == "PENDIENTE"

        assert historiales[1]["estado_desde"] == "PENDIENTE"
        assert historiales[1]["estado_hasta"] == "CONFIRMADO"

        assert historiales[2]["estado_desde"] == "CONFIRMADO"
        assert historiales[2]["estado_hasta"] == "EN_PREPARACION"

        assert historiales[3]["estado_desde"] == "EN_PREPARACION"
        assert historiales[3]["estado_hasta"] == "ENTREGADO"


class TestBorradoLogico:
    """DELETE /api/v1/pedidos/{pedido_id} — soft delete."""

    def test_borrado_logico_pedido_admin(
        self, client, admin_headers, db_session, producto_factory, pedido_factory
    ):
        producto = producto_factory()
        pedido = pedido_factory(usuario_id=4, producto_id=producto.id)

        resp = client.delete(
            f"/api/v1/pedidos/{pedido.id}", headers=admin_headers
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        from app.modules.pedido.models import Pedido

        # Expirar caché de identidad: db_session tenía el objeto precargado
        # desde pedido_factory, y get() lo devolvería sin consultar la BD.
        db_session.expire_all()
        pedido_db = db_session.get(Pedido, pedido.id)
        assert pedido_db.activo is False
        assert pedido_db.deleted_at is not None
