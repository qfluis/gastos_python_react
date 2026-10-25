from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Plantilla de nombres para índices y constraints. Sin ella, Postgres inventa
# nombres propios y Alembic no sabría cómo se llaman al borrarlos (downgrade).
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Clase madre de todos los modelos.

    Cada subclase se registra en `Base.metadata`, que es el "catálogo" de tablas
    del que Alembic saca las migraciones con `--autogenerate`.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
