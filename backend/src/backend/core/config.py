from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la app, leída de variables de entorno (y de `.env` si existe).

    Cada atributo se corresponde con una variable de entorno del mismo nombre,
    sin distinguir mayúsculas: `database_url` <- `DATABASE_URL`.
    """

    model_config = SettingsConfigDict(
        env_file=".env",  # relativo al directorio desde el que se arranca (backend/)
        env_file_encoding="utf-8",
        extra="ignore",  # el .env puede tener variables para otros (p. ej. Postgres)
    )

    # Sin valor por defecto -> obligatoria: si falta, la app no arranca.
    database_url: str

    # Con valor por defecto -> opcional. Literal limita los valores válidos.
    environment: Literal["development", "test", "production"] = "development"


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración. Se crea una sola vez y se reutiliza (caché)."""
    # El editor cree que falta `database_url`; no sabe que se lee del entorno.
    return Settings()  # type: ignore[call-arg]
