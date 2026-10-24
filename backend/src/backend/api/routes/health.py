from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/holiwi")
def holiwi() -> dict[str, str]:
    return {"holiwi": "kiwi"}
