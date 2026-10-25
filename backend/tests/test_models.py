from sqlalchemy import Numeric

import backend.models  # noqa: F401  (registra los modelos en Base.metadata)
from backend.db.base import Base

# No necesita Postgres: solo inspecciona la descripción de las tablas.
tables = Base.metadata.tables


def test_existen_las_tablas() -> None:
    assert set(tables) == {"categories", "cost_centers", "expenses"}


def test_importe_es_numeric_y_no_float() -> None:
    amount = tables["expenses"].c.amount

    assert isinstance(amount.type, Numeric)
    assert (amount.type.precision, amount.type.scale) == (12, 2)
    assert amount.type.asdecimal  # devuelve Decimal en Python


def test_gasto_tiene_categoria_y_centro_de_coste_obligatorios() -> None:
    expenses = tables["expenses"]

    for column, target in [
        ("category_id", "categories.id"),
        ("cost_center_id", "cost_centers.id"),
    ]:
        col = expenses.c[column]
        assert not col.nullable
        assert {fk.target_fullname for fk in col.foreign_keys} == {target}


def test_color_de_categoria_es_opcional() -> None:
    assert tables["categories"].c.color.nullable
