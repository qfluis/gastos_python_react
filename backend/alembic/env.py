"""Entorno de Alembic: se ejecuta en cada comando (`upgrade`, `revision`, `check`...).

Aquí se decide a qué BD conectarse (la URL de la config de la app) y con qué
catálogo de tablas comparar al hacer `--autogenerate` (`Base.metadata`).
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

import backend.models  # noqa: F401  (registra todos los modelos en Base.metadata)
from backend.core.config import get_settings
from backend.db.base import Base

# Objeto Config de Alembic: da acceso a los valores de alembic.ini.
config = context.config

# Configura el logging de Python según las secciones [loggers]... de alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Catálogo de tablas que deberían existir. `--autogenerate` lo compara con la BD
# real y escribe la diferencia. Si un modelo no se importó, aquí no aparece y
# Alembic propondría borrar su tabla.
target_metadata = Base.metadata

# La misma URL que usa la API (variable de entorno DATABASE_URL o .env).
# No se pasa por config.set_main_option(): el .ini interpreta los `%` y una
# contraseña con `%` rompería.
DATABASE_URL = get_settings().database_url


def run_migrations_offline() -> None:
    """Modo offline (`alembic upgrade head --sql`): no conecta, imprime el SQL.

    Útil para revisar qué se va a ejecutar o dárselo a quien gestione la BD.
    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,  # valores escritos en el SQL, no como parámetros
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online (lo normal): conecta con la BD y ejecuta las migraciones."""
    # Engine propio en vez del de db/session.py: Alembic es un proceso corto que
    # abre una conexión y termina. NullPool -> no guarda conexiones abiertas.
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        # Cada migración va en una transacción: en Postgres, si algo falla a mitad,
        # se deshace entera (el DDL también es transaccional).
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
