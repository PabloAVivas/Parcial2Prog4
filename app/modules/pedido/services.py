from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone
from app.modules.pedido.models import Pedido, HistorialEstadoPedido, EstadoPedido, FormaPago, DetallePedido
from app.modules.producto.models import Producto
from app.modules.usuarios.models import Usuario
from app.modules.pedido.schemas import PedidoCreate, PedidoRead, PedidoHistorialUpdate, DetallePedidoCreate, DetallePedidoRead, HistorialEstadoPedidoRead
from app.modules.pedido.unit_of_work import PedidoUnitOfWork

class PedidoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: PedidoUnitOfWork, pedido_id: int) -> Pedido:
        pedido = uow.pedido.get_by_id_pedido(pedido_id)
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
    
    def _get_producto_or_404(self, uow:PedidoUnitOfWork, producto_id: int) -> Producto:
        producto = uow.producto.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con el id {producto_id} no encontrado",
            )
        return producto
    
    def _get_usuario_or_404(self, uow:PedidoUnitOfWork, usuario_id: int) -> Usuario:
        usuario = uow.usuario.get_by_id_usuario(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con el id {usuario_id} no encontrado",
            )
        return usuario

    def subtotal_producto(self, precio:float, cantidad:int) -> float:
        subtotal = precio * cantidad
        return subtotal

    def crear(self, data: PedidoCreate, usuario_actual_id: int) -> PedidoRead:
        with PedidoUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(usuario_actual_id)
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Usuario con el id {usuario_actual_id} no encontrado",
                )
            if data.direccion_id is not None:
                direccion = uow.direccion_entrega.get_by_id(data.direccion_id)
                if not direccion:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Direccion con el id {data.direccion_id} no encontrado",
                    )
                if direccion.usuario_id != usuario_actual_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="No tienes los permisos para realizar esta accion"
                    )

            if not data.detalle_pedidos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo se puede crear un pedido si tiene un detalle pedido como minimo",
                )

            subtotal_pedido = 0
            for dp in data.detalle_pedidos:
                producto = self._get_producto_or_404(uow, dp.producto_id)
                subtotal_pedido += self.subtotal_producto(producto.precio_base, dp.cantidad)

            self._get_forma_or_404(uow, data.forma_pago_codigo)
            estado = "PENDIENTE"

            total = subtotal_pedido - data.descuento + data.costo_envio

            pedido = Pedido(
                usuario_id= usuario.id,
                direccion_id= data.direccion_id,
                estado_codigo=estado,
                forma_pago_codigo=data.forma_pago_codigo.upper(),
                subtotal=subtotal_pedido,
                descuento=data.descuento,
                costo_envio=data.costo_envio,
                total=total,
                notas=data.notas,
            )
            
            uow.pedido.add(pedido)

            for depe_input in data.detalle_pedidos:
                producto = self._get_producto_or_404(uow, depe_input.producto_id)

                if  depe_input.cantidad > producto.stock_cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"No hay stock suficiente en Producto {producto.nombre}",
                    )
                
                producto.stock_cantidad -= depe_input.cantidad
                subtotal = self.subtotal_producto(producto.precio_base, depe_input.cantidad)

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
            
            historial = HistorialEstadoPedido(
                pedido_id= pedido.id,
                estado_hasta= estado,
            )
            uow.historial_estado_pedido.add(historial)
            
            uow.flush()
            pedido_creado = uow.pedido.get_by_id_pedido(pedido.id)

            result = PedidoRead.model_validate(pedido_creado)
        return result
    
    def obtener_todos(self, offset: Optional[int] = 0, limit: Optional[int] = 100) -> list[PedidoRead]:
        with PedidoUnitOfWork(self._session) as uow:
            pedidos = uow.pedido.get_activo(offset=offset, limit=limit)

            result = [PedidoRead.model_validate(p) for p in pedidos]
        return result
        
    def obtener_por_id(self, pedido_id: int, usuario_actual_id: int) -> PedidoRead:
        with PedidoUnitOfWork(self._session) as uow:
            usuario = self._get_usuario_or_404(uow, usuario_actual_id)
            roles = [rol.codigo for rol in usuario.roles]
            pedido = self._get_or_404(uow, pedido_id)
            if pedido.usuario_id != usuario_actual_id and ("ADMIN" not in roles and "PEDIDOS" not in roles):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes los permisos para acceder a esta funcionalidad"
                )
            result = PedidoRead.model_validate(pedido)
        return result
    
    def obtener_pedidos_por_usuario(self, usuario_id: int, usuario_actual_id: int) -> list[PedidoRead]:
        with PedidoUnitOfWork(self._session) as uow:
            usuario = self._get_usuario_or_404(uow, usuario_actual_id)
            roles = [rol.codigo for rol in usuario.roles]
            if usuario.id != usuario_id and "ADMIN" not in roles:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes los permisos para acceder a esta funcionalidad"
                )
            pedidos = uow.pedido.get_pedidos_by_usuario_id(usuario_id)
            result = [PedidoRead.model_validate(p) for p in pedidos]
        return result
        
    def actualizar(self, pedido_id: int, data: PedidoHistorialUpdate, usuario_actual_id: int) -> PedidoRead:
        with PedidoUnitOfWork(self._session) as uow:

            pedido = self._get_or_404(uow, pedido_id)
            usuario = self._get_usuario_or_404(uow, usuario_actual_id)
            roles = [rol.codigo for rol in usuario.roles]

            if pedido.usuario_id != usuario_actual_id and ("ADMIN" not in roles and "PEDIDOS" not in roles):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes los permisos para acceder a esta funcionalidad"
                )

            estado = self._get_estado_or_404(uow, pedido.estado_codigo)
            nuevo_estado = None
            if not data.estado_bool:
                if estado.orden >=4 or ("ADMIN" not in roles and "PEDIDOS" not in roles and estado.orden >=3):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No se puede cancelar un pedido en estado: {pedido.estado_codigo}",
                    )
                nuevo_estado = "CANCELADO"
                for depe in pedido.detalle_pedidos:
                    producto = self._get_producto_or_404(uow, depe.producto_id)
                    producto.stock_cantidad += depe.cantidad

            elif data.estado_bool and ("ADMIN" in roles or "PEDIDOS" in roles):
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
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes los permisos para acceder a esta funcionalidad"
                )
            
            historial = HistorialEstadoPedido(
                pedido_id= pedido.id,
                estado_desde= pedido.estado_codigo,
                estado_hasta= nuevo_estado,
                motivo= data.motivo
            )
            uow.historial_estado_pedido.add(historial)

            pedido.estado_codigo = nuevo_estado
            uow.pedido.add(pedido)
            uow.flush()
            pedido_actualizado = uow.pedido.get_by_id_pedido(pedido.id)
            result = PedidoRead.model_validate(pedido_actualizado)
        return result

    def borrado_logico(self, pedido_id: int) -> None:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            pedido.activo = False
            pedido.deleted_at = datetime.now(timezone.utc)
            uow.pedido.add(pedido)