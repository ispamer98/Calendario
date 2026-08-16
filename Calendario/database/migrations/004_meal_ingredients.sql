-- Migración: ingredientes estructurados en las comidas.
--
-- Es lo que permite que el menú semanal genere automáticamente la lista de
-- la compra: cada comida guarda su lista de ingredientes en JSON y el
-- generador los agrega por (nombre, unidad).
--
-- Formato de `ingredients` (array de objetos):
--   [{"name": "Arroz", "qty": 160, "unit": "g", "cat": "despensa", "staple": false}]
--     name   -> nombre canónico del producto (se agrega por él)
--     qty    -> cantidad para 2 personas
--     unit   -> g | ml | ud | lata | diente | cda | pizca | sobre | manojo
--     cat    -> sección del súper: verduras, carne, pescado, lacteos,
--               despensa, congelados, panaderia, otros
--     staple -> despensa básica (aceite, sal, especias): no se añade a la
--               lista salvo que se pida expresamente
--
-- Ejecutar en el SQL Editor de Supabase ANTES de 005_seed_meals.sql.

alter table meals add column if not exists ingredients jsonb not null default '[]'::jsonb;
alter table meals add column if not exists category text not null default 'otros';
alter table meals add column if not exists prep_minutes integer not null default 20;

-- Evita comidas duplicadas con distinta capitalización ("Paella" / "paella"),
-- que romperían la agregación de la lista de la compra.
create unique index if not exists meals_name_lower_key on meals (lower(name));
