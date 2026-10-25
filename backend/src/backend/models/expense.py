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
