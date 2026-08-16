"""
Genera el SQL que deja montado el recetario **compartido** de dos usuarios.

    python -m Calendario.database.seeds.generate_book_sql Ruben Gaby

Sale un único archivo en `migrations/` listo para pegar en el SQL Editor de
Supabase. A diferencia de `generate_sql.py` (que siembra el recetario global de
antes de la migración 014), este:

- resuelve los dos usuarios por nombre en la tabla `user`;
- deja a los dos compartiendo **un solo** `recipe_books`, fusionando lo que ya
  tuvieran igual que hace la app al pulsar "compartir recetario";
- siembra el catálogo común de `products` con la unidad, la sección y la
  cantidad habitual de cada ingrediente;
- mete las comidas del catálogo en ese recetario, con su descripción, su
  categoría, su tiempo y sus ingredientes.

Es idempotente: se puede ejecutar las veces que haga falta. Las comidas se
reconocen por nombre dentro del recetario (índice `meals_book_name_lower_key`),
así que volver a lanzarlo actualiza las que ya estén en vez de duplicarlas.

Requiere haber ejecutado antes: 004, 006, 010, 011, 013, 014 y 015.
"""

import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from Calendario.database.seeds.meals_catalog import ALL_MEALS

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def q(value) -> str:
    """Literal SQL entrecomillado, escapando comillas simples."""
    return "'" + str(value).replace("'", "''") + "'"


def num(value) -> str:
    """Número sin el .0 de los enteros, que en el SQL queda feo."""
    f = float(value)
    return str(int(f)) if f == int(f) else str(f)


def slug(text: str) -> str:
    """'Ruben Gómez' -> 'ruben_gomez', para el nombre del archivo."""
    plano = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() else "_" for c in plano.lower()).strip("_")


# ---------------------------------------------------------------------------
# Catálogo de productos: se deduce de los ingredientes de todas las recetas.
#
# Un mismo producto aparece en muchas recetas con cantidades distintas (160 g de
# arroz aquí, 200 g allí). Para el catálogo se queda la **más repetida**, que es
# la que menos veces habrá que corregir al añadirla a la compra.
# ---------------------------------------------------------------------------
def build_products() -> list[dict]:
    usos: dict[str, list[dict]] = {}
    for m in ALL_MEALS:
        for i in m["ingredients"]:
            usos.setdefault(i["name"].strip(), []).append(i)

    productos = []
    for name, apariciones in usos.items():
        def moda(campo, default):
            valores = [a.get(campo, default) for a in apariciones]
            return Counter(valores).most_common(1)[0][0]

        productos.append({
            "name": name,
            "qty": moda("qty", 1),
            "unit": moda("unit", "ud"),
            "cat": moda("cat", "otros"),
            #Si en alguna receta es despensa básica, lo es en el catálogo: es
            #más molesto que el aceite acabe en la compra cada semana que al revés
            "staple": any(a.get("staple") for a in apariciones),
        })
    return sorted(productos, key=lambda p: (p["cat"], p["name"].lower()))


# ---------------------------------------------------------------------------
# Bloques del SQL
# ---------------------------------------------------------------------------
def header(user_a: str, user_b: str, n_meals: int, n_products: int, pisar: bool) -> str:
    politica = (
        "-- OJO: se ha generado con --pisar. Una comida que ya exista con ese nombre\n"
        "-- se SOBRESCRIBE con la del catálogo (ingredientes, tiempo y categoría),\n"
        "-- así que se pierde lo que se hubiera editado a mano en ella.\n"
        if pisar
        else
        "-- Lo que ya exista no se toca: una comida que ya esté en el recetario con\n"
        "-- ese nombre se queda como está, con sus ingredientes, su tiempo y sus\n"
        "-- notas. Solo se añaden las que faltan. Lo mismo con los productos.\n"
    )
    return f"""\
-- Recetario compartido de {user_a} y {user_b}.
--
-- {n_meals} comidas con su descripción, su categoría, su tiempo de preparación y
-- sus ingredientes, más {n_products} productos en el catálogo común.
--
-- ARCHIVO GENERADO — no editar a mano.
-- Fuente: Calendario/database/seeds/meals_catalog.py
-- Regenerar con: python -m Calendario.database.seeds.generate_book_sql {user_a} {user_b}
--
-- Requiere haber ejecutado antes: 004_meal_ingredients, 006_units,
-- 010_meal_categories, 011_friends, 013_products, 014_recipe_books y
-- 015_product_qty.
--
-- Es idempotente: se puede volver a ejecutar sin duplicar nada. Las comidas se
-- reconocen por nombre DENTRO del recetario (índice meals_book_name_lower_key).
{politica}--
-- Si alguno de los dos nombres no existe en la tabla `user`, el script aborta
-- entero sin tocar nada y dice cuál falta.

begin;
"""


def context_block(user_a: str, user_b: str) -> str:
    """Resuelve los usuarios, deja un único recetario compartido y lo publica en `_ctx`."""
    return f"""
-- ---------------------------------------------------------------------------
-- 1. Los dos usuarios y su recetario compartido
--
-- Se replica lo que hace la app al compartir el recetario: si cada uno tenía el
-- suyo, las recetas del segundo se mueven al del primero (las repetidas por
-- nombre se descartan) y el recetario que queda vacío se elimina.
-- ---------------------------------------------------------------------------
create temp table if not exists _ctx (book_id bigint) on commit drop;
delete from _ctx;

do $ctx$
declare
    v_a    bigint;
    v_b    bigint;
    v_book bigint;
    v_book_b bigint;
    v_ids  bigint[];
begin
    select id into v_a from "user" where lower(username) = lower({q(user_a)}) order by id limit 1;
    select id into v_b from "user" where lower(username) = lower({q(user_b)}) order by id limit 1;

    if v_a is null then
        raise exception 'No hay ningún usuario que se llame %. Míralo con: select id, username from "user";', {q(user_a)};
    end if;
    if v_b is null then
        raise exception 'No hay ningún usuario que se llame %. Míralo con: select id, username from "user";', {q(user_b)};
    end if;
    if v_a = v_b then
        raise exception 'Los dos nombres apuntan al mismo usuario (id %)', v_a;
    end if;

    select id into v_book   from recipe_books where v_a = any(user_ids) order by id limit 1;
    select id into v_book_b from recipe_books where v_b = any(user_ids) order by id limit 1;

    --Si solo tiene recetario el segundo, se aprovecha el suyo
    if v_book is null and v_book_b is not null then
        v_book := v_book_b;
        v_book_b := null;
    end if;

    if v_book is null then
        insert into recipe_books (user_ids) values (array[v_a, v_b]) returning id into v_book;
        raise notice 'Recetario nuevo creado (id %)', v_book;
    end if;

    --Fusión: las recetas del segundo pasan al recetario del primero
    if v_book_b is not null and v_book_b <> v_book then
        delete from meals
         where book_id = v_book_b
           and lower(trim(name)) in (select lower(trim(name)) from meals where book_id = v_book);
        update meals set book_id = v_book where book_id = v_book_b;
        delete from recipe_books where id = v_book_b;
        raise notice 'Recetario % fusionado dentro del %', v_book_b, v_book;
    end if;

    --Los dos figuran como dueños del recetario que queda
    select user_ids into v_ids from recipe_books where id = v_book;
    v_ids := coalesce(v_ids, '{{}}'::bigint[]);
    if not (v_a = any(v_ids)) then v_ids := v_ids || v_a; end if;
    if not (v_b = any(v_ids)) then v_ids := v_ids || v_b; end if;
    update recipe_books set user_ids = v_ids where id = v_book;

    --Y como amigos, que es lo que la app espera de dos que comparten cosas
    if to_regclass('public.friendships') is not null then
        insert into friendships (requester_id, addressee_id, status)
        select v_a, v_b, 'accepted'
         where not exists (
                   select 1 from friendships
                    where least(requester_id, addressee_id) = least(v_a, v_b)
                      and greatest(requester_id, addressee_id) = greatest(v_a, v_b));

        update friendships set status = 'accepted'
         where least(requester_id, addressee_id) = least(v_a, v_b)
           and greatest(requester_id, addressee_id) = greatest(v_a, v_b);
    end if;

    insert into _ctx (book_id) values (v_book);
    raise notice 'Recetario compartido: id=% (usuarios % y %)', v_book, v_a, v_b;
end
$ctx$;
"""


def products_block(products: list[dict]) -> str:
    """Catálogo común de ingredientes preestablecidos."""
    filas = ",\n".join(
        f"    ({q(p['name'])}, {num(p['qty'])}, {q(p['unit'])}, {q(p['cat'])},"
        f" {str(p['staple']).lower()})"
        for p in products
    )
    return f"""
-- ---------------------------------------------------------------------------
-- 2. Catálogo de productos ({len(products)})
--
-- Es común a toda la app, no del recetario: son los ingredientes que salen en
-- el desplegable con su unidad, su sección del súper y la cantidad que se suele
-- gastar. Los marcados como básicos (aceite, sal, especias) no se añaden a la
-- lista de la compra salvo que se pida.
--
-- Un producto que ya exista se respeta tal cual esté: manda lo que haya
-- configurado el usuario.
-- ---------------------------------------------------------------------------
insert into products (name, qty, unit, cat, staple) values
{filas}
on conflict (lower(name)) do nothing;
"""


def ingredients_json(ingredients: list[dict]) -> str:
    """Los ingredientes tal y como los escribe la app: con `shop` y `note`.

    El catálogo no los trae (ninguna receta de serie tiene supermercado ni
    apunte), pero el formulario de comida sí guarda esas claves. Se emiten
    vacías para que una receta sembrada y una escrita a mano sean iguales.
    """
    completos = [
        {
            "name": i["name"],
            "qty": i["qty"],
            "unit": i["unit"],
            "cat": i["cat"],
            "shop": i.get("shop", ""),
            "staple": i.get("staple", False),
            "note": i.get("note", ""),
        }
        for i in ingredients
    ]
    return json.dumps(completos, ensure_ascii=False, separators=(",", ":"))


def meals_block(meals: list[dict], category: str, pisar: bool) -> str:
    filas = []
    for m in meals:
        filas.append(
            f"    ({q(m['name'])}, {q(m['description'])}, {q(m['category'])},"
            f" {int(m['prep_minutes'])}, {q(ingredients_json(m['ingredients']))})"
        )
    cuerpo = ",\n".join(filas)
    conflicto = (
        """on conflict (book_id, lower(name)) do update set
    category     = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients  = excluded.ingredients,
    description  = case when excluded.description = '' then meals.description
                        else excluded.description end;"""
        if pisar
        else "on conflict (book_id, lower(name)) do nothing;"
    )
    return f"""
-- ── {category.upper()} ({len(meals)}) ──
insert into meals (book_id, name, description, category, prep_minutes, ingredients)
select c.book_id, v.name, v.description, v.category, v.prep_minutes, v.ingredients::jsonb
  from _ctx c,
       (values
{cuerpo}
       ) as v(name, description, category, prep_minutes, ingredients)
{conflicto}
"""


def footer(user_a: str, user_b: str) -> str:
    return f"""
commit;

-- ---------------------------------------------------------------------------
-- Comprobación: qué ha quedado en el recetario compartido
-- ---------------------------------------------------------------------------
select b.id                              as recetario,
       (select array_agg(u.username order by u.username)
          from "user" u where u.id = any(b.user_ids)) as comparten,
       count(m.id)                       as comidas,
       count(*) filter (where jsonb_array_length(m.ingredients) > 0) as con_ingredientes,
       round(avg(m.prep_minutes))        as minutos_medios
  from recipe_books b
  left join meals m on m.book_id = b.id
 where (select id from "user" where lower(username) = lower({q(user_a)}) order by id limit 1) = any(b.user_ids)
 group by b.id;

--   Desglose por categoría:
--     select category, count(*) from meals
--      where book_id = (select id from recipe_books
--                        where (select id from "user" where lower(username) = lower({q(user_a)})) = any(user_ids))
--      group by category order by 2 desc;
"""


def build(user_a: str, user_b: str, pisar: bool = False) -> str:
    nombres = [m["name"].strip().lower() for m in ALL_MEALS]
    repes = [n for n, c in Counter(nombres).items() if c > 1]
    if repes:
        #Dos filas con el mismo nombre en un `on conflict do update` revientan
        #con "cannot affect row a second time"
        raise SystemExit(f"Hay comidas repetidas en el catálogo: {repes}")

    products = build_products()
    partes = [header(user_a, user_b, len(ALL_MEALS), len(products), pisar)]
    partes.append(context_block(user_a, user_b))
    partes.append(products_block(products))
    partes.append(
        "\n-- ---------------------------------------------------------------------------\n"
        f"-- 3. Las comidas ({len(ALL_MEALS)}), con su tiempo, su descripción y sus ingredientes\n"
        "-- ---------------------------------------------------------------------------"
    )

    #Agrupadas por categoría, en el orden en que aparecen en el catálogo
    orden: list[str] = []
    por_categoria: dict[str, list[dict]] = {}
    for m in ALL_MEALS:
        if m["category"] not in por_categoria:
            por_categoria[m["category"]] = []
            orden.append(m["category"])
        por_categoria[m["category"]].append(m)

    for categoria in orden:
        partes.append(meals_block(por_categoria[categoria], categoria, pisar))

    partes.append(footer(user_a, user_b))
    return "\n".join(partes)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    #Por defecto NO se pisa nada: si ya hay una comida con ese nombre en el
    #recetario, manda la que está (puede llevar horas de ajustes encima)
    pisar = "--pisar" in sys.argv

    user_a = args[0] if len(args) > 0 else "Ruben"
    user_b = args[1] if len(args) > 1 else "Gaby"
    salida = MIGRATIONS_DIR / f"017_recetario_{slug(user_a)}_{slug(user_b)}.sql"
    salida.write_text(build(user_a, user_b, pisar), encoding="utf-8")
    modo = "sobrescribiendo las que ya existan" if pisar else "sin tocar las que ya existan"
    print(f"✅ {salida} generado ({len(ALL_MEALS)} comidas, {len(build_products())} productos, {modo})")


if __name__ == "__main__":
    main()
