from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.models.expense import Expense


class CostCenter(Base):
    __tablename__ = "cost_centers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    expenses: Mapped[list["Expense"]] = relationship(back_populates="cost_center")
