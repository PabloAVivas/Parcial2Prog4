from datetime import timezone, datetime
from sqlmodel import Session
from fastapi import HTTPException, status
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.usuarios.models import Usuario, DireccionEntrega, UsuarioRol, Rol
from typing import Optional
from app.modules.usuarios.schemas import UsuarioRead, UsuarioUpdate, DireccionEntregaCreate, DireccionEntregaRead, DireccionEntregaUpdate, AdministrarRol, UsuarioPaginadoResponse

class UsuarioService:
    def __init__(self, session: Session):
        self._session = session

    def _get_or_404(self, uow:UsuarioUnitOfWork, usuario_id:int) -> Usuario:
        usuario = uow.usuario.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id={usuario_id} no encontrado",
            )
        return usuario

    def actualizar_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate, usuario_actual_id: int) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(usuario_id)
            usuario_actual = uow.usuario.get_by_id(usuario_actual_id)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            
            if usuario.id != usuario_actual.id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes permisos para realizar esta accion")

            usuario_actualizado = usuario_data.model_dump(exclude_unset=True)

            for field, value in usuario_actualizado.items():
                setattr(usuario, field, value)
            uow.usuario.add(usuario)

            usuario_actualizado_completo = uow.usuario.get_by_id_usuario(usuario.id)
            return UsuarioRead.model_validate(usuario_actualizado_completo)
    
    def obtener_usuarios(self) -> list[UsuarioRead]:
        with UsuarioUnitOfWork(self._session) as uow:
            usuarios = uow.usuario.get_activo()
            return [UsuarioRead.model_validate(u) for u in usuarios]

    def obtener_usuarios_admin(self, offset: int = 0, limit: int = 100, rol_codigo: Optional[str] = None) -> UsuarioPaginadoResponse:
        with UsuarioUnitOfWork(self._session) as uow:
            usuarios = uow.usuario.get_activo_paginado(offset=offset, limit=limit, rol_codigo=rol_codigo)
            total = uow.usuario.count_activo(rol_codigo=rol_codigo)
            return UsuarioPaginadoResponse(
                total=total,
                data=[UsuarioRead.model_validate(u) for u in usuarios]
            )

    def obtener_usuario_por_id(self, usuario_id: int, usuario_actual_id: int) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario_actual = self._get_or_404(uow, usuario_actual_id)
            roles = [rol.codigo for rol in usuario_actual.roles]
            usuario = self._get_or_404(uow, usuario_id)
           
            if usuario.id != usuario_actual.id and "ADMIN" not in roles:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usted no tiene los permisos para realizar esta accion")

            return UsuarioRead.model_validate(usuario)
    
    def crear_direccion_entrega(self, direccion_data: DireccionEntregaCreate, usuario_id: int) -> DireccionEntregaRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = self._get_or_404(uow, usuario_id)
            if usuario.id != usuario_id: 
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes permisos para acceder a este recurso"
                )
            
            for direccion in usuario.direcciones:
                if direccion.linea1 == direccion_data.linea1 and direccion.linea2 == direccion_data.linea2:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta direccion ya se encuentra registrada")

                if direccion.es_principal and direccion_data.es_principal:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una direccion principal para este usuario")
            
            direccion_nueva =DireccionEntrega(**direccion_data.model_dump(), usuario_id=usuario_id)
            uow.direccion_entrega.add(direccion_nueva)

            return DireccionEntregaRead.model_validate(direccion_nueva)
    
    def obtener_direcciones_entrega(self, usuario_id: int, usuario_actual_id: int) -> list[DireccionEntregaRead]:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario_actual = uow.usuario.get_by_id(usuario_actual_id)
            usuario = uow.usuario.get_by_id(usuario_id)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            
            if usuario_actual.id != usuario.id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes permisos para acceder a este recurso")

            direcciones = uow.direccion_entrega.get_direcciones_by_usuario_id(usuario_id)
            lista_direcciones = [DireccionEntregaRead.model_validate(direccion) for direccion in direcciones]
            return lista_direcciones

    def actualizar_direccion_entrega(self, direccion_id: int, direccion_data: DireccionEntregaUpdate, usuario_id: int) -> DireccionEntregaRead:
        with UsuarioUnitOfWork(self._session) as uow:
            direccion = uow.direccion_entrega.get_by_id(direccion_id)
            if not direccion:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada")
            
            if direccion.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes los permisos para acceder a esta funcionalidad"
                )

            hay_principal = uow.direccion_entrega.get_es_principal(direccion.usuario_id)
            if hay_principal and direccion_data.es_principal:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una direccion principal para este usuario")
            
            direccion_actualizada = direccion_data.model_dump(exclude_unset=True)
            for field, value in direccion_actualizada.items():
                setattr(direccion, field, value)

            uow.direccion_entrega.add(direccion)

            return DireccionEntregaRead.model_validate(direccion)
        
    def marcar_direccion_principal(self, direccion_id: int, usuario_id: int) -> DireccionEntregaRead:
        with UsuarioUnitOfWork(self._session) as uow:
            direccion = uow.direccion_entrega.get_by_id(direccion_id)
            if not direccion:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada")

            if direccion.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes los permisos para acceder a esta funcionalidad"
                )

            current_principal = uow.direccion_entrega.get_es_principal(direccion.usuario_id)
            if current_principal and current_principal.id != direccion.id:
                current_principal.es_principal = False
                uow.direccion_entrega.add(current_principal)

            direccion.es_principal = True
            uow.direccion_entrega.add(direccion)

            return DireccionEntregaRead.model_validate(direccion)

    def eliminar_direccion_entrega(self, direccion_id: int, usuario_id: int) -> None:
        with UsuarioUnitOfWork(self._session) as uow:
            direccion = uow.direccion_entrega.get_by_id(direccion_id)
            if not direccion:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada")
            
            if direccion.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes los permisos para realizar esta accion"
                )
            direccion.activo = False
            direccion.deleted_at = datetime.now(timezone.utc)
            uow.direccion_entrega.add(direccion)
        
    def asignar_rol(self, admin_id: int, informacion: AdministrarRol) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = self._get_or_404(uow, informacion.usuario_id)
            rol = uow.rol.get_by_codigo(informacion.codigo_rol)
            if not rol:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
            if rol in usuario.roles:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya tiene asignado este rol")
            
            uow.usuario_rol.add(UsuarioRol(
                usuario_id = usuario.id,
                rol_codigo = informacion.codigo_rol,
                asignado_por_id = admin_id,
                expires_at = informacion.expires_at,
                created_at = datetime.now(timezone.utc)
            ))
            uow.refresh(usuario)
            usuario_rol_asignado = self._get_or_404(uow, usuario.id)
            return UsuarioRead.model_validate(usuario_rol_asignado)
        
    def quitar_rol(self, informacion: AdministrarRol) -> None:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(informacion.usuario_id)
            rol = uow.rol.get_by_codigo(informacion.codigo_rol)
            usuario_rol = uow.usuario_rol.get_link(informacion.usuario_id, informacion.codigo_rol)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            if not rol:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
            if not usuario_rol:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no tiene asignado este rol")
            
            uow.usuario_rol.delete(usuario_rol)
            uow.refresh(usuario)
            usuario_rol_revocado = self._get_or_404(uow, usuario.id)
            return UsuarioRead.model_validate(usuario_rol_revocado)
        
    def desactivar_usuario(self, usuario_id: int):
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(usuario_id)
            if not usuario: 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            if not usuario.activo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya se encuentra desactivado")
            usuario.deleted_at = datetime.now(timezone.utc)
            usuario.activo = False
            uow.usuario.add(usuario)
            
