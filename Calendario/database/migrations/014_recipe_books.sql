-- Migración: el recetario deja de ser común y pasa a tener propietario.
--
-- Hasta ahora `meals` era una tabla global: cualquiera veía y editaba las
-- comidas de todos. Ahora funciona igual que la lista de la compra: cada
-- usuario tiene **su** recetario, y al compartirlo con otro usuario los dos
-- recetarios se fusionan en uno solo que ambos ven y editan.
--
-- `recipe_books.user_ids` es la lista de quienes comparten ese recetario, igual
-- que `shopping_lists.user_ids`.
--
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

create table if not exists recipe_books (
    id bigint generated always as identity primary key,
    user_ids bigint[] not null default '{}',
    created_at timestamptz not null default now()
);

alter table meals add column if not exists book_id bigint references recipe_books(id) on delete cascade;

-- ---------------------------------------------------------------------------
-- Borrón y cuenta nueva.
--
-- Las comidas que había eran comunes a todos y no son de nadie en concreto, así
-- que NO se reparten: se borran. Cada usuario empieza con su recetario vacío y
-- se lo va montando (y compartiendo) él.
--
-- Antes de borrarlas se rescatan sus ingredientes al catálogo de productos, que
-- SÍ es común a toda la app: así el desplegable de ingredientes no se queda
-- vacío. Esto funciona tanto si ya ejecutaste 013_products.sql como si no
-- (si la tabla `products` todavía no existe, simplemente no rescata nada, y
-- entonces conviene ejecutar 013 ANTES que esta).
-- ---------------------------------------------------------------------------
do $$
begin
    if to_regclass('public.products') is not null then
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
    end if;
end $$;

-- Los días planificados guardan el NOMBRE del plato, no su id: se limpian para
-- que no quede ningún día apuntando a una receta que ya no existe.
update days
   set meal = null
 where meal is not null
   and meal in (select name from meals where book_id is null);

update days
   set dinner = null
 where dinner is not null
   and dinner in (select name from meals where book_id is null);

-- Fuera las comidas sin dueño (las 126 comunes de antes)
delete from meals where book_id is null;

-- El nombre único pasa a serlo DENTRO de cada recetario: que tu pareja y tú
-- tengáis cada uno vuestra "Paella" antes de compartir es normal.
drop index if exists meals_name_lower_key;
create unique index if not exists meals_book_name_lower_key on meals (book_id, lower(name));
create index if not exists meals_book_id_idx on meals (book_id);

-- Índice para buscar el recetario de un usuario por su id
create index if not exists recipe_books_user_ids_idx on recipe_books using gin (user_ids);
