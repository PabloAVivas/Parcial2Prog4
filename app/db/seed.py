from sqlmodel import Session
from app.core.database import engine
from app.modules.pedido.models import EstadoPedido, FormaPago

def seed_estados_pedido(session: Session) -> None:
    estados = [
        {"codigo": "PENDIENTE", "descripcion": "Pedido creado, pago pendiente", "orden": 1, "es_terminal": False},
        {"codigo": "CONFIRMADO", "descripcion": "Pago procesado y confirmado", "orden": 2, "es_terminal": False},
        {"codigo": "EN_PREPARACION", "descripcion": "En preparacion, en cocina", "orden": 3, "es_terminal": False},
        {"codigo": "EN_CAMINO", "descripcion": "Despachado al cliente", "orden": 4, "es_terminal": False},
        {"codigo": "ENTREGADO", "descripcion": "Entrega confirmada", "orden": 5, "es_terminal": True},
        {"codigo": "CANCELADO", "descripcion": "Pedido cancelado", "orden": 6, "es_terminal": True},
    ]
    for data in estados:
        existing = session.get(EstadoPedido, data["codigo"])
        if not existing:
            session.add(EstadoPedido(**data))
            print(f"EstadoPedido creado: {data['codigo']}")
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
            print(f"FormaPago creada: {data['codigo']}")
        else:
            print(f"FormaPago ya existe: {data['codigo']}")

def seed_all() -> None:
    """Función principal para ejecutar todos los seeds bajo una misma sesión"""
    print("Iniciando el seeding de datos...")
    with Session(engine) as session:
        seed_estados_pedido(session)
        seed_formas_pago(session)
        session.commit()
    print("Seeding finalizado con éxito.")