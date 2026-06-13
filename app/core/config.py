from pydantic import computed_field
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "parcial_v2"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    # ----- JWT -----
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30

    # --- MercadoPago ---
    MP_ACCESS_TOKEN:  Optional[str] = None
    MP_PUBLIC_KEY:    Optional[str] = None
    MP_WEBHOOK_URL:   Optional[str] = None
    NGROK_URL:        Optional[str] = None

    # --- CORS y Frontend ---
    #   Si lees esto hay que revisarlo bien porque capaz esta muy al pedo
    # pero puede servir, mañana lo sigo viendo pero por ahora para que funcione
    # todo bien (si hay problemas fijarse de cambiar el puerto).
    CORS_ORIGINS:       str = "http://localhost:5173"
    VITE_FRONTEND_URL:  str = "http://localhost:5173"
    VITE_API_URL:       str = "http://localhost:8000"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()