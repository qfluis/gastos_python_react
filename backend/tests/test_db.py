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
