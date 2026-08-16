"""
Alternativa a ejecutar `005_seed_meals.sql` a mano: siembra el catálogo de
comidas a través de la API de Supabase.

    python -m Calendario.database.seeds.seed_meals          # siembra
    python -m Calendario.database.seeds.seed_meals --dry    # solo muestra

Requiere que las columnas de `004_meal_ingredients.sql` ya existan (la API
REST de Supabase no puede crear columnas, solo el SQL Editor). Si no están,
el script lo detecta y avisa en vez de fallar a medias.
"""

import argparse
import os
import sys

import dotenv
from supabase import create_client

from Calendario.database.seeds.meals_catalog import ALL_MEALS


def main() -> int:
    parser = argparse.ArgumentParser(description="Siembra el catálogo de comidas en Supabase")
    parser.add_argument("--dry", action="store_true", help="No escribe nada, solo informa")
    args = parser.parse_args()

    dotenv.load_dotenv()
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

    existing = client.table("meals").select("id, name, description, ingredients").execute().data
    by_name = {row["name"].lower(): row for row in existing}
    print(f"Comidas en la base de datos: {len(existing)} · en el catálogo: {len(ALL_MEALS)}")

    to_insert = [m for m in ALL_MEALS if m["name"].lower() not in by_name]
    to_update = [m for m in ALL_MEALS if m["name"].lower() in by_name]
    print(f"Se insertarán {len(to_insert)} y se actualizarán {len(to_update)}")

    if args.dry:
        for m in to_insert:
            print(f"  + {m['name']}")
        return 0

    for m in to_insert:
        payload = {
            "name": m["name"],
            "description": m["description"],
            "category": m["category"],
            "prep_minutes": m["prep_minutes"],
            "ingredients": m["ingredients"],
        }
        try:
            client.table("meals").insert(payload).execute()
            print(f"  + {m['name']}")
        except Exception as e:
            if "schema cache" in str(e):
                print(
                    "\n❌ Faltan las columnas de 004_meal_ingredients.sql.\n"
                    "   Ejecuta esa migración en el SQL Editor de Supabase y repite.",
                    file=sys.stderr,
                )
                return 1
            print(f"  ! {m['name']}: {e}", file=sys.stderr)

    for m in to_update:
        row = by_name[m["name"].lower()]
        payload = {
            "category": m["category"],
            "prep_minutes": m["prep_minutes"],
            "ingredients": m["ingredients"],
        }
        # La descripción original manda: el catálogo solo la aporta si la comida es nueva
        if m["description"] and not (row.get("description") or "").strip():
            payload["description"] = m["description"]
        try:
            client.table("meals").update(payload).eq("id", row["id"]).execute()
        except Exception as e:
            print(f"  ! {m['name']}: {e}", file=sys.stderr)

    print("✅ Catálogo sembrado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
