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
