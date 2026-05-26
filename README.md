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
## METODOS DE PAGO - UNIDADES DE MEDIDA - ROLES - ESTADOS DE PEDIDO  -> No tienen endpoints, tienen que pasarlos directamente desde el front
* Roles
<img width="560" height="142" alt="image" src="https://github.com/user-attachments/assets/4b77a836-fe1a-499c-8099-fba9c6a6ec2c" />


* Unidades de medida
<img width="725" height="216" alt="image" src="https://github.com/user-attachments/assets/a4b0d2aa-f7be-45ea-9d85-4ce62cb6609e" />


* Metodos de pago
<img width="402" height="114" alt="image" src="https://github.com/user-attachments/assets/8bf3d48a-f24d-4688-bbf5-ac2f63abe2b7" />


* Estados de pedido
<img width="515" height="191" alt="image" src="https://github.com/user-attachments/assets/c9897c43-5a75-4965-9d6d-c1d9fe6e00d8" />
