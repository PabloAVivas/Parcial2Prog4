from typing import Annotated
from fastapi import APIRouter, Depends, status, Query, Path
from sqlmodel import Session
from app.core.database import get_session
from app.modules.categoria.schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate, CategoriaPaginadaResponse
from app.modules.categoria.services import CategoriaService

router = APIRouter()
def get_categoria_service(session: Session = Depends(get_session)) -> CategoriaService:
    return CategoriaService(session)

SeDe = Annotated[CategoriaService, Depends(get_categoria_service)]

@router.post("/", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED, summary="Crear una Categoria")
def alta_categoria(categoria: CategoriaCreate, session: SeDe) -> CategoriaRead:
    return session.crear(categoria)

@router.get("/", response_model= CategoriaPaginadaResponse, summary="Obtener categorias paginados")
def listar_categorias(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), nombre: str = Query(default=None) , session: CategoriaService = Depends(get_categoria_service)) -> CategoriaPaginadaResponse:
    return session.obtener_todas(offset=offset, limit=limit, nombre=nombre)

@router.get("/{categoria_id}", response_model=CategoriaRead, summary="Obtener un categoria por id")
def detalle_categoria(session: SeDe, categoria_id: int = Path(gt=0) ) -> CategoriaRead:
    return session.obtener_por_id(categoria_id)

@router.patch("/{categoria_id}", response_model=CategoriaRead, summary="Actualizar un categoria con sus relaciones")
def actualizar_categoria(datos: CategoriaUpdate, session: SeDe, categoria_id: int = Path(gt=0) ) -> CategoriaRead:
    return session.actualizar(categoria_id, datos)

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Borrado logico de un categoria")
def eliminar_categoria(session: SeDe, categoria_id: int = Path(gt=0) ) -> None:
    session.borrado_logico(categoria_id)