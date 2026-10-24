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

## Node.js

### Versiones: LTS vs. actual
- Las versiones **pares** (20, 22, 24…) pasan a **LTS** (*Long Term Support*): unos 30 meses de soporte. Son las que se usan en proyectos.
- Las **impares** (19, 21, 23…) duran solo unos 6 meses y nunca llegan a LTS. No conviene usarlas.

### fnm (gestor de versiones de Node)

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

## Docker

### Docker Engine + Docker Compose

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

## VS Code

### Extensiones VSC

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
