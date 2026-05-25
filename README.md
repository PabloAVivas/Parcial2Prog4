# Esquemas

## Auth
```
UsuarioRegister:
  nombre: str
  apellido: str
  celular: str
  email: str
  password: str
```
```
UsuarioLogin:
  email: str
  password: str
```
```
TokenRead:
  access_token: str
  token_type: str
  expires_in: datetime
```

## Usuarios
```
UsuarioRead:
  id: int
  nombre: str
  apellido: str
  email: str
  celular: str
  direcciones: List[DireccionEntregaRead]
  activo: bool
  roles: List[RolRead]
```
```
UsuarioUpdate:
  nombre: Optional[str]
  apellido: Optional[str]
  email: Optional[str]
  celular: Optional[str]
  activo: Optional[bool]
```
```
RolRead:
  codigo: str          # "ADMIN" | "CLIENT" | "STOCK" | "PEDIDOS"
  nombre: str
  descripcion: str
```
```
AdministrarRol:
  usuario_id: int
  codigo_rol: str
  expires_at: Optional[datetime] = None
```
```
UsuarioPaginadoResponse:
  total: int
  data: list[UsuarioRead]
```

## Direcciones
```
DireccionEntregaCreate:
  alias: Optional[str] = None
  linea1: str
  linea2: Optional[str] = None
  ciudad: str
  provincia: str
  codigo_postal: str
  latitud: float
  longitud: float
  es_principal: bool = False
```
```
DireccionEntregaRead:
  id: int
  alias: Optional[str]
  linea1: str
  linea2: Optional[str]
  ciudad: str
  provincia: str
  es_principal: bool
  created_at: datetime
  updated_at: datetime
  deleted_at: Optional[datetime]
```
```
DireccionEntregaUpdate:
  alias: Optional[str]
  linea1: Optional[str]
  linea2: Optional[str]
  ciudad: Optional[str]
  provincia: Optional[str]
  codigo_postal: Optional[str]
  latitud: Optional[float]
  longitud: Optional[float]
  es_principal: Optional[bool]
```

## Categorías
```
CategoriaCreate:
  nombre: str
  descripcion: str
  imagen_url: str
  parent_id: Optional[int] = None
```
```
CategoriaRead:
  id: int
  nombre: str
  descripcion: str
  imagen_url: str
  parent_id: Optional[int]
  activo: bool
  created_at: datetime
  updated_at: datetime
```
```
CategoriaUpdate:
  nombre: Optional[str]
  descripcion: Optional[str]
  imagen_url: Optional[str]
  parent_id: Optional[int]
```
```
CategoriaPaginadaResponse:
  total: int
  data: list[CategoriaRead]
```
```
CategoriaTree:
  id: int
  nombre: str
  descripcion: Optional[str]
  imagen_url: Optional[str]
  parent_id: Optional[int]
  subcategorias: list[CategoriaTree]
```

## Productos
```
UnidadMedidaRead:
  nombre: str       # "kilogramo", "litro", "pieza", etc.
  simbolo: str      # "kg", "L", "u", etc.
  tipo: str         # "masa", "volumen", "unidad", etc.
```
```
CategoriaBasicRead:
  id: int
  nombre: str
  es_principal: bool
```
```
IngredienteBasicRead:
  id: int
  nombre: str
  es_alergeno: bool
  cantidad: float
  unidad_medida: str
  es_removible: bool
```
```
ProductoCreate:
  nombre: str
  unidad_medida_id: int
  descripcion: str
  precio_base: float
  imagenes_url: list[str]
  stock_cantidad: int
  disponible: bool
  categorias: list[{ id: int, es_principal: bool }]
  ingredientes: list[{ id: int, cantidad: float, unidad_medida_id: int, es_removible: bool }]
```
```
ProductoRead:
  id: int
  nombre: str
  unidad_medida: UnidadMedidaRead
  descripcion: Optional[str]
  precio_base: float
  imagenes_url: list[str]
  stock_cantidad: int
  disponible: bool
  activo: bool
  categorias: list[CategoriaBasicRead]
  ingredientes: list[IngredienteBasicRead]
  created_at: datetime
  updated_at: datetime
```
```
ProductoUpdate:
  nombre: Optional[str]
  unidad_medida_id: Optional[int]
  descripcion: Optional[str]
  precio_base: Optional[float]
  imagenes_url: Optional[list[str]]
  stock_cantidad: Optional[int]
  disponible: Optional[bool]
  categorias: Optional[list[{ id: int, es_principal: bool }]]
  ingredientes: Optional[list[{ id: int, cantidad: float, unidad_medida_id: int, es_removible: bool }]]
```
```
ProductoDisponibilidadUpdate:
  disponible: bool
```
```
ProductoPaginadoResponse:
  total: int
  data: list[ProductoRead]
```

## Pedidos
```
DetallePedidoCreate:
  producto_id: int
  cantidad: int
  personalizacion: list[int]
```
```
PedidoCreate:
  direccion_id: Optional[int]
  forma_pago_codigo: str       # "MERCADOPAGO" | "EFECTIVO" | "TRANSFERENCIA"
  descuento: float
  costo_envio: float
  notas: Optional[str]
  detalle_pedidos: list[DetallePedidoCreate]
```
```
DetallePedidoRead:
  pedido_id: int
  producto_id: int
  cantidad: int
  nombre_snapshot: str
  precio_snapshot: float
  subtotal_snap: float
  personalizacion: list[int]
  created_at: datetime
```
```
HistorialEstadoPedidoRead:
  id: int
  pedido_id: int
  estado_desde: Optional[str]
  estado_hasta: str
  usuario_id: Optional[int]
  motivo: Optional[str]
  created_at: datetime
```
```
PedidoRead:
  id: int
  usuario_id: int
  direccion_id: Optional[int]
  estado_codigo: str
  forma_pago_codigo: str
  subtotal: float
  descuento: float
  costo_envio: float
  total: float
  notas: Optional[str]
  activo: bool
  usuario: { nombre, apellido, email, celular }
  direccion: Optional[{ linea1, linea2, ciudad, provincia }]
  detalle_pedidos: list[DetallePedidoRead]
  historial_estado: list[HistorialEstadoPedidoRead]
  created_at: datetime
  updated_at: datetime
```
```
PedidoHistorialUpdate:
  estado_bool: bool             # true = avanzar estado, false = cancelar
  motivo: Optional[str]
```


# Endpoints

> **NOTA:** Todos los endpoints protegidos requieren `Authorization: Bearer <access_token>` en el header, excepto register y login.  
> El refresh_token se almacena en cookie httpOnly y se envía automáticamente al llamar a `/auth/refresh`.

---

## Auth — `/api/v1/auth/`

| Método | Ruta | Body | Respuesta | Auth |
|--------|------|------|-----------|------|
| `POST` | `/register` | `UsuarioRegister` | `UsuarioRead` | ❌ Público |
| `POST` | `/login` | `UsuarioLogin` | `TokenRead` | ❌ Público |
| `PATCH` | `/refresh` | — | `TokenRead` | Cookie refresh_token |
| `GET` | `/me` | — | `UsuarioRead` | ✅ Cualquier autenticado |
| `POST` | `/logout` | — | `200 OK` | ✅ Cualquier autenticado |

---

## Usuarios — `/api/v1/usuarios/`

| Método | Ruta | Body | Respuesta | Auth |
|--------|------|------|-----------|------|
| `GET` | `/` | — | `list[UsuarioRead]` | ✅ ADMIN |
| `GET` | `/{usuario_id}` | — | `UsuarioRead` | ✅ ADMIN o propio |
| `PATCH` | `/{usuario_id}` | `UsuarioUpdate` | `UsuarioRead` | ✅ Solo propio |
| `PATCH` | `/asignar` | `AdministrarRol` | `UsuarioRead` | ✅ ADMIN |
| `PATCH` | `/remover` | `AdministrarRol` | `UsuarioRead` | ✅ ADMIN |
| `DELETE` | `/{usuario_id}` | — | `204 No Content` | ✅ ADMIN |

---

## Direcciones — `/api/v1/direcciones/`

| Método | Ruta | Body | Respuesta | Auth |
|--------|------|------|-----------|------|
| `POST` | `/` | `DireccionEntregaCreate` | `DireccionEntregaRead` | ✅ Cualquier autenticado |
| `GET` | `/` | — | `list[DireccionEntregaRead]` | ✅ Cualquier autenticado |
| `PATCH` | `/{direccion_id}` | `DireccionEntregaUpdate` | `DireccionEntregaRead` | ✅ Propietario |
| `PATCH` | `/{direccion_id}/principal` | — | `DireccionEntregaRead` | ✅ Propietario |
| `DELETE` | `/{direccion_id}` | — | `204 No Content` | ✅ Propietario |

---

## Categorías — `/api/v1/categorias/`

| Método | Ruta | Body | Respuesta | Auth |
|--------|------|------|-----------|------|
| `POST` | `/` | `CategoriaCreate` | `CategoriaRead` | ✅ ADMIN |
| `GET` | `/` | — | `CategoriaPaginadaResponse` | ❌ Público |
| `GET` | `/tree` | — | `list[CategoriaTree]` | ❌ Público |
| `GET` | `/{categoria_id}` | — | `CategoriaRead` | ❌ Público |
| `PATCH` | `/{categoria_id}` | `CategoriaUpdate` | `CategoriaRead` | ✅ ADMIN |
| `DELETE` | `/{categoria_id}` | — | `204 No Content` | ✅ ADMIN |

**Query params GET `/`:** `?offset=0&limit=20&nombre=&parent_id=`

---

## Productos — `/api/v1/productos/`

| Método | Ruta | Body | Respuesta | Auth |
|--------|------|------|-----------|------|
| `POST` | `/` | `ProductoCreate` | `ProductoRead` | ✅ ADMIN |
| `GET` | `/` | — | `ProductoPaginadoResponse` | ❌ Público |
| `GET` | `/{producto_id}` | — | `ProductoRead` | ❌ Público |
| `PATCH` | `/{producto_id}` | `ProductoUpdate` | `ProductoRead` | ✅ ADMIN o STOCK |
| `PATCH` | `/{producto_id}/disponibilidad` | `ProductoDisponibilidadUpdate` | `ProductoRead` | ✅ ADMIN o STOCK |
| `DELETE` | `/{producto_id}` | — | `204 No Content` | ✅ ADMIN |

**Query params GET `/`:** `?offset=0&limit=20&nombre=&categoria_id=&disponible=`

---

## Pedidos — `/api/v1/pedidos/`

| Método | Ruta | Body | Respuesta | Auth |
|--------|------|------|-----------|------|
| `POST` | `/` | `PedidoCreate` | `PedidoRead` | ✅ Cualquier autenticado |
| `GET` | `/` | — | `list[PedidoRead]` | ✅ ADMIN o PEDIDOS |
| `GET` | `/usuario/{usuario_id}` | — | `list[PedidoRead]` | ✅ Propietario |
| `GET` | `/{pedido_id}` | — | `PedidoRead` | ✅ Propietario, ADMIN o PEDIDOS |
| `PATCH` | `/{pedido_id}` | `PedidoHistorialUpdate` | `PedidoRead` | ✅ Propietario (solo cancelar), ADMIN o PEDIDOS |
| `DELETE` | `/{pedido_id}` | — | `204 No Content` | ✅ ADMIN |

**Máquina de estados:**  
`PENDIENTE → CONFIRMADO → EN_PREPARACION → EN_CAMINO → ENTREGADO`  
+ `CANCELADO` (desde PENDIENTE o CONFIRMADO para el cliente; desde cualquier estado no terminal para ADMIN/PEDIDOS)

---

## Admin — `/api/v1/admin/`

| Método | Ruta | Body | Respuesta | Auth |
|--------|------|------|-----------|------|
| `GET` | `/usuarios` | — | `UsuarioPaginadoResponse` | ✅ ADMIN |
| `PATCH` | `/usuarios/{usuario_id}/roles/asignar` | `AdministrarRol` | `UsuarioRead` | ✅ ADMIN |
| `PATCH` | `/usuarios/{usuario_id}/roles/remover` | `AdministrarRol` | `UsuarioRead` | ✅ ADMIN |
| `DELETE` | `/usuarios/{usuario_id}` | — | `204 No Content` | ✅ ADMIN |

**Query params GET `/usuarios`:** `?offset=0&limit=20&rol=CLIENT`

---

## Estructura del Proyecto

```
app/
├── core/
│   ├── config.py              # Configuración general
│   ├── database.py            # Conexión PostgreSQL + sesión
│   ├── deps.py                # Dependencias (get_current_user, require_role)
│   ├── repository.py          # BaseRepository[T] genérico
│   ├── security.py            # JWT + bcrypt
│   └── unit_of_work.py        # Unit of Work base
├── db/
│   └── seed.py                # Seed obligatorio
├── modules/
│   ├── admin/                 # /api/v1/admin/
│   ├── auth/                  # /api/v1/auth/
│   ├── categoria/             # /api/v1/categorias/
│   ├── direcciones/           # /api/v1/direcciones/
│   ├── ingrediente/           # /api/v1/ingredientes/
│   ├── pago/                  # /api/v1/pago/
│   ├── pedido/                # /api/v1/pedidos/
│   ├── producto/              # /api/v1/productos/
│   └── usuarios/              # /api/v1/usuarios/
└── main.py
```
