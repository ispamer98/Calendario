"""
Genera `migrations/005_seed_meals.sql` a partir de `meals_catalog.py`.

    python -m Calendario.database.seeds.generate_sql

El SQL resultante es idempotente: se puede ejecutar las veces que haga falta.
Usa `on conflict (lower(name))` contra el índice único que crea la migración
004, de modo que una comida que ya exista solo recibe categoría, tiempo e
ingredientes — su descripción original se respeta si el catálogo la deja vacía.
"""

import json
from pathlib import Path

from Calendario.database.seeds.meals_catalog import ALL_MEALS, NEW_MEALS, EXISTING_MEALS

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"
OUTPUT = MIGRATIONS_DIR / "005_seed_meals.sql"

HEADER = """-- Migración: catálogo de comidas con ingredientes.
--
-- {n_new} comidas nuevas (arroz, pasta, boniato, legumbres, carne, pescado,
-- huevos, verduras, ensaladas y bocadillos) + ingredientes para las {n_old}
-- comidas que ya existían en la base de datos.
--
-- ARCHIVO GENERADO — no editar a mano.
-- Fuente: Calendario/database/seeds/meals_catalog.py
-- Regenerar con: python -m Calendario.database.seeds.generate_sql
--
-- Requiere haber ejecutado antes 004_meal_ingredients.sql.
-- Es idempotente: se puede volver a ejecutar sin duplicar nada.

begin;

"""

FOOTER = """
commit;

-- Comprobación rápida:
--   select category, count(*) from meals group by category order by 2 desc;
"""


def q(value: str) -> str:
    """Literal SQL entrecomillado, escapando comillas simples."""
    return "'" + str(value).replace("'", "''") + "'"


def statement(m: dict) -> str:
    ingredients = json.dumps(m["ingredients"], ensure_ascii=False, separators=(",", ":"))
    return (
        "insert into meals (name, description, category, prep_minutes, ingredients) values\n"
        f"    ({q(m['name'])}, {q(m['description'])}, {q(m['category'])}, {m['prep_minutes']}, {q(ingredients)}::jsonb)\n"
        "on conflict (lower(name)) do update set\n"
        "    category = excluded.category,\n"
        "    prep_minutes = excluded.prep_minutes,\n"
        "    ingredients = excluded.ingredients,\n"
        "    description = case when excluded.description = '' then meals.description else excluded.description end;\n"
    )


def build() -> str:
    parts = [HEADER.format(n_new=len(NEW_MEALS), n_old=len(EXISTING_MEALS))]
    current_category = None
    for m in ALL_MEALS:
        if m["category"] != current_category:
            current_category = m["category"]
            parts.append(f"\n-- ── {current_category.upper()} ──\n")
        parts.append(statement(m))
    parts.append(FOOTER)
    return "\n".join(parts)


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"✅ {OUTPUT} generado ({len(ALL_MEALS)} comidas)")
