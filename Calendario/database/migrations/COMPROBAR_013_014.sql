-- Comprobación después de ejecutar EJECUTAR_AHORA_013_014.sql
--
-- Esperado:
--   productos_en_catalogo -> unos cuantos cientos (los ingredientes rescatados)
--   comidas               -> 0  (empezáis todos con el recetario vacío)
--   recetarios            -> 0  (se crean solos al entrar cada usuario)

select
    (select count(*) from products)     as productos_en_catalogo,
    (select count(*) from meals)        as comidas,
    (select count(*) from recipe_books) as recetarios;
