from sqlmodel import Session
from app.modules.pedido.models import EstadoPedido, FormaPago

def seed_estados_pedido(session: Session) -> None:
    estados = [
        {"codigos": "PENDINETE", "descripcion": "Pedido creado, pago pendiente", "orden":1, "es_terminal": False},
        {"codigos": "CONFIRMADO", "descripcion": "Pago procesado y confirmado", "orden":2, "es_terminal": False},
        {"codigos": "EN_PREPARACION", "descripcion": "En preparacion, en concina", "orden":3, "es_terminal": False},
        {"codigos": "EN_CAMINO", "descripcion": "Despachado al cliente", "orden":4, "es_terminal": False},
        {"codigos": "ENTREGADO", "descripcion": "Entrega confirmada", "orden":5, "es_terminal": True},
        {"codigos": "CANCELADO", "descripcion": "Pedido cancelado", "orden":6, "es_terminal": True},
    ]
    for data in estados:
        existing = session.get(EstadoPedido, data["codigo"])
        if not existing:
            session.add(EstadoPedido(**data))
            print(f"EstadoPedido: {data['codigo']}")
        else:
            print(f"EstadoPedido ya existe: {data['codigo']}")

def seed_formas_pago(session: Session) -> None:
    formas = [
        {"codigo": "MERCADOPAGO", "descripcion": "MercadoPago - Checkout API", "habilitado": True},
        {"codigo": "EFECTIVO", "descripcion": "Efectivo - retiro en local", "habilitado": True},
        {"codigo": "TRANSFERENCIA", "descripcion": "Transferencia bancaria", "habilitado": True},
    ]
    for data in formas:
        existing = session.get(FormaPago, data["codigo"])
        if not existing:
            session.add(FormaPago(**data))
            print(f"FormaPago: {data['codigo']}")
        else:
            print(f"FormaPago ya existe: {data['codigo']}")