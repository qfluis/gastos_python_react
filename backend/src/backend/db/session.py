from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import get_settings

settings = get_settings()

# Pool de conexiones a Postgres: uno por proceso, se crea al importar el módulo.
# No conecta todavía: abre conexiones cuando una sesión las pide.
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,  # True -> imprime en consola el SQL que genera SQLAlchemy
    pool_pre_ping=True,  # comprueba la conexión antes de reutilizarla (descarta las caídas)
)

# Fábrica de sesiones: `SessionLocal()` crea una Session nueva atada al engine.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,  # los cambios van a la BD al hacer commit()/flush(), no antes
    expire_on_commit=False,  # tras commit() los objetos conservan sus datos
)


def get_db() -> Iterator[Session]:
    """Dependencia de FastAPI: una sesión por petición, cerrada siempre al terminar."""
    with SessionLocal() as db:  # el `with` llama a db.close() aunque haya error
        yield db


# Alias para los endpoints: `def endpoint(db: DbSession): ...`
DbSession = Annotated[Session, Depends(get_db)]
