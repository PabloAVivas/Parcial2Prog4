from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.producto.models import Producto
from app.modules.producto.schemas import ProductoCreate, ProductoUpdate, ProductoRead, ProductoPaginadoResponse, ProductoDisponibilidadUpdate, CategoriaBasicRead, IngredienteBasicRead, UnidadMedidaRead
from app.modules.usuarios.schemas import RolRead
from datetime import datetime, timezone
from app.modules.producto.unit_of_work import ProductoUnitOfWork

class ProductoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uow.producto.get_by_id_categorias_ingredientes(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        return producto

    def _map_to_read(self, producto: Producto) -> ProductoRead:
        unidad_medida=UnidadMedidaRead(
            nombre=producto.unidad_medida.nombre,
            simbolo=producto.unidad_medida.simbolo,
            tipo=producto.unidad_medida.tipo
        )
        
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
                stock_cantidad=link.ingrediente.stock_cantidad,
                es_alergeno=link.ingrediente.es_alergeno,
                cantidad= link.cantidad,
                unidad_medida= link.unidad_medida,
                es_removible=link.es_removible
            ) for link in producto.ingrediente_links
        ]

        res_dict = producto.model_dump()
        res_dict["unidad_medida"] = unidad_medida
        res_dict["categorias"] = categorias_read
        res_dict["ingredientes"] = ingredientes_read

        return ProductoRead(**res_dict)


    def crear(self, data: ProductoCreate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            unidad = uow.producto.get_unidad(data.unidad_medida_id)
            if not unidad:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Unidad de medida con id={data.unidad_medida_id} no encontrado",
                )
            producto = Producto(
                nombre=data.nombre,
                unidad_medida_id=data.unidad_medida_id,
                descripcion=data.descripcion,
                precio_base=data.precio_base,
                imagenes_url=data.imagenes_url,
                stock_cantidad=data.stock_cantidad,
                disponible=data.disponible,
            )
            if not data.categorias:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo se puede crear un producto si tiene por lo menos una categoria",
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
                uow.producto.add_ingrediente(producto.id, ing_input.id, ing_input.cantidad, ing_input.unidad_medida_id, ing_input.es_removible)

            uow.flush()
            producto_creado = uow.producto.get_by_id_categorias_ingredientes(producto.id)

            return self._map_to_read(producto_creado)

    def obtener_todos(self, offset: int = 0, limit: int = 100, nombre: Optional[str] = None, categoria_id: Optional[int] = None, disponible: Optional[bool] = None) -> ProductoPaginadoResponse:
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.producto.get_activo(offset=offset, limit=limit, nombre=nombre, categoria_id=categoria_id, disponible=disponible)
            total = uow.producto.count_activo(nombre=nombre, categoria_id=categoria_id, disponible=disponible)

            return ProductoPaginadoResponse(
                total=total,
                data=[self._map_to_read(p) for p in productos]
            )

    def obtener_por_id(self, producto_id: int) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            return self._map_to_read(producto)

    def actualizar(self, producto_id: int, data: ProductoUpdate, usuario_rol: list[RolRead]) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            if "ADMIN" in [rol.codigo for rol in usuario_rol]:
                unidad = uow.producto.get_unidad(data.unidad_medida_id)
                if not unidad:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Unidad de medida con id={data.unidad_medida_id} no encontrado",
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
                        uow.producto.add_ingrediente(producto.id, ing_input.id, ing_input.cantidad, ing_input.unidad_medida_id, ing_input.es_removible)

                uow.flush()
                producto_actualizado = uow.producto.get_by_id_categorias_ingredientes(producto.id)
                return self._map_to_read(producto_actualizado)


            elif "STOCK" in [rol.codigo for rol in usuario_rol]:
                producto.stock_cantidad = data.stock_cantidad
                producto.disponible = data.disponible
                uow.producto.add(producto)
                uow.flush()
                producto_actualizado = uow.producto.get_by_id_categorias_ingredientes(producto.id)
                return self._map_to_read(producto_actualizado)


        

    def actualizar_disponibilidad(self, producto_id: int, data: ProductoDisponibilidadUpdate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.disponible = data.disponible
            uow.producto.add(producto)
            uow.flush()
            producto_actualizado = uow.producto.get_by_id_categorias_ingredientes(producto.id)
            return self._map_to_read(producto_actualizado)

    def borrado_logico(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.activo = False
            producto.deleted_at = datetime.now(timezone.utc)
            uow.producto.add(producto)

