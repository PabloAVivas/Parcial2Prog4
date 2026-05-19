from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.producto.models import Producto
from app.modules.producto.schemas import ProductoCreate, ProductoUpdate, ProductoRead, ProductoPaginadoResponse, CategoriaBasicRead, IngredienteBasicRead
from datetime import datetime, timezone
from app.modules.producto.unit_of_work import ProductoUnitOfWork

class ProductoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uow.producto.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        return producto
    
    def _map_to_read(self, producto: Producto) -> ProductoRead:
        categorias_read = [
            CategoriaBasicRead(
                id=link.categoria_id,
                nombre=link.categoria.nombre,
                es_principal=link.es_principal
            ) for link in producto.categoria_links
        ]

        ingredientes_read = [
            IngredienteBasicRead(
                id=link.ingrediente_id,
                nombre=link.ingrediente.nombre,
                es_alergeno=link.ingrediente.es_alergeno,
                es_removible=link.es_removible
            ) for link in producto.ingrediente_links
        ]

        res_dict = producto.model_dump()
        res_dict["categorias"] = categorias_read
        res_dict["ingredientes"] = ingredientes_read

        return ProductoRead(**res_dict)


    def crear(self, data: ProductoCreate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = Producto(
                nombre=data.nombre,
                descripcion=data.descripcion,
                precio_base=data.precio_base,
                imagenes_url=data.imagenes_url,
                stock_cantidad=data.stock_cantidad,
                disponible=data.disponible,
            )
            if not data.categorias or not data.ingredientes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo se puede crear un producto si tiene una categoria y un ingrediente minimo",
                )

            uow.producto.add(producto)

            principales = [c for c in data.categorias if c.es_principal]
            if len(principales) > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo puede haber una categoría principal por producto",
                )
            for cat_input in data.categorias:
                cat = uow.categoria.get_by_id(cat_input.id)
                if not cat:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Categoría {cat_input.id} no encontrada",
                    )
                uow.producto.add_categoria(producto.id, cat_input.id, cat_input.es_principal)

            for ing_input in data.ingredientes:
                ing = uow.ingrediente.get_by_id(ing_input.id)
                if not ing:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Ingrediente {ing_input.id} no encontrado",
                    )
                uow.producto.add_ingrediente(producto.id, ing_input.id, ing_input.es_removible)

            uow.flush()
            uow.refresh(producto)

            return self._map_to_read(producto)

    def obtener_todos(self, offset: int = 0, limit: int = 100, nombre: Optional[str] = None) -> ProductoPaginadoResponse:
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.producto.get_activo(offset=offset, limit=limit, nombre=nombre)
            total = uow.producto.count_activo(nombre=nombre)

            return ProductoPaginadoResponse(
                total=total,
                data=[self._map_to_read(p) for p in productos]
            )

    def obtener_por_id(self, producto_id: int) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            return self._map_to_read(producto)

    def actualizar(self, producto_id: int, data: ProductoUpdate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            if not data.categorias or not data.ingredientes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo se puede crear un producto si tiene al menos una categoría y un ingrediente"
                )

            patch = data.model_dump(exclude_unset=True, exclude={"categorias", "ingredientes"})

            for field, value in patch.items():
                setattr(producto, field, value)

            uow.producto.add(producto)

            principales = [c for c in data.categorias if c.es_principal]
            if len(principales) > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo puede haber una categoría principal por producto",
                )
            if data.categorias is not None:
                uow.producto.eliminar_categoria(producto.id)
                for cat_input in data.categorias:
                    cat = uow.categoria.get_by_id(cat_input.id)
                    if not cat:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Categoría {cat_input.id} no encontrada",
                        )
                    uow.producto.add_categoria(producto.id, cat_input.id, cat_input.es_principal)

            if data.ingredientes is not None:
                uow.producto.eliminar_ingrediente(producto.id)
                for ing_input in data.ingredientes:
                    ing = uow.ingrediente.get_by_id(ing_input.id)
                    if not ing:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Ingrediente {ing_input.id} no encontrado",
                        )
                    uow.producto.add_ingrediente(producto.id, ing_input.id, ing_input.es_removible)

            uow.commit()
            uow.refresh(producto)

            return self._map_to_read(producto)

    def borrado_logico(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.activo = False
            producto.deleted_at = datetime.now(timezone.utc)
            uow.producto.add(producto)
            uow.commit()

