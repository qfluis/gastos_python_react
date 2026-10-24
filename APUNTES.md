# Apuntes

## Puesta en marcha entorno / Instalaciones

### Python

#### uv

**Qué es:** gestor de proyectos y paquetes de Python (de Astral, los de Ruff), escrito en Rust. Sustituye a `pyenv`, `venv`, `pip`, `pip-tools`/Poetry y `pipx`, y es mucho más rápido.

**Para qué sirve:**
- Instalar versiones de Python sin tocar el del sistema → `uv python install 3.13`
- Crear el entorno virtual (`.venv`) de cada proyecto automáticamente
- Añadir dependencias → `uv add fastapi` (actualiza `pyproject.toml` y `uv.lock`)
- Ejecutar comandos dentro del entorno → `uv run ...`
- Fijar versiones exactas en `uv.lock` → local, contenedor y CI instalan lo mismo

**Instalación (Linux, sin sudo):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # se instala en ~/.local/bin
source ~/.bashrc                                  # o abrir una terminal nueva
uv --version                                      # comprobar
```

**Local vs. contenedor:**
- En **local**: se decide qué versiones usar (`uv add` → `uv.lock` → git) y el editor usa el `.venv`.
- En el **contenedor**: solo se reproduce lo que dice el lock → `uv sync --frozen`.

### Node.js

#### Versiones: LTS vs. actual
- Las versiones **pares** (20, 22, 24…) pasan a **LTS** (*Long Term Support*): unos 30 meses de soporte. Son las que se usan en proyectos.
- Las **impares** (19, 21, 23…) duran solo unos 6 meses y nunca llegan a LTS. No conviene usarlas.

#### fnm (gestor de versiones de Node)

**Qué es:** el equivalente a `uv python` en el mundo Node. Instala y cambia entre versiones de Node sin `sudo` ni tocar el sistema. Está escrito en Rust y es rápido. La alternativa clásica es `nvm` (en bash, más lento, pero igual de válido).

**Por qué no `apt install nodejs`:**
- La versión de los repositorios suele ser antigua, y la que haya instalada es una sola para todo el sistema.
- Cada proyecto puede necesitar una versión distinta, y con apt no se puede tener más de una.
- Para instalar paquetes globales (`npm i -g`) hace falta `sudo`.

**Instalación:**
```bash
curl -fsSL https://fnm.vercel.app/install | bash   # se instala en ~/.local/share/fnm y edita ~/.bashrc
source ~/.bashrc                                   # o abrir una terminal nueva
fnm --version                                      # comprobar
```

**Instalar Node LTS:**
```bash
fnm install --lts          # descarga la última LTS
fnm default lts-latest     # la marca como versión por defecto
node --version             # comprobar (debe ser par: v24, v26…)
npm --version
which node                 # debe apuntar a ~/.local/share/fnm/..., no a /usr/bin/node
```

**Fijar la versión por proyecto** (como `.python-version` en uv):
```bash
cd frontend
node --version > .node-version   # se versiona en git
```
- Para que fnm cambie de versión automáticamente al entrar en la carpeta, en `~/.bashrc` la línea `eval "`fnm env`"` debe quedar así: `eval "$(fnm env --use-on-cd --shell bash)"`.

**Node antiguo instalado con apt:** fnm tiene prioridad en el `PATH`, así que no molesta. Para eliminarlo: `sudo apt remove nodejs` (y quitar el repositorio de NodeSource de `/etc/apt/sources.list.d/` si existe).

### Docker

#### Docker Engine + Docker Compose

**Qué es:**
- **Docker Engine:** el motor que construye imágenes y ejecuta contenedores. Incluye el demonio `dockerd` y la CLI `docker`.
- **Docker Compose (plugin):** define y levanta varios contenedores juntos (backend, frontend, base de datos…) a partir de un `compose.yaml`. Con el plugin se usa `docker compose ...`, con espacio. El antiguo `docker-compose`, con guion, está obsoleto.

**Por qué no `apt install docker.io`:** es el paquete de Ubuntu, suele ir atrasado y no trae el plugin de Compose actualizado. Es mejor usar el repositorio oficial de Docker.

**Instalación (Ubuntu, con sudo):**

1. Añadir el repositorio oficial:
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

2. Instalar Engine y plugins:
```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

3. Usar Docker sin `sudo` (añadir el usuario al grupo `docker`):
```bash
sudo usermod -aG docker $USER
```
- El grupo nuevo se aplica al **volver a iniciar sesión**. `newgrp docker` solo sirve para la terminal actual, y VS Code hay que reiniciarlo entero.
- Estar en el grupo `docker` equivale a tener permisos de **root**. Es aceptable en un equipo de desarrollo.

**Comprobar:**
```bash
docker --version
docker compose version
docker run --rm hello-world   # sin sudo
id -nG | grep docker          # el usuario debe estar en el grupo
```

### VS Code

#### Extensiones VSC

| Extensión | ID | Para qué sirve |
|---|---|---|
| **Python** | `ms-python.python` | Soporte de Python: selector de intérprete (`.venv`), depurador y Pylance (autocompletado y tipos) |
| **Ruff** | `charliermarsh.ruff` | Linter y formateador de Python, el mismo `ruff` del proyecto |
| **ESLint** | `dbaeumer.vscode-eslint` | Muestra en el editor los errores de ESLint del frontend |
| **Prettier** | `esbenp.prettier-vscode` | Formateador de JS/TS, CSS, JSON, YAML, Markdown… |
| **Docker** | `ms-azuretools.vscode-docker` | Resaltado y ayuda para `Dockerfile` y `compose.yaml`; ver imágenes, contenedores y logs |

**Instalación desde la terminal:**
```bash
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension ms-azuretools.vscode-docker
```
- También desde la vista de extensiones (`Ctrl+Shift+X`) buscando el nombre o el ID.
- Comprobar: `code --list-extensions`

## Backend

### Iniciar el proyecto (FastAPI + uv)

**1. Crear el proyecto con uv:**
```bash
cd backend
uv init    # estructura src/: src/backend/__init__.py + [build-system] en pyproject.toml
```
- En uv 0.13, `uv init` sin opciones ya crea el layout `src/` y el código se instala como paquete importable (`backend`). Equivale a `uv init --package`.
- `uv init --no-package` crea una **app** plana (`main.py` en la raíz, sin `[build-system]`).
- `uv init --lib` es para librerías que se publican, no para una API.
- Hay que fijarse en lo que genera, porque el comportamiento por defecto ha cambiado entre versiones de uv.

**Ficheros generados:**
- `pyproject.toml`: nombre, versión, Python requerido y dependencias del proyecto.
- `.python-version`: versión de Python que usará uv en esta carpeta.
- `README.md` y `src/backend/__init__.py`.
- `.venv/` y `uv.lock` **no** aparecen hasta el primer `uv add`, `uv sync` o `uv run`. El `uv.lock` se versiona en git y el `.venv/` no.

**2. Fijar la versión de Python** (si `uv init` cogió la del sistema):
```bash
uv python install 3.13
uv python pin 3.13          # reescribe .python-version
```
- Ajustar también `requires-python = ">=3.13"` en `pyproject.toml` para que coincida.

**3. Añadir dependencias:**
```bash
uv add fastapi "uvicorn[standard]"
```
- **fastapi**: el framework (rutas, validación con Pydantic, OpenAPI automático).
- **uvicorn**: el servidor ASGI que ejecuta la app. `[standard]` añade extras más rápidos (`uvloop`, `httptools`) y la recarga automática.
- Crea `.venv/`, instala todo y actualiza `pyproject.toml` y `uv.lock`.

**4. Crear la app** en `src/backend/main.py`:
```python
from fastapi import FastAPI

app = FastAPI(title="Gastos API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

**5. Arrancar en desarrollo:**
```bash
uv run uvicorn backend.main:app --reload
```
- `backend.main:app` → módulo `backend/main.py`, variable `app`.
- `--reload` reinicia el servidor al guardar un `.py`. Es solo para desarrollo.
- Por defecto escucha en `http://127.0.0.1:8000`.

**Comprobar:**
- `http://127.0.0.1:8000/health` → `{"status": "ok"}`
- `http://127.0.0.1:8000/docs` → Swagger UI (probar endpoints desde el navegador)
- `http://127.0.0.1:8000/redoc` → documentación alternativa
- `http://127.0.0.1:8000/openapi.json` → esquema OpenAPI en crudo

**VS Code:** `Ctrl+Shift+P` → *Python: Select Interpreter* → `backend/.venv/bin/python`, para que Pylance reconozca `fastapi`.

### Calidad del código


**Dependencias de producción vs. de desarrollo:**
- **Producción** (`uv add paquete`) → van a `[project].dependencies`. La app las necesita para funcionar (`fastapi`, `uvicorn`).
- **Desarrollo** (`uv add --dev paquete`) → van a `[dependency-groups].dev`. Solo se usan mientras se programa (`ruff`, `pytest`…). La imagen de producción no las instala (`uv sync --no-dev`), así queda más pequeña.

#### Ruff (linter + formateador)

**Qué es:** herramienta de Astral (los de uv), escrita en Rust. Hace dos cosas:
- **Linter** (`ruff check`): busca errores y malas prácticas (imports sin usar, variables no definidas, bugs típicos…). Sustituye a Flake8, isort, pyupgrade…
- **Formateador** (`ruff format`): deja el código con un estilo uniforme. Es compatible con Black.

**1. Instalar:**
```bash
uv add --dev ruff
```

**2. Configurar** en `pyproject.toml` (secciones `[tool.ruff]`):
```toml
[tool.ruff]
line-length = 88
target-version = "py313"
src = ["src"]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "C4", "RUF", "FAST"]
ignore = ["E501"]
```
- `select` elige qué familias de reglas se activan. Cada letra es un plugin (`F` = Pyflakes, `I` = isort, `B` = bugbear, `FAST` = reglas de FastAPI…).
- `E501` (línea demasiado larga) se ignora porque ya lo resuelve el formateador.
- `extend-immutable-calls` en `[tool.ruff.lint.flake8-bugbear]` evita que ruff se queje de `Depends(...)` como valor por defecto, que en FastAPI es lo normal.

**3. Usar:**
```bash
uv run ruff check .          # muestra los problemas
uv run ruff check --fix .    # corrige los que se pueden arreglar solos
uv run ruff format .         # formatea el código
uv run ruff format --check . # solo comprueba, no toca nada (útil en CI)
```
- La extensión **Ruff** de VS Code usa la misma configuración del `pyproject.toml`, así que los avisos del editor coinciden con los de la terminal.

#### Tests: pytest + httpx2

**Qué es:**
- **pytest**: el framework de tests estándar en Python. Busca archivos `test_*.py`, ejecuta las funciones `test_*` y comprueba los `assert`.
- **httpx2**: cliente HTTP que usa por debajo el `TestClient` de FastAPI. Hace falta instalarlo aunque no se importe directamente.
- Se usa **`httpx2`** y no `httpx`: con `httpx`, Starlette (la base de FastAPI) avisa de que está obsoleto (`StarletteDeprecationWarning`).

**1. Instalar:**
```bash
uv add --dev pytest httpx2
```

**2. Configurar** en `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]   # buscar tests solo en tests/ (no recorre .venv)
addopts = "-ra"         # resumen final de tests fallidos/saltados
```

**3. Escribir el test** en `backend/tests/test_health.py`:
```python
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_devuelve_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```
- La carpeta `tests/` va **fuera** de `src/`: los tests no forman parte del paquete que se instala.
- `from backend.main import app` funciona porque uv instala el proyecto como paquete en el `.venv`.

**4. Ejecutar** (desde `backend/`):
```bash
uv run pytest        # resumen con un punto por test
uv run pytest -v     # nombre de cada test
uv run pytest -k health   # solo los tests cuyo nombre contiene "health"
```

**`TestClient`: probar la API sin levantar servidor:**
- No arranca uvicorn ni abre puertos. Llama a la app ASGI **directamente en memoria** y devuelve una respuesta igual que si fuera una petición HTTP real.
- Por eso los tests son rápidos y no dependen de que haya un servidor corriendo.

#### pre-commit (ruff antes de cada commit)

**Qué es:** herramienta que gestiona los *git hooks*, scripts que git ejecuta automáticamente en ciertos momentos. Con el hook `pre-commit`, ruff revisa el código **antes** de que se guarde el commit, y si algo falla el commit no se hace.

**1. Instalar:**
```bash
uv add --dev pre-commit
```

**2. Configurar** en `.pre-commit-config.yaml`, **en la raíz del repo** (git trabaja a nivel de repositorio, no de carpeta):
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.2 # misma versión que ruff en backend/uv.lock
    hooks:
      - id: ruff-check
        args: [--fix]
        files: ^backend/
      - id: ruff-format
        files: ^backend/
```
- `files: ^backend/` → los hooks solo miran archivos del backend. Más adelante se pueden añadir hooks para el frontend en el mismo archivo.
- pre-commit descarga **su propia copia** de ruff (la del `rev`), así que al actualizar ruff en `uv.lock` hay que cambiar también el `rev`. Si no, el editor y el hook podrían aplicar reglas distintas.

**3. Activar el hook** (una vez por cada clon del repo):
```bash
cd backend
uv run pre-commit install           # crea .git/hooks/pre-commit
uv run pre-commit run --all-files   # pasarlo a mano sobre todo el código
```
- `.git/hooks/` no se sube a git: quien clone el repo tiene que hacer `pre-commit install`.

**Qué pasa al hacer `git commit`:**
- Todo bien → el commit se hace normal.
- Ruff corrige algo → el commit **se para** (`Failed - files were modified by this hook`) y deja los archivos ya corregidos. Se revisan los cambios, `git add` y se repite el commit.
- Error que ruff no puede arreglar solo → lo muestra y el commit se para.
- `git commit --no-verify` se salta los hooks. Solo para casos puntuales.

### Configuración y estructura

#### 12-Factor App: la configuración va en el entorno

**Qué es:** *The Twelve-Factor App* es un conjunto de buenas prácticas para apps que se despliegan en la nube. El factor III dice que la **configuración** (lo que cambia entre local, test y producción: URL de la BD, claves, modo…) se lee de **variables de entorno**, no se escribe en el código.

**Por qué:**
- El mismo código (y la misma imagen Docker) sirve para todos los entornos; solo cambian las variables.
- Los secretos no acaban en git.
- Cloud Run, Docker Compose y GitHub Actions saben pasar variables de entorno, así que no hace falta nada especial.

#### pydantic-settings

**Qué es:** extensión de Pydantic que lee la configuración de variables de entorno (y de un `.env`) y la **valida y convierte de tipo** igual que un modelo Pydantic.

**1. Instalar** (dependencia de producción, la app la necesita para arrancar):
```bash
cd backend
uv add pydantic-settings
```

**2. Crear** `src/backend/core/config.py`:
```python
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
    return Settings()  # type: ignore[call-arg]
```
- Cada atributo se rellena con la variable de entorno del mismo nombre, **sin distinguir mayúsculas**: `database_url` ← `DATABASE_URL`.
- **Campo sin valor por defecto = obligatorio.** Si falta, salta un `ValidationError` al arrancar. Es mejor fallar pronto que en la primera consulta a la BD.
- **`Literal[...]`** solo admite esos valores: `ENVIRONMENT=staging` da error.
- **Prioridad:** las variables de entorno del sistema ganan al `.env`. Así Docker Compose o Cloud Run pueden sobrescribir lo que haya en el fichero.
- **`extra="ignore"`:** por defecto, si el `.env` tiene variables que `Settings` no conoce, da error. Se cambia porque el mismo `.env` tendrá variables para el contenedor de Postgres.
- **`get_settings()` con `@lru_cache`:** el `.env` se lee **una sola vez** y se reutiliza. Además no se lee al importar el módulo, sino al llamar a la función, y en los tests se puede sustituir por otra configuración. Es el patrón que recomienda la documentación de FastAPI.
- **`# type: ignore[call-arg]`:** el editor cree que falta el argumento `database_url` porque no sabe que se lee del entorno.

**3. Comprobar** (desde `backend/`):
```bash
uv run python -c "from backend.core.config import get_settings; print(get_settings())"
# sin DATABASE_URL     → ValidationError: database_url  Field required
# con DATABASE_URL     → database_url='postgresql+psycopg://...' environment='development'
# ENVIRONMENT=staging  → ValidationError: Input should be 'development', 'test' or 'production'
```

#### `.env` y `.env.example`

| Fichero | ¿Va a git? | Para qué |
|---|---|---|
| `.env.example` | **Sí** | Plantilla: documenta qué variables hacen falta, con valores de ejemplo (nunca secretos reales) |
| `.env` | **No** | Valores reales de cada desarrollador/máquina |

`backend/.env.example`:
```dotenv
# Conexión a PostgreSQL (obligatoria).
# Formato: postgresql+psycopg://USUARIO:CONTRASEÑA@HOST:PUERTO/BASE_DE_DATOS
DATABASE_URL=postgresql+psycopg://gastos:gastos@localhost:5432/gastos

# Entorno de ejecución: development | test | production (opcional).
ENVIRONMENT=development
```
- Va en `backend/` porque `env_file=".env"` es relativo a la carpeta desde la que se arranca uvicorn.
- `+psycopg` le dice a SQLAlchemy qué driver usar (psycopg 3).
- `localhost` sirve cuando uvicorn corre en local contra el Postgres de Compose. Si la API corre **dentro** de Compose, el host es `db` (lo pondrá `docker-compose.yml`).

**Crear el `.env` propio:**
```bash
cd backend
cp .env.example .env
```

**En `.gitignore`:**
```gitignore
.env
.env.*
# Excepción: la plantilla sí se versiona.
!.env.example
```
- En `.gitignore` los comentarios van en su propia línea: un `#` al final de una regla se toma como parte del patrón.
- Comprobar: `git check-ignore -v .env` debe mostrar la regla que lo ignora, y `git status` debe mostrar `.env.example` pero no `.env`.

#### Estructura por capas

```
src/backend/
  main.py        # crea la app y monta los routers
  api/
    routes/      # routers (endpoints), uno por recurso
  core/          # config, seguridad
  db/            # engine, sesión, base
  models/        # modelos SQLAlchemy (tablas)
  schemas/       # modelos Pydantic (entrada/salida de la API)
  services/      # lógica de negocio
```
- Se sigue el layout `src/backend/` que creó `uv init`, en vez de `app/`: el paquete importable se llama `backend` (`from backend.core.config import get_settings`).
- Cada carpeta lleva un **`__init__.py` vacío**: la convierte en paquete importable y, además, git no versiona carpetas vacías.
```bash
cd backend/src/backend
for d in api api/routes db models schemas services; do mkdir -p $d && touch $d/__init__.py; done
```

**Modelos de BD (SQLAlchemy) vs. esquemas de API (Pydantic):**
- **Modelo** (`models/`) = cómo se guarda un dato en la tabla: columnas, claves foráneas, relaciones.
- **Esquema** (`schemas/`) = qué datos entran y salen por la API, y cómo se validan.
- No son lo mismo: al crear un gasto no se envía `id` ni `created_at` (`ExpenseCreate`), al leerlo sí se devuelven (`ExpenseRead`), y en un futuro `User` la contraseña cifrada está en la tabla pero nunca debe salir por la API.
- Separarlos permite cambiar la BD sin romper el contrato con el frontend, y al revés.

#### Routers (`APIRouter`)

**Qué es:** un `APIRouter` agrupa endpoints como si fuera una mini-app. No se ejecuta por sí solo; se monta en la app principal con `include_router`.

`src/backend/api/routes/health.py`:
```python
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

`src/backend/main.py`:
```python
from fastapi import FastAPI

from backend.api.routes import health

app = FastAPI(title="Gastos API")

app.include_router(health.router)
```
- `tags=["health"]` agrupa los endpoints bajo ese título en `/docs`.
- `main.py` queda solo para crear la app y montar routers. Los siguientes se añaden igual, con prefijo: `app.include_router(expenses.router, prefix="/expenses")`.
- El test de `/health` no cambia: importa `app` desde `backend.main` y prueba la API desde fuera, sin importarle en qué fichero está el endpoint.

### Docker en desarrollo

**Objetivo:** levantar Postgres + API con un solo comando (`docker compose up`), con el código montado desde el host para que al guardar un `.py` la API se recargue sola.

**Ficheros:**
```
backend/Dockerfile      # cómo se construye la imagen de la API (dev y prod)
backend/.dockerignore   # qué NO entra en la imagen
docker-compose.yml      # servicios db + api + adminer (raíz del repo)
```

#### Imagen vs. contenedor (repaso)
- **Imagen**: plantilla de solo lectura (sistema base + Python + dependencias + código). Se construye con `docker build` a partir de un `Dockerfile`.
- **Contenedor**: una imagen **en ejecución**, con su propia capa de escritura encima. De una imagen salen tantos contenedores como se quiera.
- Lo que se escribe dentro de un contenedor se pierde al borrarlo, salvo que vaya a un **volumen** o a un **bind mount**.

#### Capas y caché
- Cada instrucción del `Dockerfile` (`FROM`, `COPY`, `RUN`…) crea una **capa**. Docker las guarda en caché.
- Al reconstruir, Docker reutiliza capas hasta llegar a la primera que cambia; **esa y todas las siguientes** se rehacen.
- Por eso el orden importa: primero lo que cambia poco (dependencias), al final lo que cambia mucho (el código).

Mal (cada cambio en un `.py` reinstala todas las dependencias):
```dockerfile
COPY . .
RUN uv sync --locked
```

Bien (las dependencias solo se reinstalan si cambian `pyproject.toml` o `uv.lock`):
```dockerfile
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project
COPY . .
RUN uv sync --locked
```
- `--mount=type=bind` hace visibles esos dos ficheros **solo durante ese `RUN`**, sin crear una capa con ellos.
- `--mount=type=cache,target=/root/.cache/uv` guarda la caché de descargas de uv **entre builds**, sin meterla en la imagen.

#### uv dentro de Docker
- uv se copia desde su imagen oficial, con la misma versión que en local:
```dockerfile
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv
```
- `uv sync --locked`: instala exactamente lo del `uv.lock`, y **falla** si el lock no está al día con el `pyproject.toml` (mejor fallar que instalar otra cosa).
- `--no-install-project`: instala solo las dependencias, no el paquete `backend`. Es la mitad "lenta y estable" del truco de caché.
- `--no-dev`: sin `ruff`, `pytest`… (para producción).
- `--no-editable`: copia el paquete `backend` dentro del `.venv` en vez de enlazar a `src/`. Así la imagen final solo necesita el `.venv`.
- `ENV PATH="/app/.venv/bin:$PATH"`: `uvicorn` y `python` son los del `.venv` sin escribir `uv run`.
- `UV_LINK_MODE=copy`: la caché de uv está en otro mount y no se pueden hacer *hardlinks* entre ellos; sin esto uv da un aviso.

#### Dockerfile multi-stage

**Qué es:** un solo `Dockerfile` con varias etapas (`FROM ... AS nombre`). Cada etapa puede copiar cosas de otra (`COPY --from=etapa`). Con `--target` se elige cuál construir.

```
base ──┬── dev
       └── builder ── prod
```
- **base**: `python:3.13-slim` + uv. Común a todas.
- **dev**: dependencias de desarrollo + `uvicorn --reload`. Es la que usa Compose (`target: dev`).
- **builder**: prepara el `.venv` de producción (sin dev, sin editable, con `.pyc` precompilados). Se descarta.
- **prod**: parte de **otra** `python:3.13-slim` limpia y solo copia el `.venv` del builder.

**Por qué la imagen de producción es más pequeña y segura:**
- No lleva uv, ni cachés, ni herramientas de desarrollo, ni el código fuente suelto: solo lo necesario para ejecutar.
- Menos cosas instaladas = menos superficie de ataque y menos vulnerabilidades que parchear.
- Corre con un usuario sin privilegios (`USER app`), no como root.
- Comparación real: `dev` ≈ 347 MB, `prod` ≈ 234 MB (la mayor parte es la propia imagen de Python).

**Construir cada una a mano** (Compose lo hace solo con la de dev):
```bash
docker build --target dev  -t gastos-api:dev  backend/
docker build --target prod -t gastos-api:prod backend/
```

**`CMD` de producción:**
```dockerfile
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```
- Cloud Run dice en qué puerto escuchar con la variable `PORT`. `${PORT:-8000}` usa 8000 si no existe.
- Hace falta `sh -c` para que se expanda la variable (la forma `["uvicorn", ...]` no expande nada).
- `exec` hace que uvicorn **sustituya** al shell: así recibe él la señal de parada (`SIGTERM`) y se apaga limpiamente.
- `--host 0.0.0.0`: dentro de un contenedor hay que escuchar en todas las interfaces. Con `127.0.0.1` (lo de por defecto) solo se aceptarían conexiones desde dentro del propio contenedor.

#### `.dockerignore`
- Al hacer `docker build`, Docker envía la carpeta entera (el **contexto**) al motor. `.dockerignore` excluye cosas, igual que `.gitignore`.
- Fuera:
  - `.env`: los secretos llegan por variables de entorno, nunca dentro de la imagen.
  - `.venv/`: es el del host, con rutas y binarios que no sirven dentro del contenedor.
  - cachés y `__pycache__`.
- Va junto al `Dockerfile`, en la raíz del contexto (`backend/`).

#### `docker-compose.yml`

**Qué es:** describe varios contenedores (servicios) y cómo se relacionan, para levantarlos juntos. Va en la raíz del repo porque orquesta piezas de varias carpetas.

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: gastos
      POSTGRES_PASSWORD: gastos
      POSTGRES_DB: gastos
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gastos -d gastos"]
      interval: 5s
      timeout: 5s
      retries: 10

  api:
    build:
      context: ./backend
      target: dev
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://gastos:gastos@db:5432/gastos
      ENVIRONMENT: development
    volumes:
      - ./backend/src:/app/src
    depends_on:
      db:
        condition: service_healthy

  adminer:
    image: adminer
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  pgdata:
```
- `ports: "HOST:CONTENEDOR"` publica un puerto del contenedor en el host. `5432` se publica para poder conectar desde fuera (uvicorn local, tests, un cliente SQL).
- Las variables de `environment` tienen prioridad sobre el `.env` (pydantic-settings lee primero el entorno).
- Las credenciales `gastos/gastos` son solo para local. En la nube irán en Secret Manager.
- **Adminer** → `http://localhost:8080`. Sistema: PostgreSQL, Servidor: `db`, Usuario/Contraseña/BD: `gastos`.

#### Bind mount vs. volumen nombrado

| | Bind mount | Volumen nombrado |
|---|---|---|
| Sintaxis | `./backend/src:/app/src` | `pgdata:/var/...` |
| Dónde vive | Carpeta tuya del host | La gestiona Docker |
| Para qué | Código en desarrollo | Datos (la BD) |

- **Bind mount**: el contenedor ve tu carpeta real. Lo que guardas en el editor aparece al instante dentro → `--reload` lo detecta y reinicia.
- **Volumen nombrado**: Docker lo guarda aparte (`docker volume ls`). Sobrevive a que se borre el contenedor, por eso los datos de Postgres no se pierden con `down`.
- Solo se monta `src/`, **no** todo `backend/`: si no, el `.venv` del host taparía el `.venv` del contenedor, y el del host no funciona dentro (rutas y Python distintos).
- En `dev` se pone `PYTHONDONTWRITEBYTECODE=1`: el contenedor corre como root y, sin esto, crearía carpetas `__pycache__` de root dentro de tu `src/`.

#### Redes en Compose: `db` y no `localhost`
- Compose crea una red privada para el proyecto y mete en ella todos los servicios.
- En esa red hay un DNS interno: **cada servicio se alcanza por su nombre**. Desde `api`, Postgres está en `db:5432`.
- `localhost` dentro de un contenedor es **el propio contenedor**. Desde `api`, `localhost:5432` no tiene nada.
- Por eso hay dos URLs:
  - uvicorn en local (fuera de Docker) → `.env` con `localhost:5432` (usa el puerto publicado).
  - API dentro de Compose → `environment` con `db:5432`.
- El puerto interno (`5432` en `db:5432`) es el del contenedor; el `ports:` solo hace falta para entrar **desde el host**.

#### `healthcheck` + `depends_on`
- `depends_on: [db]` solo espera a que el contenedor de `db` **arranque**, no a que Postgres esté listo. Postgres tarda unos segundos en aceptar conexiones.
- El `healthcheck` ejecuta `pg_isready` cada 5 s. Cuando responde bien, el servicio pasa a `healthy`.
- `condition: service_healthy` hace que `api` no arranque hasta entonces. Se ve en `docker compose ps` → `Up (healthy)`.

#### Comandos del día a día
Desde la raíz del repo:
```bash
docker compose up -d           # levantar en 2.º plano
docker compose up -d --build   # ídem, reconstruyendo la imagen
docker compose ps              # estado de los servicios
docker compose logs -f api     # seguir logs (Ctrl+C sale)
docker compose exec api bash   # shell dentro del contenedor
docker compose exec db psql -U gastos   # consola SQL
docker compose restart api     # reiniciar un servicio
docker compose down            # parar y borrar contenedores
docker compose down -v         # ídem + borrar volúmenes
```
- `--build` hace falta al cambiar el `Dockerfile` o las dependencias (`uv add`). Los cambios en `.py` **no** lo necesitan: llegan por el bind mount.
- `exec` entra en un contenedor que ya está corriendo. `run` crea uno nuevo (útil para tareas puntuales).

**`down` vs. `down -v`:**
- `down` borra contenedores y la red, pero **conserva los volúmenes**: al volver a hacer `up`, la BD sigue con sus datos.
- `down -v` borra también los volúmenes: **se pierden los datos** de Postgres. Útil para empezar de cero.
- Comprobar: `docker volume ls` muestra `gastos_python_react_pgdata` tras `down`, pero no tras `down -v`.

#### Problemas típicos
- **`port is already allocated`**: algo del host ya usa ese puerto (p. ej. un `uvicorn` local en el 8000). Pararlo, o cambiar el puerto del host en `ports:`.
- **Añadí una dependencia y la API no la encuentra**: falta reconstruir → `docker compose up -d --build`.
- **No recarga al guardar**: comprobar en `logs -f api` que sale `Will watch for changes` y que el fichero está dentro de `src/` (lo único montado).

### Base de datos: SQLAlchemy + Alembic

**Objetivo:** que la API guarde y lea datos en PostgreSQL usando clases Python (ORM) en vez de SQL a mano, y que los cambios en las tablas queden versionados como migraciones.

#### Dependencias
```bash
uv add sqlalchemy "psycopg[binary]" alembic   # desde backend/
```
- **sqlalchemy**: el **ORM**. Traduce clases Python ↔ tablas y objetos ↔ filas. También gestiona el **pool de conexiones** (el `engine`).
- **psycopg** (v3): el **driver**, lo que de verdad habla con Postgres por la red. SQLAlchemy no se conecta solo, delega en él.
  - Por eso la URL es `postgresql+psycopg://...`: el `+psycopg` le dice a SQLAlchemy qué driver usar.
  - `[binary]` trae `libpq` (la librería C de Postgres) ya compilada. No hay que instalar nada en el sistema ni en la imagen `slim`.
  - Las comillas en `"psycopg[binary]"` evitan que la shell interprete los corchetes.
- **alembic**: **migraciones**. Guarda cada cambio de esquema como un fichero versionado con `upgrade()` y `downgrade()`. Es del mismo autor que SQLAlchemy. Arrastra `mako`, el motor de plantillas con el que genera esos ficheros.
- Las tres son de **producción** (sin `--dev`): la app necesita el ORM y el driver para funcionar, y Alembic se ejecutará en la nube para migrar la BD (Cloud Run Job).

**Comprobar la conexión** (con el Postgres de Compose levantado):
```bash
uv run python -c "
from sqlalchemy import create_engine, text
from backend.core.config import get_settings
engine = create_engine(get_settings().database_url)
with engine.connect() as conn:
    print(conn.execute(text('select version()')).scalar())
"
# PostgreSQL 17.x ...
```

**No olvidar:** dependencias nuevas → reconstruir la imagen de la API, porque el `.venv` vive dentro de ella (el bind mount solo trae `src/`):
```bash
docker compose up -d --build
```

#### `engine`, `Session` y `get_db()`
Código en `src/backend/db/session.py`. Es la "fontanería" entre FastAPI y Postgres, todavía sin modelos ni tablas.

| Pieza | Qué es | Cuántas hay | Vida |
|---|---|---|---|
| `engine` | **Pool de conexiones** a Postgres (usa psycopg por debajo). Al crearse no conecta: abre conexiones cuando se le piden. | 1 por proceso | Toda la vida de la app |
| `SessionLocal` | **Fábrica** de sesiones (`sessionmaker`) atada al engine. `SessionLocal()` → una `Session` nueva. | 1 | Toda la vida de la app |
| `Session` | **Unidad de trabajo**: toma una conexión del pool, lleva la transacción (`commit()` / `rollback()`) y sigue los objetos cargados/añadidos. | 1 por petición HTTP | Lo que dura la petición |
| `get_db()` | **Dependencia** de FastAPI (generador con `yield`): abre la sesión, se la da al endpoint y la cierra al acabar, pase lo que pase. | — | — |

```
GET /gastos ──► FastAPI ve Depends(get_db)
              ──► get_db(): db = SessionLocal()   (pide conexión al pool)
              ──► yield db → el endpoint la usa
              ──► al salir del `with`: db.close() (devuelve la conexión al pool)
```

**Opciones elegidas:**
- `echo=settings.db_echo` → con `DB_ECHO=true` se ve en consola todo el SQL generado. En Compose está activado: `docker compose logs -f api`.
- `pool_pre_ping=True` → antes de reutilizar una conexión del pool hace una comprobación; si Postgres la cerró (reinicio, timeout en Cloud SQL) la descarta en vez de fallar.
- `autoflush=False` → los cambios se mandan a la BD al hacer `commit()`/`flush()`, no "por sorpresa" antes de cada consulta.
- `expire_on_commit=False` → tras `commit()` el objeto conserva sus datos y se puede devolver como respuesta sin otra consulta.

**Uso en un endpoint** (alias `DbSession = Annotated[Session, Depends(get_db)]`):
```python
@router.get("/health/db")
def health_db(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"database": "ok"}
```
Con `DB_ECHO=true` se ve:
```
BEGIN (implicit)   ← SQLAlchemy abre la transacción sola al primer uso
SELECT 1
ROLLBACK           ← al cerrar la sesión sin commit(), se deshace todo
```
→ **sin `commit()` no se guarda nada**. Al escribir datos (B6) habrá que llamar a `db.commit()` explícitamente.

**Por qué `def` y no `async def`:** SQLAlchemy + psycopg se usan aquí en modo síncrono (bloqueante). FastAPI ejecuta las dependencias y endpoints `def` en un hilo aparte, así que no bloquean el servidor.

**Sustituir la dependencia en tests:** `app.dependency_overrides[get_db] = otra_funcion` hace que FastAPI use otra sesión (falsa o contra una BD de pruebas) sin tocar el código de los endpoints. Ver `tests/test_db.py`.
