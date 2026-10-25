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
