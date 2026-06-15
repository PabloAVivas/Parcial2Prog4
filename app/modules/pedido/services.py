import logging
from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone
from app.modules.pedido.models import Pedido, HistorialEstadoPedido, EstadoPedido, FormaPago, DetallePedido
from app.modules.producto.models import Producto
from app.modules.ingrediente.models import Ingrediente
from app.modules.usuarios.models import Usuario
from app.modules.pedido.schemas import PedidoCreate, PedidoRead, PedidoHistorialUpdate, DetallePedidoCreate, DetallePedidoRead, HistorialEstadoPedidoRead
from app.modules.pedido.unit_of_work import PedidoUnitOfWork

logger = logging.getLogger("app.modules.pedidos.service")

EVENTOS_WS = {
    "PENDIENTE":  "NUEVO_PEDIDO",
    "CONFIRMADO": "PEDIDO_CONFIRMADO",
    "EN_PREPARACION": "PEDIDO_EN_PREPARACION",
    "ENTREGADO":  "PEDIDO_ENTREGADO",
    "CANCELADO":  "PEDIDO_CANCELADO",
}

ROLES_POR_TRANSICION = {
    "PENDIENTE":  ["PEDIDOS", "ADMIN"],
    "CONFIRMADO": ["PEDIDOS", "ADMIN"],
    "EN_PREPARACION": ["PEDIDOS", "ADMIN"],
    "ENTREGADO":  ["PEDIDOS", "ADMIN"],
    "CANCELADO":  ["PEDIDOS", "ADMIN"],
}

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
        producto = uow.producto.get_by_id_categorias_ingredientes(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con el id {producto_id} no encontrado",
            )
        return producto
    
    def _get_ingrediente_or_404(self, uow:PedidoUnitOfWork, ingrediente_id: int) -> Ingrediente:
        ingrediente = uow.ingrediente.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con el id {ingrediente_id} no encontrado",
            )
        return ingrediente
    
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

    async def crear(self, data: PedidoCreate, usuario_actual_id: int) -> PedidoRead:
        result: PedidoRead | None = None
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
                        status_code=status.HTTP_403_FORBIDDEN,
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
                
                if producto.ingredientes is not None:
                    for ingrediente_producto in producto.ingrediente_links:
                        if ingrediente_producto.ingrediente_id not in depe_input.personalizacion:
                            ingrediente = self._get_ingrediente_or_404(uow, ingrediente_producto.ingrediente_id)
                            cantidad_restar = ingrediente_producto.cantidad * depe_input.cantidad
                            if cantidad_restar > ingrediente.stock_cantidad:
                                raise HTTPException(
                                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail=f"No hay stock suficiente en Ingrediente {ingrediente.nombre}",
                            )
                            ingrediente.stock_cantidad -= cantidad_restar

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

        await self._emit_ws_events(result.id, estado, result)
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
        
    async def actualizar(self, pedido_id: int, data: PedidoHistorialUpdate, usuario_actual_id: int) -> PedidoRead:
        result: PedidoRead | None = None
        nuevo_estado: str = ""
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
                    if producto.ingredientes is not None:
                        for ingrediente_producto in producto.ingrediente_links:
                            if ingrediente_producto.ingrediente_id not in depe.personalizacion:
                                ingrediente = self._get_ingrediente_or_404(uow, ingrediente_producto.ingrediente_id)
                                cantidad_sumar = ingrediente_producto.cantidad * depe.cantidad
                                ingrediente.stock_cantidad += cantidad_sumar

            elif data.estado_bool and "ADMIN" in roles:
                match pedido.estado_codigo:
                    case "PENDIENTE":
                        nuevo_estado = "CONFIRMADO"
                    case "CONFIRMADO":
                        nuevo_estado = "EN_PREPARACION"
                    case "EN_PREPARACION":
                        nuevo_estado = "ENTREGADO"
                    case "ENTREGADO" | "CANCELADO":
                        raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No se puede avanzar un pedido que ya esta en estado: {pedido.estado_codigo}",
                    )
            elif data.estado_bool and "PEDIDOS" in roles:
                match pedido.estado_codigo:
                    case "CONFIRMADO":
                        nuevo_estado = "EN_PREPARACION"
                    case "EN_PREPARACION":
                        nuevo_estado = "ENTREGADO"
                    case "PENDIENTE" | "ENTREGADO" | "CANCELADO":
                        raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No se puede avanzar un pedido que ya esta en estado: {pedido.estado_codigo} o no tienes los permisos suficientes",
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

            logger.info(
                f"AUDITORÍA FSM: Usuario {usuario.nombre} "
                f"(ID: {usuario.id}, Rol: {[role.codigo for role in usuario.roles]}) "
                f"avanzó pedido {pedido_id} de '{pedido.estado_codigo}' a '{nuevo_estado}'"
            )

            pedido.estado_codigo = nuevo_estado
            uow.pedido.add(pedido)
            uow.flush()
            pedido_actualizado = uow.pedido.get_by_id_pedido(pedido.id)
            result = PedidoRead.model_validate(pedido_actualizado)
        
        await self._emit_ws_events(pedido_id, nuevo_estado, result)
        return result

    def borrado_logico(self, pedido_id: int) -> None:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            pedido.activo = False
            pedido.deleted_at = datetime.now(timezone.utc)
            uow.pedido.add(pedido)

    def autorizacion_pedido(self, pedido_id: int, usuario_id: int) -> bool:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = uow.pedido.get_by_id_pedido(pedido_id)
            if not pedido or pedido.usuario_id != usuario_id:
                return False
            return True
    
    async def _emit_ws_events(self, pedido_id: int, destino: str, result: PedidoRead) -> None:
        from app.core.websocket import manager
        event_type = EVENTOS_WS.get(destino)
        if not event_type:
            return
        data = result.model_dump()
        await manager.broadcast_to_order(pedido_id, event_type, data)
        roles_a_notificar = ROLES_POR_TRANSICION.get(destino, [])
        if roles_a_notificar:
            await manager.broadcast_to_roles(roles_a_notificar, event_type, data)

        logger.info(
            f"WS emitido: {event_type} | pedido={pedido_id} | "
            f"roles={roles_a_notificar} | rooms_activas={manager.get_rooms_info()}"
        )