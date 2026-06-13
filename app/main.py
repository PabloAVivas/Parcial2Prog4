from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.db.seed import seed_all
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter
from app.modules.producto.routers import router as producto_router
from app.modules.categoria.routers import router as categoria_router
from app.modules.ingrediente.routers import router as ingrediente_router
from app.modules.pedido.routers import router as pedido_router
from app.modules.usuarios.routers import router as usuario_router
from app.modules.auth.routers import router as auth_router
from app.modules.direcciones.routers import router as direcciones_router
from app.modules.admin.routers import router as admin_router
from app.modules.images.routers import router as imagen_router

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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
CORSMiddleware,
allow_origins=['http://localhost:5173'],
allow_credentials=True,
allow_methods=['*'],
allow_headers=['*'],
)

app.include_router(producto_router, prefix="/api/v1/productos", tags=["producto"])
app.include_router(categoria_router, prefix="/api/v1/categorias", tags=["categoria"])
app.include_router(ingrediente_router, prefix="/api/v1/ingredientes", tags=["ingrediente"])
app.include_router(pedido_router, prefix="/api/v1/pedidos", tags=["pedido"])
app.include_router(usuario_router, prefix="/api/v1/usuarios", tags=["Usuarios"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(direcciones_router, prefix="/api/v1/direcciones", tags=["direcciones"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(imagen_router, prefix="/api/v1/imagenes", tags=["imagenes"])