from sqlmodel import Session, select
from app.core.database import engine
from app.modules.pedido.models import EstadoPedido, FormaPago
from app.modules.producto.models import UnidadMedida
from app.modules.usuarios.models import Usuario, Rol, UsuarioRol
from app.core.security import hashear_password

def seed_unidad_medida(session:Session) -> None:
    unidades = [
        {"nombre":"kilogramo", "simbolo":"kg", "tipo":"masa"},
        {"nombre":"gramo", "simbolo":"g", "tipo":"masa"},
        {"nombre":"litro", "simbolo":"L", "tipo":"volumen"},
        {"nombre":"mililitro", "simbolo":"mL", "tipo":"volumen"},
        {"nombre":"pieza", "simbolo":"u", "tipo":"unidad"},
        {"nombre":"docena", "simbolo":"doc", "tipo":"unidad"},
        {"nombre":"metro cuadrado", "simbolo":"m²", "tipo":"area"},
    ]
    for data in unidades:
        statement = select(UnidadMedida).where(UnidadMedida.nombre == data["nombre"])
        existing = session.exec(statement).first()
        
        if not existing:
            session.add(UnidadMedida(**data))
            print(f"UnidadMedida creada: {data['nombre']}")
        else:
            print(f"UnidadMedida ya existe: {data['nombre']}")

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

def seed_roles(session: Session) -> None:
    roles = [
        {"codigo" : "ADMIN","nombre" : "Administrador", "descripcion" : "Acceso total sin restricciones"},
        {"codigo" : "STOCK","nombre" : "Gestor de Stock", "descripcion" : "Actualiza el stock y disponibilidad de los productos"},
        {"codigo" : "PEDIDOS","nombre" : "Gestor de Pedidos", "descripcion" : "Avanzar estados de pedidos"},
        {"codigo" : "CLIENT","nombre" : "Cliente", "descripcion" : "Navega la plataforma y gestiona sus datos"},
    ]
    for data in roles:
        existing = session.get(Rol, data["codigo"])
        if not existing:
            session.add(Rol(**data))
            print(f"Rol creado: {data['codigo']}")
        else:
            print(f"Rol ya existente: {data['codigo']}")

def seed_usuarios(session: Session) -> None:
    usuarios = [
        {"nombre": "Admin", "apellido": "Principal", "celular" : "1234567890", "email" : "admin@foodstore.com", "password_hash" : hashear_password("admin123")}
    ]
    for data in usuarios:
        existing = session.exec(
            select(Usuario).where(Usuario.email == data["email"])
        ).first()
        if not existing:
            rol_admin = session.get(Rol, "ADMIN")
            usuario = (Usuario(**data))
            session.add(usuario)
            session.flush()
            session.add(UsuarioRol(
                usuario_id = usuario.id,
                rol_codigo = "ADMIN", 
                asignado_por_id = None
            ))

def seed_all() -> None:
    with Session(engine) as session:
        seed_unidad_medida(session)
        seed_estados_pedido(session)
        seed_formas_pago(session)
        seed_roles(session)
        seed_usuarios(session)
        session.commit()
    print("Seeding finalizado con éxito.")