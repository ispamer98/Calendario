-- Migración: catálogo de productos (los ingredientes preestablecidos).
--
-- Hasta ahora el nombre del ingrediente era texto libre: "Tomate", "tomates" y
-- "Tomate frito" acababan siendo tres productos distintos en la lista de la
-- compra, y no había forma de sumar cantidades. Ahora los ingredientes salen de
-- este catálogo, que se gestiona desde la app (añadir, editar, borrar).
--
-- Cada producto trae sus valores por defecto: al elegirlo en una receta o en la
-- compra, ya vienen puestos la unidad, la sección del súper, el supermercado,
-- si es básico de despensa y la nota. Se pueden cambiar para esa receta sin
-- tocar el catálogo.
--
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

create table if not exists products (
    id bigint generated always as identity primary key,
    name text not null,
    unit text not null default 'ud',
    cat text not null default 'otros',
    shop text not null default '',
    staple boolean not null default false,
    note text not null default '',
    created_at timestamptz not null default now()
);

-- Evita "Tomate" y "tomate" como dos productos distintos
create unique index if not exists products_name_lower_key on products (lower(name));

-- ---------------------------------------------------------------------------
-- Semilla 1: todo lo que ya usaban las recetas, con sus datos actuales.
-- Así al aplicar la migración el catálogo ya está lleno y ninguna receta se
-- queda con un ingrediente "fuera de lista".
-- ---------------------------------------------------------------------------
insert into products (name, unit, cat, shop, staple, note)
select distinct on (lower(ing->>'name'))
       trim(ing->>'name'),
       coalesce(nullif(ing->>'unit', ''), 'ud'),
       coalesce(nullif(ing->>'cat', ''), 'otros'),
       coalesce(ing->>'shop', ''),
       coalesce((ing->>'staple')::boolean, false),
       coalesce(ing->>'note', '')
from meals, jsonb_array_elements(coalesce(meals.ingredients::jsonb, '[]'::jsonb)) as ing
where coalesce(trim(ing->>'name'), '') <> ''
order by lower(ing->>'name'), trim(ing->>'name')
on conflict (lower(name)) do nothing;

-- ---------------------------------------------------------------------------
-- Semilla 2: lo que hubiera suelto en las listas de la compra.
-- ---------------------------------------------------------------------------
insert into products (name, unit, cat, shop, staple, note)
select distinct on (lower(item.key))
       trim(item.key),
       coalesce(nullif(item.value->>'unit', ''), 'ud'),
       coalesce(nullif(item.value->>'cat', ''), 'otros'),
       coalesce(item.value->>'supermarket', ''),
       coalesce((item.value->>'staple')::boolean, false),
       coalesce(item.value->>'note', '')
from shopping_lists, jsonb_each(coalesce(shopping_lists.items::jsonb, '{}'::jsonb)) as item
where coalesce(trim(item.key), '') <> ''
order by lower(item.key), trim(item.key)
on conflict (lower(name)) do nothing;
