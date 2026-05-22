from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.pedido.models import Pedido, HistorialEstadoPedido, EstadoPedido, FormaPago, DetallePedido
from app.modules.pedido.schemas import PedidoCreate, PedidoRead, PedidoHistorialUpdate, DetallePedidoCreate, DetallePedidoRead, HistorialEstadoPedidoRead
from app.modules.pedido.unit_of_work import PedidoUnitOfWork

class PedidoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: PedidoUnitOfWork, pedido_id: int) -> Pedido:
        pedido = uow.pedido.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido con id={pedido_id} no encontrado",
            )
        return pedido

    def _get_estado_or_404(self, uow: PedidoUnitOfWork, codigo: str) -> EstadoPedido:
        estado = uow.pedido.get_estado(codigo)
        if not estado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estado con id={codigo} no encontrado",
            )
        return estado
    
    def _get_forma_or_404(self, uow: PedidoUnitOfWork, codigo: str) -> FormaPago:
        forma_pago = uow.pedido.get_forma(codigo)
        if not forma_pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forma de pago con id={codigo} no encontrado",
            )
        return forma_pago

    def crear(self, data: PedidoCreate) -> PedidoRead:
        with PedidoUnitOfWork(self._session) as uow:
            
            self._get_forma_or_404(uow, data.forma_pago_codigo)
            estado = "PENDIENTE"

            pedido = Pedido(
                estado_codigo=estado,
                forma_pago_codigo=data.forma_pago_codigo.upper(),
                subtotal=data.subtotal,
                descuento=data.descuento,
                costo_envio=data.costo_envio,
                total=data.total,
                notas=data.notas,
            )
            if not data.detalle_pedidos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo se puede crear un pedido si tiene un detalle pedido como minimo",
                )
            
            uow.pedido.add(pedido)

            for depe_input in data.detalle_pedidos:
                producto = uow.producto.get_by_id(depe_input.producto_id)
                if not producto:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Producto con el id {depe_input.producto_id} no encontrado",
                    )
                if  depe_input.cantidad > producto.stock_cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"No hay stock suficiente en Producto {producto.nombre}",
                    )
                producto.stock_cantidad -= depe_input.cantidad
                subtotal = float(producto.precio_base) * float(depe_input.cantidad)
                detalle_pedido = DetallePedido(
                    pedido_id = pedido.id,
                    producto_id = depe_input.producto_id,
                    cantidad = depe_input.cantidad,
                    nombre_snapshot = producto.nombre,
                    precio_snapshot = producto.precio_base,
                    subtotal_snap = subtotal,
                    personalizacion = depe_input.personalizacion
                )
                uow.detalle_pedido.add(detalle_pedido)
            """
            historial = HistorialEstadoPedido(
                pedido_id= pedido.id,
                estado_desde=None,
                estado_hasta= estado,
                motivo= ""
            )
            uow.historial_estado_pedido.add(historial)
            """

            uow.flush()
            uow.refresh(pedido)

            result = PedidoRead.model_validate(pedido)
        return result
    
    def obtener_todos(self, offset: Optional[int] = 0, limit: Optional[int] = 100) -> list[PedidoRead]:
        with PedidoUnitOfWork(self._session) as uow:
            pedidos = uow.pedido.get_all(offset=offset, limit=limit)

            result = [PedidoRead.model_validate(p) for p in pedidos]
        return result
        
    def obtener_por_id(self, pedido_id: int) -> PedidoRead:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            result = PedidoRead.model_validate(pedido)
        return result
        
    def actualizar(self, pedido_id: int, data: PedidoHistorialUpdate) -> PedidoRead:
        with PedidoUnitOfWork(self._session) as uow:

            pedido = self._get_or_404(uow, pedido_id)
            estado = self._get_estado_or_404(uow, pedido.estado_codigo)
            nuevo_estado = None
            if not data.estado_bool:
                if estado.orden >=4:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No se puede cancelar un pedido en estado: {pedido.estado_codigo}",
                    )
                nuevo_estado = "CANCELADO"
            elif data.estado_bool:
                match pedido.estado_codigo:
                    case "PENDIENTE":
                        nuevo_estado = "CONFIRMADO"
                    case "CONFIRMADO":
                        nuevo_estado = "EN_PREPARACION"
                    case "EN_PREPARACION":
                        nuevo_estado = "EN_CAMINO"
                    case "EN_CAMINO":
                        nuevo_estado = "ENTREGADO"
                    case "ENTREGADO" | "CANCELADO":
                        raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No se puede avanzar un pedido que ya esta en estado: {pedido.estado_codigo}",
                    )

            historial = HistorialEstadoPedido(
                pedido_id= pedido.id,
                estado_desde= pedido.estado_codigo,
                estado_hasta= nuevo_estado,
                motivo= data.motivo
            )
            uow.historial_estado_pedido.add(historial)

            patch = data.model_dump(exclude_unset=True, exclude={"estado_bool", "motivo"})
            patch["estado_codigo"] = nuevo_estado

            for field, value in patch.items():
                setattr(pedido, field, value)

            uow.pedido.add(pedido)
            result = PedidoRead.model_validate(pedido)
        return result
