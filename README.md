# Esquemas
## Usuarios
* ```
  UsuarioRead :
    id: int
    nombre: str
    apellido: str
    celular: str
    direccion: List[DireccionEntregaRead]
    activo: bool
    roles: List[RolRead]
  ```
* ```
  UsuarioRegister :
    nombre: str
    apellido: str
    celular: str
    email: str
    password: str
  ```
* UsuarioUpdate : lo mismo que el register, pero todo opcional
* ```
  UsuarioLogin:
    email: str
    password: str
  ```
* ```
  DireccionEntregaCreate:
    usuario_id: int
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
* DireccionEntregaRead : lo mismo que el create, pero sin usuario_id y con id de la direccion
* DireccionEntregaUpdate : lo mismo que create, pero todo opcional meno el id de usuario
* ```
  RolRead :
    codigo : str -> "ADMIN" | "CLIENT" | ...
    nombre : str
    descripcion : str
  ```
* ```
  TokenRead :
    access_token: str
    token_type: str
    expires_in: datetime
  ```
* ```
  AdministrarRol :
    usuario_id: int
    codigo_rol: str
    expires_at: Optional[datetime] = None
  ```
  
  
# Endpoints
## Usuarios - IMPORTANTE -> Todos los endpoints tienen que tener Authorization Bearer + access_token en el headers || Utilizamos cookies para almacenar el refresh_token, esta cookie tiene que enviarse en la peticion del endpoint "/refresh" para que pueda generar el nuevo access_token
* POST -> UsuarioRegister -> http://localhost:8000/usuarios/register -> UsuarioRead
* POST -> UsuarioLogin -> http://localhost:8000/usuarios/login -> TokenRead
* PATCH -> http://localhost:8000/usuarios/refresh -> TokenRead
* POST -> http://localhost:8000/usuarios/logout -> 200 OK
* GET -> http://localhost:8000/usuarios/ -> list[UsuarioRead] -> ADMIN required
* GET -> http://localhost:8000/usuarios/{usuario_id] -> UsuarioRead -> ADMIN or current user
* PATCH -> UsuarioUpdate -> http://localhost:8000/usuarios/usuario_id -> UsuarioRead -> only current user
* DELETE -> http://localhost:8000/usuarios/{usuario_id} -> 204 NO CONTENT -> ADMIN required
* POST -> DireccionEntregaCreate -> http://localhost:8000/usuarios/direccion -> DireccionEntregaRead -> only current user
* PATCH -> DireccionEntregaUpdate -> http://localhost:8000/usuarios/direccion/{direccion_id} -> DireccionEntregaRead -> only current user
* DELETE -> http://localhost:8000/usuarios/direccion/{direccion_id} -> 204 NO CONTENT -> only current user
* PATCH -> AdministrarRol -> http://localhost:8000/usuarios/asignar -> 200 OK -> ADMIN required
* PATCH -> AdministrarRol -> http://localhost:8000/usuarios/remover -> 200 OK -> ADMIN required
