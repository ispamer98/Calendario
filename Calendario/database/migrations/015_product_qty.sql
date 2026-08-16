-- Migración: cantidad habitual en el catálogo de productos.
--
-- Al elegir un producto ya se traían su unidad, su sección, su supermercado y
-- su nota. Faltaba la cantidad: si sueles echar 500 ml de caldo, que venga
-- puesto el 500 y no un 1 que hay que corregir siempre.
--
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

alter table products add column if not exists qty numeric not null default 1;
