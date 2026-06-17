# Link al video: https://youtu.be/fN62z0xsVcw
## Estructura del Proyecto

```
app/
├── core/
│   ├── config.py              # Configuración general
│   ├── database.py            # Conexión PostgreSQL + sesión
│   ├── deps.py                # Dependencias (get_current_user, require_role)
|   ├── rate_limit.py          # Implementacion de Rate Limiting
│   ├── repository.py          # BaseRepository[T] genérico
│   ├── security.py            # JWT + bcrypt
│   ├── unit_of_work.py        # Unit of Work base
|   └── websocket.py           # Administrador de conexiones en tiempo real (Rooms + Broadcast)
├── db/
│   └── seed.py                # Seed obligatorio
├── modules/
│   ├── admin/                 # /api/v1/admin/
│   ├── auth/                  # /api/v1/auth/
│   ├── categoria/             # /api/v1/categorias/
│   ├── direcciones/           # /api/v1/direcciones/
|   ├── estadisticas/          # /api/v1/estadisticas/
|   ├── images/                # /api/v1/uploads/
│   ├── ingrediente/           # /api/v1/ingredientes/
│   ├── pago/                  # /api/v1/pago/
│   ├── pedido/                # /api/v1/pedidos/
│   ├── producto/              # /api/v1/productos/
│   └── usuarios/              # /api/v1/usuarios/
└── main.py

tests/
├── confest.py                 # Configuracion de pytest, fixtures y BD de prueba
├── test_auth.py               
├── test_estadisticas.py
├── test_pagos.py
├── test_pedidos.py
├── test_uploads.py
└── test_websocket.py


```
## Generación de tunel con Ngrok
IMPORTANTE! Antes de levantar el proyecto, deben abrir una terminal e inicializar un tunel con ngrok

```
  1- Abrir un Simbolo de sistema (cmd)
  2- Escribir -> ngrok http 8000 
  3- La url generada por ngrok (tunel) tienen que guardarle en el .env (NGROK_URL)

```

## Inicializacion del proyecto

```
  .../Parcial2Prog4 --> python -m venv .venv                    # Creacion del venv
  .../Parcial2Prog4 --> .venv/Scripts/Activate/ps1              # Inicializacion del entorno virtual
  .../Parcial2Prog4 --> pip install -r requirements.txt         # Instalacion de dependencias
  .../Parcial2Prog4 --> fastapi dev app/main.py                 # Inicializacion del backend

```

## Inicializacion de pruebas

  Para este apartado, es necesario haber realizado la creacion del venv y la instalacion de las dependencias

```
  .../Parcial2Prog4 --> python -m pytest tests/ -v               # Un comando para correr los tests
  .../Parcial2Prog4 --> pytest                                   # Otra opcion de comando para correr los tests

```
