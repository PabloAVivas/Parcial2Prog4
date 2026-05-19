from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.pedido.models import Pedido, HistorialEstadoPedido, EstadoPedido, FormaPago, DetallePedido
from app.modules.pedido.schemas import PedidoCreate, PedidoRead, PedidoUpdate, DetallePedidoCreate, DetallePedidoRead, HistorialEstadoPedidoCreate, HistorialEstadoPedidoRead
from datetime import datetime, timezone
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

    def _map_to_read(self, pedido: Pedido) -> PedidoRead:
        detalles_pedido = [
            DetallePedidoRead(
                pedido_id=link.pedido_id,
                producto_id=link.product_id,
                cantidad=link.cantidad,
                nombre_snapshot=link.nombre_snapshot,
                precio_snapshot=link.precio_snapshot,
                subtotal_snap=link.subtotal_snap,
                personalizacion=link.personalizacion,
                created_at=link.created_at
            ) for link in pedido.detalle_pedidos
        ]

        if not pedido.historial_estado:
            res_dict = pedido.model_dump()
            res_dict["detalle_pedidos"] = detalles_pedido

            return PedidoRead(**res_dict)
        
        historiales_estados = [
            HistorialEstadoPedidoRead(
                id=link.id,
                pedido_id=link.pedido_id,
                estado_desde=link.estado_desde,
                estado_hasta=link.estado_hasta,
                motivo=link.motivo,
                created_at=link.created_at
            ) for link in pedido.historial_estado
        ]
        res_dict = pedido.model_dump()
        res_dict["detalle_pedidos"] = detalles_pedido
        res_dict["historial_estado"] = historiales_estados

        return PedidoRead(**res_dict)

    def crear(self, data: PedidoCreate) -> PedidoRead:
        with PedidoUnitOfWork(self._session) as uow:
            
            self._get_forma_or_404(uow, data.forma_pago_codigo)
            estado = "PENDIENTE"

            pedido = Pedido(
                estado_codigo=estado,
                forma_pago_codigo=data.forma_pago_codigo,
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
                        status_code=404,
                        detail=f"Producto {depe_input.producto_id} no encontrado",
                    )
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
                uow.pedido.add(detalle_pedido)

            uow.flush()
            uow.refresh(pedido)

            return self._map_to_read(pedido)
    
    def mostrar_todos(self, offset: Optional[int] = 0, limit: Optional[int] = 100) -> list[PedidoRead]:
        with PedidoUnitOfWork(self._session) as uow:
            pedidos = uow.pedido.get_all(offset=offset, limit=limit)

            return [self._map_to_read(p) for p in pedidos]
        
    def actualizar(self, pedido_id: int, data: PedidoUpdate, motivo_historial: Optional[str] = None) -> PedidoRead:
        with PedidoUnitOfWork(self._session) as uow:

            pedido = self._get_or_404(uow, pedido_id)
            self._get_estado_or_404(uow, data.estado_codigo)

            historial = HistorialEstadoPedido(
                pedido_id= pedido.id,
                estado_desde= pedido.estado_codigo,
                estado_hasta= data.estado_codigo,
                motivo= motivo_historial
            )
            uow.pedido.add(historial)

            patch = data.model_dump(exclude_unset=True)

            for field, value in patch.items():
                setattr(pedido, field, value)
