# Importar aquí todos los modelos: con un solo `import backend.models` quedan
# registrados en Base.metadata (lo usará Alembic) y se resuelven las relaciones
# que se nombran como texto ("Expense", "Category"...).
from backend.models.category import Category
from backend.models.cost_center import CostCenter
from backend.models.expense import Expense

__all__ = ["Category", "CostCenter", "Expense"]
