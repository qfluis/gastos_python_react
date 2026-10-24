# TODO — App de gastos (FastAPI + React + Google Cloud)

> **Objetivo:** aprender y entender cada pieza del proceso, no solo que funcione.
> Cada bloque tiene una sección **🎓 Entender** con los conceptos que conviene tener claros antes de pasar al siguiente.

**Stack:** Python · FastAPI · uv · SQLAlchemy · Alembic · PostgreSQL · Docker · React · Vite · TypeScript · Cloud Run · Firebase Hosting · Cloud SQL

**Orden sugerido:** `0` → `Backend 1-6` → `Frontend 1-5` → `Backend 7` + `Frontend 6` (auth) → `Despliegue 1-6`

---

## 0. Preparación del entorno

- [X] Instalar **uv** y comprobar `uv --version`
- [X] Instalar **Node.js LTS** (recomendado vía `nvm` o `fnm`)
- [X] Instalar **Docker Engine** + plugin **Docker Compose**; añadir tu usuario al grupo `docker`
- [X] Instalar extensiones VS Code: Python, Ruff, ESLint, Prettier, Docker
- [X] Definir estructura de monorepo:
  ```
  backend/
  frontend/
  docker-compose.yml
  TODO.md
  ```
- [ ] Crear `.gitignore` (Python, Node, `.env`, `.venv`, `node_modules`, `dist`)

🎓 **Entender**
- ¿Qué es un entorno virtual y por qué cada proyecto Python tiene el suyo?
- ¿Qué diferencia hay entre una **imagen** y un **contenedor** en Docker?
- Monorepo vs. repos separados: ventajas e inconvenientes

---

## 🐍 BACKEND

### B1. Proyecto base FastAPI
- [ ] `uv init` en `backend/` y revisar el `pyproject.toml` generado
- [ ] Añadir dependencias: `fastapi`, `uvicorn[standard]`
- [ ] Crear `app/main.py` con un endpoint `GET /health`
- [ ] Arrancar con `uv run uvicorn app.main:app --reload`
- [ ] Explorar la documentación automática en `/docs` (Swagger) y `/redoc`
- [ ] Ver el esquema crudo en `/openapi.json`

🎓 **Entender**
- `pyproject.toml` y `uv.lock`: qué es cada uno y por qué el lock va a git
- ¿Qué es ASGI y qué papel juega **uvicorn** frente a **FastAPI**?
- `async def` vs `def` en endpoints: cuándo usar cada uno
- ¿Qué es OpenAPI y por qué FastAPI lo genera solo?

### B2. Calidad de código
- [ ] Añadir `ruff` como dependencia de desarrollo (`uv add --dev ruff`)
- [ ] Configurar reglas de ruff en `pyproject.toml`
- [ ] Añadir `pytest` + `httpx` y escribir un test para `/health`
- [ ] (Opcional) `pre-commit` para ejecutar ruff antes de cada commit

🎓 **Entender**
- Dependencias de producción vs. de desarrollo
- `TestClient` de FastAPI: cómo se prueba una API sin levantar servidor

### B3. Configuración y estructura
- [ ] Añadir `pydantic-settings` y crear `app/core/config.py`
- [ ] Leer `DATABASE_URL`, `ENVIRONMENT`, etc. desde variables de entorno / `.env`
- [ ] Crear `.env.example` (versionado) y `.env` (ignorado)
- [ ] Organizar carpetas por capas:
  ```
  app/
    api/        # routers (endpoints)
    core/       # config, seguridad
    db/         # sesión, base
    models/     # modelos SQLAlchemy (tablas)
    schemas/    # modelos Pydantic (entrada/salida API)
    services/   # lógica de negocio
  ```

🎓 **Entender**
- Principio de **12-Factor App**: configuración en el entorno, no en el código
- Por qué separar **modelos de BD** (SQLAlchemy) de **esquemas de API** (Pydantic)

### B4. Docker en desarrollo
- [ ] Escribir `backend/Dockerfile` **multi-stage** con targets `dev` y `prod`
- [ ] Crear `.dockerignore`
- [ ] Crear `docker-compose.yml` con servicios:
  - [ ] `db` → `postgres:17` con volumen persistente
  - [ ] `api` → build target `dev`, bind mount del código, `--reload`
  - [ ] (Opcional) `adminer` para ver la BD desde el navegador
- [ ] Añadir `healthcheck` a `db` y `depends_on: condition: service_healthy` en `api`
- [ ] Comprobar que al guardar un `.py` el contenedor recarga
- [ ] Practicar comandos: `up`, `down`, `logs -f`, `exec`, `down -v`

🎓 **Entender**
- Capas de una imagen y por qué el orden de instrucciones afecta a la caché
- Multi-stage build: por qué la imagen de producción es más pequeña y segura
- **Bind mount** vs **volumen nombrado**
- Redes en Compose: por qué `api` se conecta a `db` usando el host `db` y no `localhost`
- Qué pasa con los datos al hacer `down` vs `down -v`

### B5. Base de datos: SQLAlchemy + Alembic
- [ ] Añadir `sqlalchemy`, `psycopg[binary]`, `alembic`
- [ ] Crear `engine`, `SessionLocal` y dependencia `get_db()` para FastAPI
- [ ] Definir modelos:
  - [ ] `Category` (id, nombre, color/icono)
  - [ ] `Expense` (id, importe, fecha, descripción, category_id, created_at)
- [ ] `alembic init` y configurar `env.py` para leer la URL de config
- [ ] Generar primera migración con `--autogenerate` y **revisarla a mano**
- [ ] Aplicar con `alembic upgrade head` y comprobar las tablas en Adminer
- [ ] Practicar: añadir un campo, generar migración, hacer `downgrade`

🎓 **Entender**
- Qué es un ORM y qué SQL genera por debajo (activar `echo=True` para verlo)
- Por qué el dinero se guarda como `Numeric`/`Decimal` y **nunca** como `float`
- Relaciones 1-N (`Category` → `Expense`) y claves foráneas
- Qué es una migración y por qué no se usa `create_all()` en producción
- Inyección de dependencias en FastAPI (`Depends`)

### B6. API REST (CRUD)
- [ ] Schemas Pydantic: `ExpenseCreate`, `ExpenseUpdate`, `ExpenseRead` (ídem `Category`)
- [ ] Endpoints de categorías: `GET`, `POST`, `PATCH`, `DELETE`
- [ ] Endpoints de gastos: `GET` (lista), `GET /{id}`, `POST`, `PATCH`, `DELETE`
- [ ] Filtros en listado: rango de fechas, categoría
- [ ] Paginación (`limit` / `offset`)
- [ ] Endpoint de resumen: total por categoría y por mes
- [ ] Manejo de errores: 404, 422, respuestas coherentes
- [ ] Tests con BD de pruebas (fixture de pytest)

🎓 **Entender**
- Verbos HTTP y códigos de estado correctos (200, 201, 204, 400, 404, 422)
- `PUT` vs `PATCH`
- Validación automática de Pydantic y de dónde sale el error 422
- `response_model`: por qué controla qué datos salen de la API
- Agregaciones SQL (`GROUP BY`, `SUM`) desde SQLAlchemy

### B7. Autenticación (cuando el front ya funcione)
- [ ] Decidir enfoque: **Firebase Auth** (recomendado para GCP) o JWT propio
- [ ] Añadir modelo `User` y relacionar `Expense.user_id`
- [ ] Dependencia `get_current_user` que valida el token
- [ ] Filtrar todos los datos por usuario
- [ ] Tests de endpoints protegidos

🎓 **Entender**
- Autenticación vs. autorización
- Qué es un JWT, qué contiene y por qué está firmado y no cifrado
- Por qué el backend **nunca** debe confiar en un `user_id` enviado por el cliente

---

## ⚛️ FRONTEND

### F1. Proyecto base
- [ ] `npm create vite@latest` → React + TypeScript en `frontend/`
- [ ] Revisar estructura generada: `index.html`, `main.tsx`, `vite.config.ts`, `tsconfig`
- [ ] Configurar ESLint + Prettier
- [ ] Configurar **proxy de Vite**: `/api` → `http://localhost:8000`
- [ ] Llamar a `/api/health` desde un componente y mostrar el resultado

🎓 **Entender**
- Qué hace Vite en desarrollo (servidor + HMR) vs. en build (genera estáticos)
- Qué es **CORS** y por qué el proxy evita el problema en local
- `package.json` vs `package-lock.json`
- Componentes, props, estado (`useState`) y efectos (`useEffect`)

### F2. UI y estilos
- [ ] Instalar **Tailwind CSS**
- [ ] Inicializar **shadcn/ui** y añadir componentes básicos (Button, Input, Card, Dialog, Table)
- [ ] Layout principal: cabecera, navegación, contenido

🎓 **Entender**
- Enfoque *utility-first* de Tailwind
- Por qué shadcn/ui copia componentes a tu código en vez de instalarlos como librería

### F3. Routing
- [ ] Instalar **React Router**
- [ ] Páginas: Dashboard, Gastos, Categorías
- [ ] Ruta 404

🎓 **Entender**
- SPA: por qué el servidor siempre devuelve `index.html` y el router decide qué pintar

### F4. Comunicación con la API
- [ ] Generar cliente tipado desde `/openapi.json` con **orval** o **openapi-typescript**
- [ ] Añadir script `npm run generate:api`
- [ ] Instalar **TanStack Query** y configurar `QueryClientProvider`
- [ ] Listar categorías y gastos con `useQuery`
- [ ] Crear/editar/borrar con `useMutation` + invalidación de caché
- [ ] Estados de carga y error

🎓 **Entender**
- Estado del servidor vs. estado local de la UI
- Caché, *stale time* y reintentos de TanStack Query
- Por qué generar tipos desde OpenAPI evita errores entre front y back

### F5. Formularios y funcionalidad
- [ ] Instalar **React Hook Form** + **Zod**
- [ ] Formulario de alta/edición de gasto con validación
- [ ] Formulario de categoría
- [ ] Tabla de gastos con filtros (fechas, categoría)
- [ ] Dashboard: totales del mes + gráfico por categoría (p. ej. **Recharts**)
- [ ] Formateo de moneda y fechas con `Intl` (locale `es-ES`)

🎓 **Entender**
- Inputs controlados vs. no controlados
- Validación en cliente (UX) vs. en servidor (seguridad): se necesitan las dos

### F6. Autenticación (junto con B7)
- [ ] Integrar SDK de Firebase Auth (login con Google / email)
- [ ] Contexto de usuario y rutas protegidas
- [ ] Enviar token en cabecera `Authorization: Bearer ...`

🎓 **Entender**
- Dónde vive el token en el navegador y riesgos asociados

---

## ☁️ DESPLIEGUE (Google Cloud)

### D1. Preparar Google Cloud
- [ ] Crear cuenta / proyecto en GCP
- [ ] **Configurar alerta de presupuesto** (p. ej. 10 €) — ¡antes que nada!
- [ ] Instalar `gcloud` CLI y hacer `gcloud init`
- [ ] Habilitar APIs: Cloud Run, Artifact Registry, Cloud SQL Admin, Secret Manager, Cloud Build
- [ ] Elegir región (p. ej. `europe-southwest1` Madrid o `europe-west1`)

🎓 **Entender**
- Proyectos, facturación y cuotas en GCP
- IAM: cuentas de usuario vs. **cuentas de servicio**, roles y principio de mínimo privilegio

### D2. Base de datos en la nube
- [ ] Decidir: **Cloud SQL** (~10 €/mes mínimo) o **Neon/Supabase** (gratis para empezar)
- [ ] Crear instancia + base de datos + usuario
- [ ] Guardar credenciales en **Secret Manager**
- [ ] Ejecutar migraciones contra la BD remota (desde local la primera vez)

🎓 **Entender**
- Por qué la BD es lo único que no escala a cero
- Cómo conecta Cloud Run con Cloud SQL (conector / socket Unix) sin exponer IP pública

### D3. Backend en Cloud Run (manual primero)
- [ ] Crear repositorio en **Artifact Registry**
- [ ] Construir imagen con target `prod` y subirla (`docker push` o `gcloud builds submit`)
- [ ] Desplegar en **Cloud Run** con variables de entorno y secretos montados
- [ ] Asignar cuenta de servicio propia al servicio
- [ ] Probar `/health` y `/docs` en la URL pública
- [ ] Crear **Cloud Run Job** para ejecutar `alembic upgrade head`
- [ ] Revisar logs en **Cloud Logging**

🎓 **Entender**
- Qué es *serverless* para contenedores: escalado a cero y **cold starts**
- Variable `PORT` y por qué el contenedor debe escucharla
- Revisiones y reparto de tráfico (rollback en un clic)
- Por qué las migraciones van en un job aparte y no al arrancar la app

### D4. Frontend en Firebase Hosting
- [ ] Instalar `firebase-tools` y vincular el proyecto GCP
- [ ] `npm run build` y revisar la carpeta `dist/`
- [ ] Configurar `firebase.json`:
  - [ ] *rewrite* `/api/**` → servicio de Cloud Run
  - [ ] *rewrite* `**` → `/index.html` (SPA)
- [ ] `firebase deploy` y probar la app completa
- [ ] (Opcional) Dominio propio

🎓 **Entender**
- Por qué el front es solo archivos estáticos servidos desde una CDN
- Cómo el *rewrite* mantiene front y API en el mismo dominio (sin CORS, igual que en local)

### D5. CI/CD con GitHub Actions
- [ ] Workflow de **CI** en cada PR: ruff + pytest (back), lint + build (front)
- [ ] Configurar **Workload Identity Federation** (sin claves JSON)
- [ ] Workflow de **CD** al hacer push a `main`:
  - [ ] Build + push de imagen a Artifact Registry
  - [ ] Ejecutar job de migraciones
  - [ ] Desplegar nueva revisión en Cloud Run
  - [ ] Build + deploy del front a Firebase Hosting
- [ ] Proteger rama `main` (requerir CI verde)

🎓 **Entender**
- CI vs. CD
- Por qué Workload Identity Federation es más seguro que una clave descargada
- Orden correcto del despliegue: migrar → desplegar back → desplegar front

### D6. Operación
- [ ] Revisar métricas de Cloud Run (latencia, instancias, errores)
- [ ] Configurar backups automáticos de la BD y **probar una restauración**
- [ ] Revisar costes en Billing tras el primer mes
- [ ] Documentar en `README.md` cómo arrancar en local y cómo desplegar

🎓 **Entender**
- Un backup que no se ha restaurado nunca no es un backup fiable

---

## 📝 Notas / dudas

-
