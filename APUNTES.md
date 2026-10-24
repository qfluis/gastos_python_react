# Apuntes

## Python

### uv

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
