from typing import Optional
from sqlmodel import Session
from fastapi import HTTPException, status
from app.modules.ingrediente.models import Ingrediente
from app.modules.ingrediente.schemas import IngredienteCreate, IngredienteUpdate, IngredienteRead, IngredientePaginadoResponse
from app.modules.ingrediente.unit_of_work import IngredienteUnitOfWork

class IngredienteService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: IngredienteUnitOfWork, ingrediente_id: int) -> Ingrediente:
            ingrediente = uow.ingrediente.get_by_id(ingrediente_id)
            if not ingrediente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingrediente con id={ingrediente_id} no encontrado",
                )
            return ingrediente

    def crear(self, data: IngredienteCreate) -> IngredienteRead:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = Ingrediente(**data.model_dump())
            uow.ingrediente.add(ingrediente)

            result = IngredienteRead.model_validate(ingrediente)

        return result

    def obtener_todos(self, offset: int = 0, limit: int = 100, nombre: Optional[str] = None) -> IngredientePaginadoResponse:
        with IngredienteUnitOfWork(self._session) as uow:
            ingredientes = uow.ingrediente.get_activo(offset=offset, limit=limit, nombre=nombre)
            total = uow.ingrediente.count_activo(nombre=nombre)

            return IngredientePaginadoResponse(
                total=total,
                data=[IngredienteRead.model_validate(i) for i in ingredientes],
            )

    def obtener_por_id(self, ingrediente_id: int) -> IngredienteRead:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            result = IngredienteRead.model_validate(ingrediente)

        return result

    def actualizar(self, ingrediente_id: int, data: IngredienteUpdate) -> IngredienteRead:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)

            patch = data.model_dump(exclude_unset=True)

            for field, value in patch.items():
                setattr(ingrediente, field, value)

            uow.ingrediente.add(ingrediente)
            result = IngredienteRead.model_validate(ingrediente)

        return result

    def borrado_logico(self, ingrediente_id: int) -> None:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            ingrediente.activo = False
            uow.ingrediente.add(ingrediente)
            uow.commit()
