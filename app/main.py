from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.modules.producto.routers import router as producto_router
from app.modules.categoria.routers import router as categoria_router
from app.modules.ingrediente.routers import router as ingrediente_router

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    
app = FastAPI(
    title="Primer Parcial",
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