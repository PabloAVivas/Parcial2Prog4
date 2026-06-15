from sqlmodel import Session, select, func, delete
from app.core.repository import BaseRepository
from sqlalchemy.orm import selectinload
from app.modules.pedido.models import Pedido, HistorialEstadoPedido, DetallePedido, FormaPago, EstadoPedido
from app.modules.producto.models import Producto
from datetime import date

class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)

    def get_activo(self, offset: int = 0, limit: int = 100) -> list[Pedido]:
        query = select(Pedido).where(Pedido.activo == True)
        
        query = query.options(
            selectinload(Pedido.detalle_pedidos),
            selectinload(Pedido.historial_estado),
            selectinload(Pedido.usuario),
            selectinload(Pedido.direccion)
        )
            
        query = query.order_by(Pedido.id)
        
        return list(
            self.session.exec(query.offset(offset).limit(limit)).all()
        )
    
    def get_by_id_pedido(self, pedido_id: int) -> Pedido:
        query = select(Pedido).where(Pedido.id == pedido_id).options(
            selectinload(Pedido.detalle_pedidos),
            selectinload(Pedido.historial_estado),
            selectinload(Pedido.usuario),
            selectinload(Pedido.direccion)
        )
        return self.session.exec(query).first()

    def get_estado(self, codigo:str) -> EstadoPedido:
        return self.session.get(EstadoPedido, codigo.upper())
    
    def get_forma(self, codigo:str) -> FormaPago:
        return self.session.get(FormaPago, codigo.upper())
    
    def get_pedidos_by_usuario_id(self, usuario_id: int) -> list[Pedido]:
        query = select(Pedido).where(Pedido.usuario_id == usuario_id)
        query = query.options(
            selectinload(Pedido.detalle_pedidos),
            selectinload(Pedido.historial_estado),
            selectinload(Pedido.usuario),
            selectinload(Pedido.direccion)
        )
        query = query.order_by(Pedido.id)
        return self.session.exec(query).all()
    
    def get_ventas_periodo(self, desde:date, hasta: date, agrupacion: str) -> list[dict]:
        fecha_grupo = func.date_trunc(agrupacion, Pedido.created_at).label("fecha_grupo")
        query = (
            select(
                fecha_grupo,
                func.count(Pedido.id).label("cantidad_pedidos"),
                func.sum(Pedido.total).label("ventas_totales")
            )
            .where(
                Pedido.created_at >= desde,
                Pedido.created_at <= hasta,
                Pedido.estado_codigo == "ENTREGADO" 
            )
            .group_by(fecha_grupo)
            .order_by(fecha_grupo.asc())
        )
        resultados = self.session.exec(query).all()
        return [row._asdict() for row in resultados]
    
    def get_pedidos_por_estado(self) -> list[dict]:
        query = (
            select(
                Pedido.estado_codigo,
                func.count(Pedido.id).label("cantidad")
            )
            .group_by(Pedido.estado_codigo)
        )
        resultados = self.session.exec(query).all()
        return [row._asdict() for row in resultados]
    
    def get_ingresos_por_forma_pago(self, desde:date, hasta: date) -> list[dict]:
        query = (
            select(
                Pedido.forma_pago_codigo,
                func.sum(Pedido.total).label("cantidad")
            )
            .where(
                Pedido.created_at >= desde,
                Pedido.created_at <= hasta,
                Pedido.estado_codigo == "ENTREGADO" 
            )
            .group_by(Pedido.forma_pago_codigo)
        )
        resultados = self.session.exec(query).all()
        return [row._asdict() for row in resultados]
    
    def get_ventas_hoy(self, desde:date, hasta: date) -> list[dict]:
        query = (
            select(
                func.count(Pedido.id).label("contar_ventas"),
                func.sum(Pedido.total).label("cantidad")
            )
            .where(
                Pedido.created_at >= desde,
                Pedido.created_at <= hasta,
                Pedido.estado_codigo == "ENTREGADO"
            )
        )
        resultados = self.session.exec(query).all()
        return [row._asdict() for row in resultados]
    
    def get_pedidos_activo(self, desde:date, hasta: date) -> int:
        query = (
            select(
                func.count(Pedido.id).label("contar_ventas")
            )
            .where(
                Pedido.created_at >= desde,
                Pedido.created_at <= hasta,
                Pedido.estado_codigo.notin_(["ENTREGADO", "CANCELADO"])
            )
        )
        return self.session.exec(query).scalar()

class DetallePedidoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, instance: DetallePedido) -> DetallePedido:
        self.session.add(instance)
        return instance
    
    def get_productos_top(self, limit: int) -> list[dict]:
        query = (
            select(
                Producto.nombre,
                func.sum(DetallePedido.subtotal_snap).label("total_ingresos"),
                func.sum(DetallePedido.cantidad).label("cantidad_vendida")
            )
            .join(DetallePedido, DetallePedido.producto_id == Producto.id)
            .group_by(Producto.nombre)
            .order_by(func.sum(DetallePedido.subtotal_snap).desc())
            .limit(limit)
        )

        resultados = self.session.exec(query).all()
        return [row._asdict() for row in resultados]

class HistorialEstadoPedidoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, instance: HistorialEstadoPedido) -> HistorialEstadoPedido:
        self.session.add(instance)
        return instance