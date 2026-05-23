from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.db.seed import seed_all

from app.modules.producto.routers import router as producto_router
from app.modules.categoria.routers import router as categoria_router
from app.modules.ingrediente.routers import router as ingrediente_router
from app.modules.pedido.routers import router as pedido_router
from app.modules.usuarios.routers import router as usuario_router

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    try:
        seed_all()
    except Exception as e:
        print(f"Error al ejecutar el seed: {e}")
    yield
    
app = FastAPI(
    title="Segundo Parcial",
    description="CRUD completo con Producto, Categoría e Ingrediente",
    version="1.0.0",
    lifespan=lifespan,
)
    
app.add_middleware(
CORSMiddleware,
allow_origins=['http://localhost:5173'],
allow_methods=['*'],
allow_headers=['*'],
)

app.include_router(producto_router, prefix="/productos", tags=["producto"])
app.include_router(categoria_router, prefix="/categorias", tags=["categoria"])
app.include_router(ingrediente_router, prefix="/ingredientes", tags=["ingrediente"])
app.include_router(pedido_router, prefix="/pedidos", tags=["pedido"])
app.include_router(usuario_router, prefix="/usuarios", tags=["Usuarios"])