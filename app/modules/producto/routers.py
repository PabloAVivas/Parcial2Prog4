from typing import Annotated
from fastapi import APIRouter, Depends, Query, status, Path
from sqlmodel import Session
from app.core.database import get_session
from app.modules.producto.schemas import ProductoCreate, ProductoRead, ProductoUpdate, ProductoPaginadoResponse
from app.modules.producto.services import ProductoService

router = APIRouter()
def get_producto_service(session: Session = Depends(get_session)) -> ProductoService:
    return ProductoService(session)

SeDe = Annotated[ProductoService, Depends(get_producto_service)]

@router.post("/", response_model=ProductoRead, status_code=status.HTTP_201_CREATED, summary="Crear un Producto con sus relaciones")
def alta_producto(producto: ProductoCreate, session: SeDe) -> ProductoRead:
    return session.crear(producto)

@router.get("/", response_model= ProductoPaginadoResponse, summary="Obtener productos paginados")
def listar_productos(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), nombre: str = Query(default=None) , session: ProductoService = Depends(get_producto_service)) -> ProductoPaginadoResponse:
    return session.obtener_todos(offset=offset, limit=limit, nombre=nombre)

@router.get("/{producto_id}", response_model=ProductoRead, summary="Obtener un producto por id")
def detalle_producto(session: SeDe, producto_id: int = Path(gt=0) ) -> ProductoRead:
    return session.obtener_por_id(producto_id)

@router.patch("/{producto_id}", response_model=ProductoRead, summary="Actualizar un producto con sus relaciones")
def actualizar_producto(datos: ProductoUpdate, session: SeDe, producto_id: int = Path(gt=0) ) -> ProductoRead:
    return session.actualizar(producto_id, datos)

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Borrado logico de un producto")
def eliminar_producto(session: SeDe, producto_id: int = Path(gt=0) ) -> None:
    session.borrado_logico(producto_id)
