# Código del proyecto

Estructura del repositorio y código relevante (sin *scaffolding*), ordenado para leerlo de arriba abajo y entender cómo encaja todo. Los conceptos están explicados en `APUNTES.md` y el progreso en `TODO.md`; aquí solo está el código, con una breve introducción en cada bloque.

> **Foto a fecha del commit `fe43779`** (B5: modelos + primera migración). Si el código cambia, manda el código: este fichero no se actualiza solo.

---

## 1. Árbol del proyecto

Ficheros versionados en git. Los marcados con `·` son *scaffolding* o configuración por defecto y no se copian más abajo.

```
gastos_python_react/
├── .gitignore                          · Python, Node, .env, .venv, node_modules, dist
├── .pre-commit-config.yaml             ruff antes de cada commit (§9)
├── APUNTES.md                          · apuntes de conceptos
├── TODO.md                             · hoja de ruta del proyecto
├── CODIGO.md                           · este fichero
├── README.md                           · (vacío)
├── docker-compose.yml                  db + api + adminer para desarrollo (§8)
├── scripts/
│   └── apuntes_ebook.py                · genera APUNTES.epub/.azw3 (herramienta, no es la app)
└── backend/
    ├── .dockerignore                   · qué no entra en el contexto de `docker build`
    ├── .env.example                    plantilla de variables de entorno (§3)
    ├── .python-version                 · 3.13
    ├── Dockerfile                      multi-stage: dev / prod (§8)
    ├── README.md                       · (vacío)
    ├── pyproject.toml                  dependencias, ruff, pytest (§9)
    ├── uv.lock                         · versiones exactas (lo genera uv)
    ├── alembic.ini                     config de Alembic; solo se copia lo personalizado (§6)
    ├── alembic/
    │   ├── README                      · generado por `alembic init`
    │   ├── env.py                      conecta Alembic con la config y los modelos (§6)
    │   ├── script.py.mako              · plantilla de las migraciones
    │   └── versions/
    │       ├── .gitkeep                ·
    │       └── 2026_10_25_1124-3164f9e00e5c_tablas_iniciales.py   primera migración (§6)
    ├── src/backend/
    │   ├── __init__.py                 ·
    │   ├── main.py                     crea la app FastAPI y registra los routers (§4)
    │   ├── core/
    │   │   └── config.py               Settings (pydantic-settings) (§3)
    │   ├── api/routes/
    │   │   └── health.py               GET /health, /health/db (§4)
    │   ├── db/
    │   │   ├── base.py                 Base declarativa + naming convention (§5)
    │   │   └── session.py              engine, SessionLocal, get_db, DbSession (§5)
    │   ├── models/
    │   │   ├── __init__.py             importa todos los modelos (§5)
    │   │   ├── category.py             tabla categories (§5)
    │   │   ├── cost_center.py          tabla cost_centers (§5)
    │   │   └── expense.py              tabla expenses (§5)
    │   ├── schemas/                    · vacío (Pydantic, llega en B6)
    │   └── services/                   · vacío (lógica de negocio, llega en B6)
    └── tests/
        ├── test_health.py              (§7)
        ├── test_db.py                  (§7) necesita Postgres levantado
        └── test_models.py              (§7)
```

Todavía no existe `frontend/`.

---

## 2. Mapa: cómo encaja todo

**Una petición HTTP** (`GET /health/db`):

```
uvicorn (servidor ASGI)
  └─▶ backend.main:app                         main.py
        └─▶ router de health                    api/routes/health.py
              └─▶ health_db(db: DbSession)
                    └─▶ Depends(get_db)         db/session.py  ── abre una Session por petición
                          └─▶ SessionLocal()    db/session.py  ── fábrica de sesiones
                                └─▶ engine      db/session.py  ── pool de conexiones
                                      └─▶ Postgres (DATABASE_URL de core/config.py)
```

**Las tablas** (camino paralelo, no pasa por la API):

```
models/category.py ─┐
models/cost_center.py ─┼─▶ se registran en Base.metadata (db/base.py)
models/expense.py ──┘          │
                               ▼
alembic/env.py  ── compara Base.metadata con la BD real ──▶ alembic/versions/*.py
                ── usa la misma DATABASE_URL (core/config.py)
```

**La configuración** sale siempre de un único sitio: `get_settings()` en `core/config.py`, que lee variables de entorno (o `.env`). La usan `db/session.py` (la API) y `alembic/env.py` (las migraciones).

---

## 3. Configuración

### `backend/src/backend/core/config.py`

Toda la configuración de la app en una clase. Fíjate en:
- un campo sin valor por defecto (`database_url`) es obligatorio: sin él la app no arranca;
- `Literal[...]` restringe los valores válidos;
- `@lru_cache` hace que `Settings()` se cree una sola vez.

```python
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

    # Si es True, SQLAlchemy imprime en consola cada sentencia SQL que ejecuta.
    db_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración. Se crea una sola vez y se reutiliza (caché)."""
    # El editor cree que falta `database_url`; no sabe que se lee del entorno.
    return Settings()  # type: ignore[call-arg]
```

### `backend/.env.example`

Plantilla versionada; el `.env` real (ignorado por git) se crea copiándola. Cada variable corresponde a un campo de `Settings`.

```dotenv
# Plantilla de configuración del backend.
# Copiar a `.env` (no se versiona) y rellenar con valores reales:
#   cp .env.example .env
# Las variables de entorno del sistema tienen prioridad sobre este fichero.

# Conexión a PostgreSQL (obligatoria).
# Formato: postgresql+psycopg://USUARIO:CONTRASEÑA@HOST:PUERTO/BASE_DE_DATOS
# `+psycopg` indica a SQLAlchemy qué driver usar (psycopg 3).
# En local, contra el Postgres de Docker Compose con el puerto publicado, el host es `localhost`.
DATABASE_URL=postgresql+psycopg://gastos:gastos@localhost:5432/gastos

# Entorno de ejecución: development | test | production (opcional, por defecto development).
ENVIRONMENT=development

# Imprimir en consola el SQL que genera SQLAlchemy: true | false (opcional, por defecto false).
DB_ECHO=false
```

---

## 4. Arranque de la app

### `backend/src/backend/main.py`

El punto de entrada: `uvicorn backend.main:app`. Solo crea la app y engancha los routers; los endpoints viven en `api/routes/`.

```python
from fastapi import FastAPI

from backend.api.routes import health

app = FastAPI(title="Gastos API")

app.include_router(health.router)
```

### `backend/src/backend/api/routes/health.py`

Primer router. `health_db` es el ejemplo mínimo de endpoint con BD: recibe la sesión por inyección de dependencias (`DbSession`) en vez de crearla él. `/holiwi` es un endpoint de prueba.

```python
from fastapi import APIRouter
from sqlalchemy import text

from backend.db.session import DbSession

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/db")
def health_db(db: DbSession) -> dict[str, str]:
    """Comprueba la cadena engine -> sesión -> get_db con un `SELECT 1`."""
    db.execute(text("SELECT 1"))
    return {"database": "ok"}


@router.get("/holiwi")
def holiwi() -> dict[str, str]:
    return {"holiwi": "kiwi"}
```

---

## 5. Base de datos

### Esquema

```
categories                 expenses                          cost_centers
──────────────             ───────────────────────────       ──────────────
id    PK         1 ───┐    id              PK          ┌── 1 id    PK
name  UQ (50)         └─N  category_id     FK RESTRICT │     name  UQ (100)
color NULL (7)             cost_center_id  FK RESTRICT ┘N
                           amount          Numeric(12,2)  CHECK amount > 0
                           date            Date  (índice)
                           description     NULL (255)
                           created_at      now() en Postgres
```

Una categoría y un centro de coste tienen muchos gastos (1-N). `RESTRICT` impide borrar una categoría o un centro que aún tenga gastos.

### `backend/src/backend/db/base.py`

Clase madre de todos los modelos. La `NAMING_CONVENTION` da nombres predecibles a PK, FK, índices, etc.: en la migración aparecen `pk_categories`, `fk_expenses_category_id_categories`…

```python
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
```

### `backend/src/backend/db/session.py`

Las tres piezas para hablar con la BD, de más general a más concreta: `engine` (pool de conexiones, uno por proceso) → `SessionLocal` (fábrica) → `get_db()` (una sesión por petición). `DbSession` es el alias que usan los endpoints.

```python
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
```

### `backend/src/backend/models/__init__.py`

Importar `backend.models` registra todos los modelos de una vez. Lo hacen `alembic/env.py` y `tests/test_models.py`.

```python
# Importar aquí todos los modelos: con un solo `import backend.models` quedan
# registrados en Base.metadata (lo usará Alembic) y se resuelven las relaciones
# que se nombran como texto ("Expense", "Category"...).
from backend.models.category import Category
from backend.models.cost_center import CostCenter
from backend.models.expense import Expense

__all__ = ["Category", "CostCenter", "Expense"]
```

### `backend/src/backend/models/category.py`

Patrón que siguen todos los modelos: `Mapped[tipo]` decide el tipo y si admite NULL (`| None`), y `mapped_column(...)` añade los detalles SQL. `expenses` no es una columna: es el lado "1" de la relación.

```python
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

# Solo para el editor/ruff: evita el import circular category <-> expense en ejecución.
if TYPE_CHECKING:
    from backend.models.expense import Expense


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    # `| None` -> la columna admite NULL (nullable=True). Sin él, NOT NULL.
    color: Mapped[str | None] = mapped_column(String(7))  # hex "#RRGGBB"

    # Lado "1" de la relación 1-N: no es una columna, es un atributo Python
    # que SQLAlchemy rellena consultando `expenses.category_id`.
    expenses: Mapped[list["Expense"]] = relationship(back_populates="category")
```

### `backend/src/backend/models/cost_center.py`

Igual que `Category`, sin color.

```python
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.models.expense import Expense


class CostCenter(Base):
    __tablename__ = "cost_centers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    expenses: Mapped[list["Expense"]] = relationship(back_populates="cost_center")
```

### `backend/src/backend/models/expense.py`

El modelo central. Aquí están las decisiones importantes: `Numeric` para el dinero, `CheckConstraint`, claves foráneas con `RESTRICT` e índice, y `server_default` para `created_at`.

```python
import datetime as dt  # como módulo: el campo `date` no tapa al tipo `dt.date`
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.models.category import Category
    from backend.models.cost_center import CostCenter


class Expense(Base):
    __tablename__ = "expenses"
    # Regla que comprueba la propia BD: rechaza el INSERT/UPDATE aunque falle la API.
    __table_args__ = (CheckConstraint("amount > 0", name="amount_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    # Dinero: Numeric (decimal exacto), nunca Float. 12 dígitos, 2 decimales.
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    date: Mapped[dt.date] = mapped_column(Date, index=True)  # se filtrará por rango
    description: Mapped[str | None] = mapped_column(String(255))

    # Lado "N": la columna real con la clave foránea. RESTRICT impide borrar una
    # categoría/centro que aún tenga gastos. Postgres no indexa las FK solo.
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True
    )
    cost_center_id: Mapped[int] = mapped_column(
        ForeignKey("cost_centers.id", ondelete="RESTRICT"), index=True
    )

    # server_default: el valor lo pone Postgres (now()) al insertar, no Python.
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    category: Mapped["Category"] = relationship(back_populates="expenses")
    cost_center: Mapped["CostCenter"] = relationship(back_populates="expenses")
```

---

## 6. Migraciones (Alembic)

### `backend/alembic.ini` (solo lo personalizado)

El resto del fichero es el que genera `alembic init` (logging). Lo cambiado:
- `file_template`: los nombres de las migraciones empiezan por fecha y hora, así quedan ordenadas en el explorador;
- `[post_write_hooks]`: cada migración generada pasa por `ruff check --fix` y `ruff format`.

```ini
[alembic]
script_location = %(here)s/alembic
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
prepend_sys_path = .

[post_write_hooks]
hooks = ruff_check, ruff_format
ruff_check.type = module
ruff_check.module = ruff
ruff_check.options = check --fix REVISION_SCRIPT_FILENAME
ruff_format.type = module
ruff_format.module = ruff
ruff_format.options = format REVISION_SCRIPT_FILENAME
```

### `backend/alembic/env.py`

Se ejecuta con cada comando de Alembic. Une las dos mitades: la **URL** sale de `get_settings()` y el **catálogo de tablas** de `Base.metadata` (por eso importa `backend.models`).

```python
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
```

### `backend/alembic/versions/2026_10_25_1124-3164f9e00e5c_tablas_iniciales.py`

Generada con `alembic revision --autogenerate -m "tablas iniciales"` y revisada a mano. Compárala con los modelos de §5: cada `Mapped`/`mapped_column` se convierte en un `sa.Column`, y los nombres de constraints salen de la `NAMING_CONVENTION`. `downgrade()` deshace en orden inverso (primero `expenses`, que depende de las otras dos).

```python
"""tablas iniciales

Revision ID: 3164f9e00e5c
Revises:
Create Date: 2026-10-25 11:24:29.000843

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3164f9e00e5c"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
        sa.UniqueConstraint("name", name=op.f("uq_categories_name")),
    )
    op.create_table(
        "cost_centers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cost_centers")),
        sa.UniqueConstraint("name", name=op.f("uq_cost_centers_name")),
    )
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("cost_center_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("amount > 0", name=op.f("ck_expenses_amount_positive")),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("fk_expenses_category_id_categories"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cost_center_id"],
            ["cost_centers.id"],
            name=op.f("fk_expenses_cost_center_id_cost_centers"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_expenses")),
    )
    op.create_index(
        op.f("ix_expenses_category_id"), "expenses", ["category_id"], unique=False
    )
    op.create_index(
        op.f("ix_expenses_cost_center_id"), "expenses", ["cost_center_id"], unique=False
    )
    op.create_index(op.f("ix_expenses_date"), "expenses", ["date"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_expenses_date"), table_name="expenses")
    op.drop_index(op.f("ix_expenses_cost_center_id"), table_name="expenses")
    op.drop_index(op.f("ix_expenses_category_id"), table_name="expenses")
    op.drop_table("expenses")
    op.drop_table("cost_centers")
    op.drop_table("categories")
    # ### end Alembic commands ###
```

---

## 7. Tests

Se ejecutan con `uv run pytest` desde `backend/`.

### `backend/tests/test_health.py`

El test más simple: `TestClient` hace peticiones a la app sin levantar un servidor.

```python
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_devuelve_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

### `backend/tests/test_db.py`

El primero **necesita Postgres** (`docker compose up -d db`). El segundo no: sustituye `get_db` por un mock con `dependency_overrides`, la misma técnica que se usará en B6 para tener una BD de pruebas.

```python
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.db.session import get_db
from backend.main import app

client = TestClient(app)


def test_health_db_conecta_con_postgres() -> None:
    # Necesita el Postgres de Compose levantado: `docker compose up -d db`
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"database": "ok"}


def test_get_db_se_puede_sustituir() -> None:
    # dependency_overrides cambia una dependencia por otra solo en tests.
    # En B6 se usará para dar a los endpoints una sesión contra una BD de pruebas.
    sesion_falsa = MagicMock()
    app.dependency_overrides[get_db] = lambda: sesion_falsa
    try:
        response = client.get("/health/db")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    sesion_falsa.execute.assert_called_once()
```

### `backend/tests/test_models.py`

No necesita BD: inspecciona `Base.metadata` para comprobar las decisiones del esquema.

```python
from sqlalchemy import Numeric

import backend.models  # noqa: F401  (registra los modelos en Base.metadata)
from backend.db.base import Base

# No necesita Postgres: solo inspecciona la descripción de las tablas.
tables = Base.metadata.tables


def test_existen_las_tablas() -> None:
    assert set(tables) == {"categories", "cost_centers", "expenses"}


def test_importe_es_numeric_y_no_float() -> None:
    amount = tables["expenses"].c.amount

    assert isinstance(amount.type, Numeric)
    assert (amount.type.precision, amount.type.scale) == (12, 2)
    assert amount.type.asdecimal  # devuelve Decimal en Python


def test_gasto_tiene_categoria_y_centro_de_coste_obligatorios() -> None:
    expenses = tables["expenses"]

    for column, target in [
        ("category_id", "categories.id"),
        ("cost_center_id", "cost_centers.id"),
    ]:
        col = expenses.c[column]
        assert not col.nullable
        assert {fk.target_fullname for fk in col.foreign_keys} == {target}


def test_color_de_categoria_es_opcional() -> None:
    assert tables["categories"].c.color.nullable
```

---

## 8. Docker

### `backend/Dockerfile`

Multi-stage: `dev` para Compose (con `--reload` y el código montado desde el host) y `prod` para Cloud Run (solo Python + `.venv`, usuario sin privilegios). El diagrama de etapas está al principio del fichero.

```dockerfile
# Dockerfile multi-stage del backend.
# Un solo fichero, varias "etapas" (FROM ... AS nombre); con `--target` se elige cuál construir:
#   docker build --target dev  -t gastos-api:dev  backend/   -> desarrollo (Compose)
#   docker build --target prod -t gastos-api:prod backend/   -> producción (Cloud Run)
#
#   base ──┬── dev       (deps de desarrollo, --reload, el código llega por bind mount)
#          └── builder ── prod  (solo se copia el .venv final; sin uv, sin código fuente suelto)

# ============================================================
# base: Python + uv, común a todas las etapas
# ============================================================
FROM python:3.13-slim AS base

# uv se copia desde su imagen oficial (un binario, sin pip install).
# Misma versión que en local para que interprete el uv.lock igual.
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"
# PYTHONUNBUFFERED: los print/logs salen al momento en `docker compose logs`.
# UV_LINK_MODE=copy: la caché de uv es un mount aparte; no se pueden hacer hardlinks entre ellos.
# PATH: así `uvicorn` y `python` son los del .venv sin tener que poner `uv run`.

WORKDIR /app

# ============================================================
# dev: imagen para desarrollo con Docker Compose
# ============================================================
FROM base AS dev

# El código se monta desde el host (bind mount), así que Python escribiría los
# __pycache__ dentro de tu carpeta src/ como root. Se desactiva.
ENV PYTHONDONTWRITEBYTECODE=1

# 1) Solo dependencias (incluidas las de dev). Se usan pyproject.toml y uv.lock
#    como bind mounts de construcción: esta capa solo se rehace si cambian ellos,
#    no cada vez que tocas un .py. La caché de uv persiste entre builds.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# 2) Código y proyecto. Se instala en modo editable: el .venv apunta a /app/src,
#    que en Compose queda tapado por el bind mount con tu código vivo.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================
# builder: prepara el .venv de producción (etapa intermedia, se descarta)
# ============================================================
FROM base AS builder

# Compila a .pyc al instalar: arranque más rápido en producción (importa para cold starts).
ENV UV_COMPILE_BYTECODE=1

# Mismo truco de caché que en dev, pero sin dependencias de desarrollo.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# --no-editable: el paquete `backend` se copia dentro del .venv (site-packages),
# así la imagen final solo necesita el .venv y no la carpeta src/.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# ============================================================
# prod: imagen final, mínima
# ============================================================
# Parte de cero (sin uv, sin cachés, sin código fuente): solo Python + el .venv.
FROM python:3.13-slim AS prod

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Usuario sin privilegios: si alguien compromete la app, no es root en el contenedor.
RUN useradd --system --no-create-home app

WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv

USER app

# Cloud Run indica en qué puerto escuchar con la variable PORT (8000 si no existe).
# Se usa `sh -c` para que se expanda ${PORT}, y `exec` para que uvicorn sustituya
# al shell y reciba directamente las señales de parada (SIGTERM) -> apagado limpio.
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### `docker-compose.yml`

Entorno local completo. Fíjate en cómo se configura la API desde fuera (`environment:` → `Settings`) y en que el host de la BD es `db`, no `localhost`.

```yaml
# Entorno de desarrollo local: PostgreSQL + API (+ Adminer).
#   docker compose up -d        arrancar en segundo plano (añade --build si cambias Dockerfile o dependencias)
#   docker compose logs -f api  seguir los logs de la API
#   docker compose down         parar y borrar contenedores (los datos de la BD se conservan)
#   docker compose down -v      ídem + borrar volúmenes (¡se pierden los datos!)
#
# Las credenciales de aquí son solo para desarrollo local; en la nube irán en Secret Manager.

services:
  # --- Base de datos ---
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: gastos
      POSTGRES_PASSWORD: gastos
      POSTGRES_DB: gastos
    ports:
      # Publicado en el host para conectar desde fuera de Compose
      # (uvicorn local, tests, un cliente SQL...) con localhost:5432.
      - "5432:5432"
    volumes:
      # Volumen nombrado: Docker lo gestiona y sobrevive a `down` (no a `down -v`).
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      # `pg_isready` responde OK solo cuando Postgres ya acepta conexiones,
      # que es bastante después de que el contenedor haya "arrancado".
      test: ["CMD-SHELL", "pg_isready -U gastos -d gastos"]
      interval: 5s
      timeout: 5s
      retries: 10

  # --- API (FastAPI) ---
  api:
    build:
      context: ./backend
      target: dev
    ports:
      - "8000:8000"
    environment:
      # Dentro de la red de Compose, cada servicio se alcanza por su nombre: el host es `db`.
      # (`localhost` aquí sería el propio contenedor de la API, donde no hay Postgres.)
      # Estas variables tienen prioridad sobre cualquier .env.
      DATABASE_URL: postgresql+psycopg://gastos:gastos@db:5432/gastos
      ENVIRONMENT: development
      DB_ECHO: "true" # ver en `docker compose logs -f api` el SQL que genera SQLAlchemy
    volumes:
      # Bind mount: tu carpeta src/ del host aparece en /app/src del contenedor.
      # Al guardar un .py, uvicorn --reload lo detecta y reinicia.
      # Solo se monta src/ (no todo backend/) para no tapar el .venv del contenedor con el del host.
      - ./backend/src:/app/src
    depends_on:
      db:
        condition: service_healthy # espera al healthcheck, no solo a que el contenedor exista

  # --- Adminer: cliente web para ver la BD (opcional) ---
  # http://localhost:8080 -> Sistema: PostgreSQL, Servidor: db, Usuario/Contraseña/BD: gastos
  adminer:
    image: adminer
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  pgdata:
```

---

## 9. Proyecto y herramientas

### `backend/pyproject.toml`

Dependencias de la app y de desarrollo (`[dependency-groups]`), y configuración de ruff y pytest.

```toml
[project]
name = "backend"
version = "0.1.0"
description = "Proyecto de aprendizaje gastos"
readme = "README.md"
authors = [
    { name = "Luis", email = "qfluis@gmail.com" }
]
requires-python = ">=3.13"
dependencies = [
    "alembic>=1.20.1",
    "fastapi>=0.162.0",
    "psycopg[binary]>=3.3.6",
    "pydantic-settings>=2.16.1",
    "sqlalchemy>=2.1.6",
    "uvicorn[standard]>=0.54.0",
]

[project.scripts]
backend = "backend:main"

[build-system]
requires = ["uv_build>=0.13.5,<0.14.0"]
build-backend = "uv_build"

[dependency-groups]
dev = [
    "httpx2>=2.16.0",
    "pre-commit>=4.7.0",
    "pytest>=9.1.1",
    "ruff>=0.17.2",
]

# --- Ruff: linter + formateador ---
[tool.ruff]
line-length = 88          # igual que Black (estándar de facto)
target-version = "py313"  # coincide con requires-python
src = ["src"]             # para que ordene bien los imports propios (backend.*)

[tool.ruff.lint]
select = [
    "E", "W",  # pycodestyle: errores y avisos de estilo (PEP 8)
    "F",       # Pyflakes: imports sin usar, variables no definidas...
    "I",       # isort: orden de imports
    "N",       # pep8-naming: convenciones de nombres
    "UP",      # pyupgrade: sintaxis moderna de Python (list[str], X | None...)
    "B",       # flake8-bugbear: bugs típicos (argumentos mutables por defecto...)
    "SIM",     # flake8-simplify: código que se puede simplificar
    "C4",      # flake8-comprehensions: comprehensions más limpias
    "RUF",     # reglas propias de Ruff
    "FAST",    # reglas específicas de FastAPI
]
ignore = [
    "E501",    # longitud de línea: ya la gestiona el formateador
]

[tool.ruff.lint.flake8-bugbear]
# Permite `def endpoint(db = Depends(get_db))` sin que B008 se queje
extend-immutable-calls = ["fastapi.Depends", "fastapi.Query", "fastapi.Path", "fastapi.Body"]

[tool.ruff.format]
quote-style = "double"

# --- Pytest ---
[tool.pytest.ini_options]
testpaths = ["tests"]   # dónde buscar tests (más rápido y evita recoger .venv)
addopts = "-ra"         # resumen al final de tests saltados/fallidos
```

### `.pre-commit-config.yaml`

Pasa ruff por los ficheros de `backend/` antes de cada commit.

```yaml
# Hooks que se ejecutan automáticamente antes de cada `git commit`.
# Va en la raíz del repo porque git (y pre-commit) trabajan a nivel de repositorio,
# no de carpeta. Instalar una vez con: `cd backend && uv run pre-commit install`
repos:
  # --- Ruff (backend) ---
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.2 # mantener igual que la versión de ruff en backend/uv.lock
    hooks:
      - id: ruff-check
        args: [--fix] # arregla lo que pueda; si cambia algo, el commit se para para que lo revises
        files: ^backend/
      - id: ruff-format
        files: ^backend/
```

---

## 10. Pendiente / vacío a propósito

- `backend/src/backend/schemas/`: esquemas Pydantic de entrada y salida de la API (`ExpenseCreate`, `ExpenseRead`…). Llegan en **B6**.
- `backend/src/backend/services/`: lógica de negocio que no encaja en un endpoint (resúmenes, agregaciones). Llega en **B6**.
- `frontend/`: todavía no existe (**F1**).
- Migración aplicada (`alembic upgrade head`): pendiente en `TODO.md` (B5).
