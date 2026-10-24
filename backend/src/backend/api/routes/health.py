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
