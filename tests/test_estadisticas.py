from datetime import datetime, timezone

from sqlmodel import select

from app.modules.pedido.models import Pedido, HistorialEstadoPedido
from app.modules.usuarios.models import Usuario


def _get_admin_user(db_session):
    return db_session.exec(
        select(Usuario).where(Usuario.email == "admin@foodstore.com")
    ).first()


def _advance_pedido_to(db_session, pedido_id, target_estado, from_estado=None):
    pedido = db_session.get(Pedido, pedido_id)
    old_estado = pedido.estado_codigo
    pedido.estado_codigo = target_estado
    historial = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde=from_estado or old_estado,
        estado_hasta=target_estado,
    )
    db_session.add(historial)
    db_session.commit()


def _set_pedido_created_at(db_session, pedido_id, dt):
    pedido = db_session.get(Pedido, pedido_id)
    pedido.created_at = dt
    db_session.commit()


class TestResumen:
    def test_resumen_sin_pedidos(self, client, admin_headers):
        resp = client.get("/api/v1/estadisticas/resumen", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ventas_hoy"] == 0
        assert data["pedidos_activos"] == 0

    def test_resumen_con_pedidos(
        self, client, admin_headers, db_session, producto_factory, pedido_factory
    ):
        admin_user = _get_admin_user(db_session)
        prod = producto_factory()

        entregado = pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)
        _advance_pedido_to(db_session, entregado.id, "ENTREGADO")

        pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)

        en_prep = pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)
        _advance_pedido_to(db_session, en_prep.id, "EN_PREPARACION")

        resp = client.get("/api/v1/estadisticas/resumen", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ventas_hoy"] == 1
        assert data["pedidos_activos"] == 2


class TestPedidosPorEstado:
    def test_pedidos_por_estado(
        self, client, admin_headers, db_session, producto_factory, pedido_factory
    ):
        admin_user = _get_admin_user(db_session)
        prod = producto_factory()

        p1 = pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)
        _advance_pedido_to(db_session, p1.id, "ENTREGADO")

        p2 = pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)
        _advance_pedido_to(db_session, p2.id, "CANCELADO")

        pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)

        resp = client.get(
            "/api/v1/estadisticas/pedidos-por-estado", headers=admin_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        counts = {item["estado_codigo"]: item["cantidad"] for item in data}
        assert counts["ENTREGADO"] == 1
        assert counts["CANCELADO"] == 1
        assert counts["PENDIENTE"] == 1


class TestProductosTop:
    def test_productos_top(
        self, client, admin_headers, db_session, producto_factory, pedido_factory
    ):
        admin_user = _get_admin_user(db_session)
        barato = producto_factory(nombre="Barato", precio_base=50.0)
        caro = producto_factory(nombre="Caro", precio_base=200.0)

        pedido_factory(usuario_id=admin_user.id, producto_id=barato.id, cantidad=1)
        pedido_factory(usuario_id=admin_user.id, producto_id=caro.id, cantidad=3)

        resp = client.get(
            "/api/v1/estadisticas/productos-top/5", headers=admin_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["nombre"] == "Caro"
        assert data[0]["total_ingresos"] == 600.0
        assert data[0]["cantidad_vendida"] == 3
        assert data[1]["nombre"] == "Barato"
        assert data[1]["total_ingresos"] == 50.0
        assert data[1]["cantidad_vendida"] == 1


class TestIngresos:
    def test_ingresos_por_forma_pago(
        self, client, admin_headers, db_session, producto_factory, pedido_factory
    ):
        admin_user = _get_admin_user(db_session)
        prod = producto_factory(precio_base=100.0)

        p1 = pedido_factory(
            usuario_id=admin_user.id,
            producto_id=prod.id,
            forma_pago_codigo="EFECTIVO",
        )
        _advance_pedido_to(db_session, p1.id, "ENTREGADO")

        p2 = pedido_factory(
            usuario_id=admin_user.id,
            producto_id=prod.id,
            forma_pago_codigo="MERCADOPAGO",
        )
        _advance_pedido_to(db_session, p2.id, "ENTREGADO")

        resp = client.get(
            "/api/v1/estadisticas/ingresos?desde=2024-01-01&hasta=2030-12-31",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        ingresos = {item["forma_pago_codigo"]: item["cantidad"] for item in data}
        assert ingresos["EFECTIVO"] == 250.0
        assert ingresos["MERCADOPAGO"] == 250.0


class TestAuthorization:
    def test_estadisticas_sin_admin(self, client, client_headers):
        resp = client.get("/api/v1/estadisticas/resumen", headers=client_headers)
        assert resp.status_code == 403


class TestCanceladosNoSuman:
    def test_cancelados_no_suman(
        self, client, admin_headers, db_session, producto_factory, pedido_factory
    ):
        admin_user = _get_admin_user(db_session)
        prod = producto_factory()

        cancelado = pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)
        _advance_pedido_to(db_session, cancelado.id, "CANCELADO")

        entregado = pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)
        _advance_pedido_to(db_session, entregado.id, "ENTREGADO")

        resp = client.get(
            "/api/v1/estadisticas/pedidos-por-estado", headers=admin_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        counts = {item["estado_codigo"]: item["cantidad"] for item in data}
        assert counts["CANCELADO"] == 1
        assert counts["ENTREGADO"] == 1

        resp = client.get("/api/v1/estadisticas/resumen", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ventas_hoy"] == 1
        assert data["pedidos_activos"] == 0


class TestVentasPeriodo:
    def test_ventas_periodo(
        self, client, admin_headers, db_session, producto_factory, pedido_factory
    ):
        admin_user = _get_admin_user(db_session)
        prod = producto_factory()

        p1 = pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)
        _advance_pedido_to(db_session, p1.id, "ENTREGADO")
        _set_pedido_created_at(
            db_session, p1.id, datetime(2024, 6, 15, tzinfo=timezone.utc)
        )

        p2 = pedido_factory(usuario_id=admin_user.id, producto_id=prod.id)
        _advance_pedido_to(db_session, p2.id, "ENTREGADO")
        _set_pedido_created_at(
            db_session, p2.id, datetime(2024, 6, 16, tzinfo=timezone.utc)
        )

        resp = client.get(
            "/api/v1/estadisticas/ventas?desde=2024-01-01&hasta=2030-12-31&agrupacion=day",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2
        for entry in data:
            assert entry["ventas_totales"] > 0
