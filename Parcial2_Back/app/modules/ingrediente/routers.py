from typing import Annotated
from fastapi import APIRouter, Depends, Query, status, Path
from sqlmodel import Session
from app.core.database import get_session
from app.modules.ingrediente.schemas import IngredienteCreate, IngredienteUpdate, IngredienteRead, IngredientePaginadoResponse
from app.modules.ingrediente.services import IngredienteService

router = APIRouter()
def get_ingrediente_service(session: Session = Depends(get_session)) -> IngredienteService:
    return IngredienteService(session)

SeDe = Annotated[IngredienteService, Depends(get_ingrediente_service)]

@router.post("/", response_model=IngredienteRead, status_code=status.HTTP_201_CREATED, summary="Crear una Ingrediente")
def alta_ingrediente(ingrediente: IngredienteCreate, session: SeDe) -> IngredienteRead:
    return session.crear(ingrediente)

@router.get("/", response_model= IngredientePaginadoResponse, summary="Obtener categorias paginados")
def listar_ingredientes(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), nombre: str = Query(default=None) , session: IngredienteService = Depends(get_ingrediente_service)) -> IngredientePaginadoResponse:
    return session.obtener_todos(offset=offset, limit=limit, nombre=nombre)

@router.get("/{ingrediente_id}", response_model=IngredienteRead, summary="Obtener un ingrediente por id")
def detalle_ingrediente(session: SeDe, ingrediente_id: int = Path(gt=0) ) -> IngredienteRead:
    return session.obtener_por_id(ingrediente_id)

@router.patch("/{ingrediente_id}", response_model=IngredienteRead, summary="Actualizar un ingrediente con sus relaciones")
def actualizar_ingrediente(datos: IngredienteUpdate, session: SeDe, ingrediente_id: int = Path(gt=0) ) -> IngredienteRead:
    return session.actualizar(ingrediente_id, datos)

@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Borrado logico de un ingrediente")
def eliminar_ingrediente(session: SeDe, ingrediente_id: int = Path(gt=0) ) -> None:
    session.borrado_logico(ingrediente_id)