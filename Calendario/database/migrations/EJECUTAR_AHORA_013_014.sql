-- =====================================================================
--  PEGAR ENTERO EN EL SQL EDITOR DE SUPABASE Y EJECUTAR (una sola vez).
--
--  Junta 013_products.sql y 014_recipe_books.sql en el orden correcto:
--    1) Catálogo de productos  -> los ingredientes salen de una lista
--    2) Recetarios con dueño   -> cada usuario el suyo, compartible
--
--  Es idempotente: si lo ejecutas dos veces no rompe nada.
--
--  OJO AL PEGAR: si al final del editor te aparece un "$0;" suelto (lo mete
--  el editor como marcador de plantilla), BÓRRALO antes de darle a Run. Da
--  este error:  syntax error at or near "$0"
-- =====================================================================


-- =====================================================================
-- 1) CATÁLOGO DE PRODUCTOS
-- =====================================================================
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

-- Semilla 1: los ingredientes que ya usaban tus recetas, con sus datos
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

-- Semilla 2: lo que hubiera suelto en las listas de la compra
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


-- =====================================================================
-- 2) RECETARIOS CON PROPIETARIO
--    Las comidas comunes de antes SE BORRAN (sus ingredientes ya están
--    rescatados arriba, en el catálogo). Cada usuario empieza vacío.
-- =====================================================================
create table if not exists recipe_books (
    id bigint generated always as identity primary key,
    user_ids bigint[] not null default '{}',
    created_at timestamptz not null default now()
);

alter table meals add column if not exists book_id bigint references recipe_books(id) on delete cascade;

-- Los días guardan el NOMBRE del plato: se limpian para no dejar días
-- apuntando a recetas que dejan de existir
update days
   set meal = null
 where meal is not null
   and meal in (select name from meals where book_id is null);

update days
   set dinner = null
 where dinner is not null
   and dinner in (select name from meals where book_id is null);

-- Fuera las comidas sin dueño
delete from meals where book_id is null;

-- El nombre único pasa a serlo DENTRO de cada recetario
drop index if exists meals_name_lower_key;
create unique index if not exists meals_book_name_lower_key on meals (book_id, lower(name));
create index if not exists meals_book_id_idx on meals (book_id);
create index if not exists recipe_books_user_ids_idx on recipe_books using gin (user_ids);

-- FIN. (La comprobación va aparte, en COMPROBAR_013_014.sql, para que este
--  archivo termine en una sentencia sencilla y no se lie al pegarlo.)
