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

## Archivo .env
```
  SECRET_KEY="clave de JWT creada por ustedes"
  POSTGRES_USER= "usuario de postgres" = "postgres"
  POSTGRES_PASSWORD= "contraseña propia de postgres" = "postgres"
  POSTGRES_DB= "nombre de la base de datos"
  POSTGRES_HOST= localhost
  POSTGRES_PORT= 5432
  DATABASE_URL=postgresql://postgres:{contaseña de postgres}@localhost:5432/parcial_v2

```

## Inicializacion del proyecto

```
  .../Parcial2Prog4 --> python -m venv .venv
  .../Parcial2Prog4 --> .venv/Scripts/Activate/ps1
  .../Parcial2Prog4 --> pip install -r requirements.txt
  .../Parcial2Prog4 --> fastapi dev app/main.py

```
