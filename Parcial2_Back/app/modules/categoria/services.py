from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.categoria.models import Categoria
from app.modules.categoria.schemas import CategoriaCreate, CategoriaUpdate, CategoriaRead, CategoriaPaginadaResponse
from datetime import datetime, timezone
from app.modules.categoria.unit_of_work import CategoriaUnitOfWork

class CategoriaService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: CategoriaUnitOfWork, categoria_id: int) -> Categoria:
            categoria = uow.categoria.get_by_id(categoria_id)
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Categoria con id={categoria_id} no encontrada",
                )
            return categoria

    def crear(self, data: CategoriaCreate) -> CategoriaRead:
        with CategoriaUnitOfWork(self._session) as uow:
            if data.parent_id is not None:
                self._get_or_404(uow, data.parent_id)
            categoria = Categoria(**data.model_dump())
            uow.categoria.add(categoria)

            result = CategoriaRead.model_validate(categoria)

        return result

    def obtener_todas(self, offset: int = 0, limit: int = 100, nombre: Optional[str] = None) -> CategoriaPaginadaResponse:
        with CategoriaUnitOfWork(self._session) as uow:
            categorias = uow.categoria.get_activo(offset=offset, limit=limit, nombre=nombre)
            total = uow.categoria.count_activo(nombre=nombre)

            return CategoriaPaginadaResponse(
                total=total,
                data=[CategoriaRead.model_validate(c) for c in categorias],
            )

    def obtener_por_id(self, categoria_id: int) -> CategoriaRead:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            result = CategoriaRead.model_validate(categoria)
        return result

    def actualizar(self, categoria_id: int, data: CategoriaUpdate) -> CategoriaRead:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)

            if data.parent_id is not None:
                self._get_or_404(uow, data.parent_id)

            patch = data.model_dump(exclude_unset=True)

            for field, value in patch.items():
                setattr(categoria, field, value)

            uow.categoria.add(categoria)
            result = CategoriaRead.model_validate(categoria)

        return result

    def borrado_logico(self, categoria_id: int) -> None:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            categoria.activo = False
            categoria.deleted_at = datetime.now(timezone.utc)
            uow.categoria.add(categoria)
            uow.commit()
