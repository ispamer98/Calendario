-- Migración: catálogo de comidas con ingredientes.
--
-- 100 comidas nuevas (arroz, pasta, boniato, legumbres, carne, pescado,
-- huevos, verduras, ensaladas y bocadillos) + ingredientes para las 25
-- comidas que ya existían en la base de datos.
--
-- ARCHIVO GENERADO — no editar a mano.
-- Fuente: Calendario/database/seeds/meals_catalog.py
-- Regenerar con: python -m Calendario.database.seeds.generate_sql
--
-- Requiere haber ejecutado antes 004_meal_ingredients.sql.
-- Es idempotente: se puede volver a ejecutar sin duplicar nada.

begin;



-- ── ARROZ ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz con pollo', 'Sofríes cebolla y pollo, echas el arroz y el doble de caldo, y a esperar.', 'arroz', 30, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Pechuga de pollo","qty":300,"unit":"g","cat":"carne","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento rojo","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Caldo de pollo","qty":400,"unit":"ml","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz a la cubana', 'Arroz blanco, tomate frito y huevo frito encima. Imbatible.', 'arroz', 20, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Tomate frito","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Huevos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Plátano","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz con verduras', 'Salteas verdura congelada, añades arroz y caldo. Cero esfuerzo.', 'arroz', 25, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Menestra congelada","qty":300,"unit":"g","cat":"congelados","staple":false},{"name":"Cebolla","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Caldo de verduras","qty":400,"unit":"ml","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz con huevo', 'Arroz blanco con dos huevos fritos y un chorro de soja.', 'arroz', 15, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Huevos","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Salsa de soja","qty":2,"unit":"cda","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz al curry', 'Arroz con leche de coco y curry: se hace solo y sabe a restaurante.', 'arroz', 25, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Leche de coco","qty":200,"unit":"ml","cat":"despensa","staple":false},{"name":"Curry en polvo","qty":1,"unit":"cda","cat":"despensa","staple":true},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pechuga de pollo","qty":250,"unit":"g","cat":"carne","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz tres delicias', 'Arroz del día anterior salteado con guisantes, jamón y huevo.', 'arroz', 20, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Guisantes congelados","qty":100,"unit":"g","cat":"congelados","staple":false},{"name":"Jamón cocido","qty":100,"unit":"g","cat":"carne","staple":false},{"name":"Huevos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Zanahoria","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz con atún', 'Arroz blanco, tomate y dos latas de atún. Diez minutos.', 'arroz', 20, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Tomate frito","qty":150,"unit":"g","cat":"despensa","staple":false},{"name":"Cebolla","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz caldoso', 'Más caldo de lo normal y lo dejas melosito. Reconforta.', 'arroz', 35, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Muslos de pollo","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Caldo de pollo","qty":700,"unit":"ml","cat":"despensa","staple":false},{"name":"Pimiento verde","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Tomate triturado","qty":100,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz con champiñones', 'Champiñones laminados salteados con ajo y arroz.', 'arroz', 25, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Champiñones","qty":250,"unit":"g","cat":"verduras","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Caldo de verduras","qty":400,"unit":"ml","cat":"despensa","staple":false},{"name":"Perejil","qty":1,"unit":"manojo","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz con chorizo', 'Chorizo, arroz y caldo. Contundente y baratísimo.', 'arroz', 30, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Chorizo","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimentón","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Caldo de pollo","qty":400,"unit":"ml","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz con gambas', 'Gambas congeladas, ajo y arroz. Sabe a domingo.', 'arroz', 30, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Gambas peladas","qty":250,"unit":"g","cat":"congelados","staple":false},{"name":"Ajo","qty":3,"unit":"diente","cat":"verduras","staple":false},{"name":"Caldo de pescado","qty":400,"unit":"ml","cat":"despensa","staple":false},{"name":"Pimiento rojo","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz negro', 'Con sobre de tinta de calamar y anillas congeladas.', 'arroz', 35, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Anillas de calamar","qty":250,"unit":"g","cat":"congelados","staple":false},{"name":"Tinta de calamar","qty":2,"unit":"sobre","cat":"pescado","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Caldo de pescado","qty":400,"unit":"ml","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Risotto de champiñones', 'El único que pide remover, pero merece la pena.', 'arroz', 35, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Champiñones","qty":250,"unit":"g","cat":"verduras","staple":false},{"name":"Caldo de verduras","qty":600,"unit":"ml","cat":"despensa","staple":false},{"name":"Queso rallado","qty":60,"unit":"g","cat":"lacteos","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Mantequilla","qty":20,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Arroz con brócoli', 'Brócoli hervido con el propio arroz y salteado con ajo.', 'arroz', 25, '[{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Brócoli","qty":300,"unit":"g","cat":"verduras","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Queso rallado","qty":40,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── PASTA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Espaguetis boloñesa', 'Carne picada, tomate y a hervir pasta mientras.', 'pasta', 30, '[{"name":"Espaguetis","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Carne picada","qty":300,"unit":"g","cat":"carne","staple":false},{"name":"Tomate triturado","qty":400,"unit":"g","cat":"despensa","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Zanahoria","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Queso rallado","qty":50,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Espaguetis carbonara', 'Bacon, huevo y queso fuera del fuego. Nada de nata.', 'pasta', 20, '[{"name":"Espaguetis","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Bacon","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Huevos","qty":3,"unit":"ud","cat":"lacteos","staple":false},{"name":"Queso rallado","qty":80,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Macarrones con tomate', 'El clásico de siempre, con chorizo si te apetece.', 'pasta', 20, '[{"name":"Macarrones","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Tomate frito","qty":300,"unit":"g","cat":"despensa","staple":false},{"name":"Queso rallado","qty":50,"unit":"g","cat":"lacteos","staple":false},{"name":"Orégano","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Macarrones con atún', 'Pasta, tomate y dos latas de atún. Receta de urgencia.', 'pasta', 20, '[{"name":"Macarrones","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Tomate frito","qty":250,"unit":"g","cat":"despensa","staple":false},{"name":"Cebolla","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pasta al pesto', 'Hierves pasta, abres el bote de pesto y listo.', 'pasta', 15, '[{"name":"Fusilli","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Pesto","qty":100,"unit":"g","cat":"despensa","staple":false},{"name":"Tomates cherry","qty":150,"unit":"g","cat":"verduras","staple":false},{"name":"Queso rallado","qty":40,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pasta con nata y bacon', 'Nata, bacon y champiñones. Cremosa y rapidísima.', 'pasta', 20, '[{"name":"Tallarines","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Nata líquida","qty":200,"unit":"ml","cat":"lacteos","staple":false},{"name":"Bacon","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Champiñones","qty":150,"unit":"g","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Lasaña de carne', 'Placas precocinadas y bechamel de brik: al horno y fuera.', 'pasta', 45, '[{"name":"Placas de lasaña","qty":12,"unit":"ud","cat":"despensa","staple":false},{"name":"Carne picada","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Tomate triturado","qty":400,"unit":"g","cat":"despensa","staple":false},{"name":"Bechamel","qty":500,"unit":"ml","cat":"despensa","staple":false},{"name":"Queso rallado","qty":100,"unit":"g","cat":"lacteos","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Espaguetis al ajillo', 'Ajo, aceite y guindilla. Tres ingredientes, cero excusas.', 'pasta', 15, '[{"name":"Espaguetis","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Ajo","qty":4,"unit":"diente","cat":"verduras","staple":false},{"name":"Guindilla","qty":1,"unit":"ud","cat":"despensa","staple":true},{"name":"Perejil","qty":1,"unit":"manojo","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Fusilli con verduras', 'Salteas verduras congeladas y las mezclas con la pasta.', 'pasta', 25, '[{"name":"Fusilli","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Calabacín","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento rojo","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Queso rallado","qty":40,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pasta con pollo', 'Tiras de pollo, champiñones y un poco de nata.', 'pasta', 25, '[{"name":"Penne","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Pechuga de pollo","qty":300,"unit":"g","cat":"carne","staple":false},{"name":"Champiñones","qty":150,"unit":"g","cat":"verduras","staple":false},{"name":"Nata líquida","qty":150,"unit":"ml","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Ensalada de pasta', 'Se hace de un día para otro y aguanta perfecta en la nevera.', 'pasta', 20, '[{"name":"Fusilli","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Tomates cherry","qty":150,"unit":"g","cat":"verduras","staple":false},{"name":"Maíz dulce","qty":1,"unit":"lata","cat":"despensa","staple":false},{"name":"Huevos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Aceitunas","qty":80,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Macarrones gratinados', 'Los de ayer con bechamel y queso, cinco minutos de grill.', 'pasta', 30, '[{"name":"Macarrones","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Bechamel","qty":300,"unit":"ml","cat":"despensa","staple":false},{"name":"Queso rallado","qty":100,"unit":"g","cat":"lacteos","staple":false},{"name":"Jamón cocido","qty":100,"unit":"g","cat":"carne","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Noodles con verduras', 'Wok rápido con noodles instantáneos y salsa de soja.', 'pasta', 15, '[{"name":"Noodles","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Verduras para wok","qty":300,"unit":"g","cat":"congelados","staple":false},{"name":"Salsa de soja","qty":3,"unit":"cda","cat":"despensa","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Espaguetis con gambas', 'Gambas congeladas, ajo, guindilla y pasta.', 'pasta', 20, '[{"name":"Espaguetis","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Gambas peladas","qty":250,"unit":"g","cat":"congelados","staple":false},{"name":"Ajo","qty":3,"unit":"diente","cat":"verduras","staple":false},{"name":"Tomates cherry","qty":150,"unit":"g","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── PATATA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Boniato al horno', 'Lo pinchas, 45 min a 200º y ya está. Literalmente cero trabajo.', 'patata', 50, '[{"name":"Boniato","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Boniato con miel', 'Boniato asado con miel y un puñado de nueces por encima.', 'patata', 50, '[{"name":"Boniato","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Miel","qty":2,"unit":"cda","cat":"despensa","staple":false},{"name":"Nueces","qty":50,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Puré de boniato', 'Boniato cocido, chorrito de leche y a machacar.', 'patata', 30, '[{"name":"Boniato","qty":3,"unit":"ud","cat":"verduras","staple":false},{"name":"Leche","qty":100,"unit":"ml","cat":"lacteos","staple":false},{"name":"Mantequilla","qty":20,"unit":"g","cat":"lacteos","staple":false},{"name":"Nuez moscada","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Boniato relleno', 'Boniato asado abierto y relleno de atún y mayonesa.', 'patata', 50, '[{"name":"Boniato","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Mayonesa","qty":2,"unit":"cda","cat":"despensa","staple":false},{"name":"Queso rallado","qty":50,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Chips de boniato', 'En rodajas finas al horno o a la freidora de aire.', 'patata', 30, '[{"name":"Boniato","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimentón","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Patatas al horno', 'Patatas en gajos con especias, 40 minutos y a otra cosa.', 'patata', 45, '[{"name":"Patata","qty":4,"unit":"ud","cat":"verduras","staple":false},{"name":"Romero","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Puré de patata', 'De sobre o cociendo patatas: en ambos casos, cinco minutos.', 'patata', 20, '[{"name":"Patata","qty":4,"unit":"ud","cat":"verduras","staple":false},{"name":"Leche","qty":150,"unit":"ml","cat":"lacteos","staple":false},{"name":"Mantequilla","qty":30,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Patatas guisadas', 'Con chorizo o sin él, en una olla y a fuego lento.', 'patata', 40, '[{"name":"Patata","qty":5,"unit":"ud","cat":"verduras","staple":false},{"name":"Chorizo","qty":100,"unit":"g","cat":"carne","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento verde","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimentón","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Tortilla de boniato', 'Como la de patata pero más dulce y jugosa.', 'patata', 30, '[{"name":"Boniato","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Huevos","qty":5,"unit":"ud","cat":"lacteos","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Patatas rellenas', 'Patatas asadas rellenas de carne picada y queso gratinado.', 'patata', 50, '[{"name":"Patata","qty":4,"unit":"ud","cat":"verduras","staple":false},{"name":"Carne picada","qty":250,"unit":"g","cat":"carne","staple":false},{"name":"Queso rallado","qty":80,"unit":"g","cat":"lacteos","staple":false},{"name":"Tomate frito","qty":100,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Boniato con garbanzos', 'Boniato asado con garbanzos de bote y especias. Muy saciante.', 'patata', 40, '[{"name":"Boniato","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Garbanzos cocidos","qty":1,"unit":"lata","cat":"despensa","staple":false},{"name":"Comino","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Patatas panadera', 'Patata y cebolla en láminas al horno. Acompaña cualquier cosa.', 'patata', 45, '[{"name":"Patata","qty":4,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Vino blanco","qty":100,"unit":"ml","cat":"otros","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── LEGUMBRE ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Lentejas rápidas', 'Bote de lentejas cocidas, sofrito y listo en 15 minutos.', 'legumbre', 20, '[{"name":"Lentejas cocidas","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Zanahoria","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Chorizo","qty":80,"unit":"g","cat":"carne","staple":false},{"name":"Pimentón","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Garbanzos con espinacas', 'Garbanzos de bote, espinacas congeladas y comino.', 'legumbre', 20, '[{"name":"Garbanzos cocidos","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Espinacas congeladas","qty":300,"unit":"g","cat":"congelados","staple":false},{"name":"Ajo","qty":3,"unit":"diente","cat":"verduras","staple":false},{"name":"Comino","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Hummus casero', 'Garbanzos, tahini y limón a la batidora. Con pan de pita.', 'legumbre', 10, '[{"name":"Garbanzos cocidos","qty":1,"unit":"lata","cat":"despensa","staple":false},{"name":"Tahini","qty":2,"unit":"cda","cat":"despensa","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pan de pita","qty":4,"unit":"ud","cat":"panaderia","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Ensalada de garbanzos', 'En frío, con tomate, pepino y atún. Ideal en verano.', 'legumbre', 15, '[{"name":"Garbanzos cocidos","qty":1,"unit":"lata","cat":"despensa","staple":false},{"name":"Tomate","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Pepino","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Atún en lata","qty":1,"unit":"lata","cat":"despensa","staple":false},{"name":"Cebolla","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Alubias con chorizo', 'Alubias de bote con sofrito y chorizo. Cuchara de la buena.', 'legumbre', 25, '[{"name":"Alubias cocidas","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Chorizo","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento verde","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Lentejas con verduras', 'Versión ligera, solo con verdura y un buen chorro de aceite.', 'legumbre', 25, '[{"name":"Lentejas cocidas","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Zanahoria","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Calabacín","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Caldo de verduras","qty":200,"unit":"ml","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Garbanzos al curry', 'Garbanzos con leche de coco y curry. Sabe a mucho más.', 'legumbre', 25, '[{"name":"Garbanzos cocidos","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Leche de coco","qty":200,"unit":"ml","cat":"despensa","staple":false},{"name":"Curry en polvo","qty":1,"unit":"cda","cat":"despensa","staple":true},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Tomate triturado","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Sopa de lentejas', 'Lentejas trituradas con caldo: crema calentita en 20 minutos.', 'legumbre', 25, '[{"name":"Lentejas cocidas","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Caldo de verduras","qty":500,"unit":"ml","cat":"despensa","staple":false},{"name":"Zanahoria","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Patata","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Alubias con atún', 'Alubias blancas, atún, cebolla y vinagre. Sin fuego.', 'legumbre', 10, '[{"name":"Alubias cocidas","qty":1,"unit":"lata","cat":"despensa","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Cebolla","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Vinagre","qty":1,"unit":"cda","cat":"despensa","staple":true},{"name":"Perejil","qty":1,"unit":"manojo","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Chili con carne', 'Carne picada, alubias rojas y especias. Mejor al día siguiente.', 'legumbre', 35, '[{"name":"Carne picada","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Alubias rojas","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Tomate triturado","qty":400,"unit":"g","cat":"despensa","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento rojo","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Comino","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── CARNE ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pollo al limón', 'Pechuga a la sartén con limón y ajo. Diez minutos.', 'carne', 20, '[{"name":"Pechuga de pollo","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pollo a la plancha', 'Lo más básico del mundo, y con especias está buenísimo.', 'carne', 15, '[{"name":"Pechuga de pollo","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Especias variadas","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pechuga empanada', 'Huevo, pan rallado y sartén. Como en casa de tu madre.', 'carne', 25, '[{"name":"Pechuga de pollo","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Pan rallado","qty":100,"unit":"g","cat":"despensa","staple":false},{"name":"Huevos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pollo teriyaki', 'Pollo en dados con salsa teriyaki y arroz al lado.', 'carne', 25, '[{"name":"Pechuga de pollo","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Salsa teriyaki","qty":60,"unit":"ml","cat":"despensa","staple":false},{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Sésamo","qty":1,"unit":"cda","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Alitas al horno', 'Alitas con especias, 35 minutos al horno y a comer con las manos.', 'carne', 45, '[{"name":"Alitas de pollo","qty":800,"unit":"g","cat":"carne","staple":false},{"name":"Pimentón","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Miel","qty":1,"unit":"cda","cat":"despensa","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Muslos asados', 'Muslos con patatas debajo: una bandeja, una comida.', 'carne', 55, '[{"name":"Muslos de pollo","qty":4,"unit":"ud","cat":"carne","staple":false},{"name":"Patata","qty":3,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Vino blanco","qty":100,"unit":"ml","cat":"otros","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Fajitas de pollo', 'Pollo con pimientos y tortillas de trigo. Cada uno se la monta.', 'carne', 25, '[{"name":"Pechuga de pollo","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Tortillas de trigo","qty":6,"unit":"ud","cat":"panaderia","staple":false},{"name":"Pimiento rojo","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento verde","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Queso rallado","qty":80,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Albóndigas con tomate', 'Las compras hechas o las lías en 5 minutos. Con tomate frito.', 'carne', 30, '[{"name":"Carne picada","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Tomate frito","qty":300,"unit":"g","cat":"despensa","staple":false},{"name":"Huevos","qty":1,"unit":"ud","cat":"lacteos","staple":false},{"name":"Pan rallado","qty":50,"unit":"g","cat":"despensa","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Hamburguesa casera', 'Carne picada, pan, queso y lo que pilles en la nevera.', 'carne', 20, '[{"name":"Carne picada","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Pan de hamburguesa","qty":2,"unit":"ud","cat":"panaderia","staple":false},{"name":"Queso en lonchas","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Tomate","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Lechuga","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Filete de ternera', 'A la plancha, vuelta y vuelta, con patatas o ensalada.', 'carne', 15, '[{"name":"Filete de ternera","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Carne guisada', 'Ternera con patatas y zanahoria a fuego lento. Se hace sola.', 'carne', 70, '[{"name":"Ternera para guisar","qty":500,"unit":"g","cat":"carne","staple":false},{"name":"Patata","qty":3,"unit":"ud","cat":"verduras","staple":false},{"name":"Zanahoria","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Vino tinto","qty":100,"unit":"ml","cat":"otros","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Salteado de pavo', 'Pavo en tiras con verduras y soja. Ligero y rápido.', 'carne', 20, '[{"name":"Pavo en filetes","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Verduras para wok","qty":300,"unit":"g","cat":"congelados","staple":false},{"name":"Salsa de soja","qty":2,"unit":"cda","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Lomo a la plancha', 'Lomo de cerdo con ajo y perejil. Cinco minutos por lado.', 'carne', 15, '[{"name":"Lomo de cerdo","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Perejil","qty":1,"unit":"manojo","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pollo al ajillo', 'Pollo troceado con mucho ajo y un chorro de vino blanco.', 'carne', 35, '[{"name":"Pollo troceado","qty":800,"unit":"g","cat":"carne","staple":false},{"name":"Ajo","qty":6,"unit":"diente","cat":"verduras","staple":false},{"name":"Vino blanco","qty":150,"unit":"ml","cat":"otros","staple":false},{"name":"Perejil","qty":1,"unit":"manojo","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── PESCADO ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Salmón al horno', 'Lomos con limón y eneldo, 15 minutos a 200º.', 'pescado', 25, '[{"name":"Salmón","qty":400,"unit":"g","cat":"pescado","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Eneldo","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Merluza a la plancha', 'Con un chorrito de limón y ajo picado por encima.', 'pescado', 15, '[{"name":"Merluza","qty":400,"unit":"g","cat":"pescado","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Bacalao al horno', 'Bacalao con patata panadera debajo. Plato único.', 'pescado', 45, '[{"name":"Bacalao","qty":400,"unit":"g","cat":"pescado","staple":false},{"name":"Patata","qty":3,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimentón","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Atún a la plancha', 'Lomo de atún fresco vuelta y vuelta con soja.', 'pescado', 15, '[{"name":"Atún fresco","qty":400,"unit":"g","cat":"pescado","staple":false},{"name":"Salsa de soja","qty":2,"unit":"cda","cat":"despensa","staple":false},{"name":"Sésamo","qty":1,"unit":"cda","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Lubina al horno', 'Entera con limón y patatas. Impresiona y no tiene mérito.', 'pescado', 40, '[{"name":"Lubina","qty":2,"unit":"ud","cat":"pescado","staple":false},{"name":"Patata","qty":3,"unit":"ud","cat":"verduras","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Vino blanco","qty":100,"unit":"ml","cat":"otros","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Tortilla de atún', 'Huevos, atún y cebolla. Cena resuelta en 10 minutos.', 'pescado', 15, '[{"name":"Huevos","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Cebolla","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Salmón teriyaki', 'Salmón glaseado con teriyaki y arroz blanco.', 'pescado', 25, '[{"name":"Salmón","qty":400,"unit":"g","cat":"pescado","staple":false},{"name":"Salsa teriyaki","qty":60,"unit":"ml","cat":"despensa","staple":false},{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Dorada al horno', 'Con ajo, limón y perejil. Sana y sin complicaciones.', 'pescado', 35, '[{"name":"Dorada","qty":2,"unit":"ud","cat":"pescado","staple":false},{"name":"Ajo","qty":3,"unit":"diente","cat":"verduras","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Perejil","qty":1,"unit":"manojo","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Bacalao con tomate', 'Bacalao desalado en salsa de tomate con cebolla.', 'pescado', 30, '[{"name":"Bacalao","qty":400,"unit":"g","cat":"pescado","staple":false},{"name":"Tomate triturado","qty":400,"unit":"g","cat":"despensa","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento rojo","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Mejillones al vapor', 'Una olla, un dedo de agua y limón. Cinco minutos.', 'pescado', 15, '[{"name":"Mejillones","qty":1000,"unit":"g","cat":"pescado","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Laurel","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── HUEVO ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Huevos revueltos', 'A fuego bajo y removiendo. Con tostada al lado.', 'huevo', 10, '[{"name":"Huevos","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Mantequilla","qty":15,"unit":"g","cat":"lacteos","staple":false},{"name":"Pan de molde","qty":4,"unit":"ud","cat":"panaderia","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Tortilla francesa', 'La cena de emergencia por excelencia.', 'huevo', 10, '[{"name":"Huevos","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Huevos al plato', 'Huevos sobre tomate frito al horno con jamón.', 'huevo', 20, '[{"name":"Huevos","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Tomate frito","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Jamón cocido","qty":100,"unit":"g","cat":"carne","staple":false},{"name":"Queso rallado","qty":50,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Shakshuka', 'Huevos escalfados en salsa de tomate con pimiento y comino.', 'huevo', 25, '[{"name":"Huevos","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Tomate triturado","qty":400,"unit":"g","cat":"despensa","staple":false},{"name":"Pimiento rojo","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Comino","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pan","qty":0.5,"unit":"ud","cat":"panaderia","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Tortilla de calabacín', 'Como la de patata pero más ligera y más rápida.', 'huevo', 25, '[{"name":"Huevos","qty":5,"unit":"ud","cat":"lacteos","staple":false},{"name":"Calabacín","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Huevos rellenos', 'Huevos cocidos rellenos de atún y mayonesa. Se hacen antes.', 'huevo', 20, '[{"name":"Huevos","qty":6,"unit":"ud","cat":"lacteos","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Mayonesa","qty":3,"unit":"cda","cat":"despensa","staple":false},{"name":"Tomate frito","qty":50,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Tortilla de espinacas', 'Con espinacas congeladas y un poco de queso.', 'huevo', 20, '[{"name":"Huevos","qty":5,"unit":"ud","cat":"lacteos","staple":false},{"name":"Espinacas congeladas","qty":200,"unit":"g","cat":"congelados","staple":false},{"name":"Queso rallado","qty":50,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Huevos con atún', 'Huevos cocidos, atún y ensalada. Cero cocina.', 'huevo', 15, '[{"name":"Huevos","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Lechuga","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Tomate","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── VERDURA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Crema de calabacín', 'Calabacín, patata y caldo a la batidora. Infalible.', 'verdura', 30, '[{"name":"Calabacín","qty":3,"unit":"ud","cat":"verduras","staple":false},{"name":"Patata","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Caldo de verduras","qty":500,"unit":"ml","cat":"despensa","staple":false},{"name":"Quesitos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Crema de calabaza', 'Dulce y naranja. Con un poco de nata queda de restaurante.', 'verdura', 35, '[{"name":"Calabaza","qty":600,"unit":"g","cat":"verduras","staple":false},{"name":"Zanahoria","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Caldo de verduras","qty":500,"unit":"ml","cat":"despensa","staple":false},{"name":"Nata líquida","qty":100,"unit":"ml","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Verduras al horno', 'Todo troceado en una bandeja con aceite y sal. 40 minutos.', 'verdura', 45, '[{"name":"Calabacín","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Berenjena","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento rojo","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Patata","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pisto rápido', 'Con verdura ya troceada congelada y tomate frito.', 'verdura', 25, '[{"name":"Pisto congelado","qty":400,"unit":"g","cat":"congelados","staple":false},{"name":"Tomate frito","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Huevos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Salteado de brócoli', 'Brócoli con ajo y guindilla. Crujiente, no papilla.', 'verdura', 15, '[{"name":"Brócoli","qty":400,"unit":"g","cat":"verduras","staple":false},{"name":"Ajo","qty":3,"unit":"diente","cat":"verduras","staple":false},{"name":"Guindilla","qty":1,"unit":"ud","cat":"despensa","staple":true},{"name":"Almendras","qty":40,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Berenjenas rellenas', 'Rellenas de carne picada y gratinadas con queso.', 'verdura', 45, '[{"name":"Berenjena","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Carne picada","qty":300,"unit":"g","cat":"carne","staple":false},{"name":"Tomate frito","qty":150,"unit":"g","cat":"despensa","staple":false},{"name":"Queso rallado","qty":80,"unit":"g","cat":"lacteos","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Espinacas salteadas', 'Espinacas con pasas y piñones. Suena fino, cuesta nada.', 'verdura', 15, '[{"name":"Espinacas congeladas","qty":400,"unit":"g","cat":"congelados","staple":false},{"name":"Pasas","qty":40,"unit":"g","cat":"despensa","staple":false},{"name":"Piñones","qty":30,"unit":"g","cat":"despensa","staple":false},{"name":"Ajo","qty":2,"unit":"diente","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Coliflor al horno', 'En ramilletes con especias, queda crujiente y adictiva.', 'verdura', 40, '[{"name":"Coliflor","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimentón","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Queso rallado","qty":50,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── ENSALADA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Ensalada mixta', 'Lechuga, tomate, atún, maíz y huevo. La de toda la vida.', 'ensalada', 10, '[{"name":"Lechuga","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Tomate","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Maíz dulce","qty":1,"unit":"lata","cat":"despensa","staple":false},{"name":"Huevos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Aceitunas","qty":60,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Ensalada de tomate', 'Tomate bueno, cebolla, aceite y sal. No hace falta más.', 'ensalada', 10, '[{"name":"Tomate","qty":4,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Orégano","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Ensalada de quinoa', 'Quinoa cocida con verduras crudas y limón. Aguanta días.', 'ensalada', 25, '[{"name":"Quinoa","qty":150,"unit":"g","cat":"despensa","staple":false},{"name":"Pepino","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Tomates cherry","qty":150,"unit":"g","cat":"verduras","staple":false},{"name":"Aguacate","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Ensalada campera', 'Patata cocida, tomate, cebolla, atún y huevo. Muy de verano.', 'ensalada', 30, '[{"name":"Patata","qty":3,"unit":"ud","cat":"verduras","staple":false},{"name":"Tomate","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Atún en lata","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Huevos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Ensalada de aguacate', 'Aguacate, tomate cherry, cebolla morada y lima.', 'ensalada', 10, '[{"name":"Aguacate","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Tomates cherry","qty":200,"unit":"g","cat":"verduras","staple":false},{"name":"Cebolla morada","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Lima","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Salmorejo', 'Tomate, pan, ajo y aceite a la batidora. Con jamón y huevo.', 'ensalada', 15, '[{"name":"Tomate","qty":8,"unit":"ud","cat":"verduras","staple":false},{"name":"Pan","qty":200,"unit":"g","cat":"panaderia","staple":false},{"name":"Ajo","qty":1,"unit":"diente","cat":"verduras","staple":false},{"name":"Jamón serrano","qty":80,"unit":"g","cat":"carne","staple":false},{"name":"Huevos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── SANDWICH ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Sándwich mixto', 'Jamón y queso a la plancha. La cena de los días perdidos.', 'sandwich', 10, '[{"name":"Pan de molde","qty":4,"unit":"ud","cat":"panaderia","staple":false},{"name":"Jamón cocido","qty":100,"unit":"g","cat":"carne","staple":false},{"name":"Queso en lonchas","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Mantequilla","qty":15,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Wrap de pollo', 'Tortilla de trigo con pollo, lechuga y salsa césar.', 'sandwich', 15, '[{"name":"Tortillas de trigo","qty":4,"unit":"ud","cat":"panaderia","staple":false},{"name":"Pechuga de pollo","qty":300,"unit":"g","cat":"carne","staple":false},{"name":"Lechuga","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Salsa césar","qty":3,"unit":"cda","cat":"despensa","staple":false},{"name":"Tomate","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Bocadillo de tortilla', 'Tortilla francesa dentro de una barra. Sagrado.', 'sandwich', 15, '[{"name":"Pan","qty":1,"unit":"ud","cat":"panaderia","staple":false},{"name":"Huevos","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Tomate","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Tostada de aguacate', 'Pan tostado con aguacate machacado y huevo poché.', 'sandwich', 15, '[{"name":"Pan","qty":0.5,"unit":"ud","cat":"panaderia","staple":false},{"name":"Aguacate","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Huevos","qty":2,"unit":"ud","cat":"lacteos","staple":false},{"name":"Limón","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── OTROS ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pizza', '', 'otros', 20, '[{"name":"Pizza congelada","qty":2,"unit":"ud","cat":"congelados","staple":false},{"name":"Queso rallado","qty":50,"unit":"g","cat":"lacteos","staple":false},{"name":"Orégano","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── ENSALADA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Ensalada César', '', 'ensalada', 20, '[{"name":"Lechuga romana","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pechuga de pollo","qty":300,"unit":"g","cat":"carne","staple":false},{"name":"Salsa césar","qty":4,"unit":"cda","cat":"despensa","staple":false},{"name":"Picatostes","qty":80,"unit":"g","cat":"panaderia","staple":false},{"name":"Queso parmesano","qty":50,"unit":"g","cat":"lacteos","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── VERDURA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Sopa de verduras', '', 'verdura', 35, '[{"name":"Puerro","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Zanahoria","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Patata","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Judías verdes","qty":200,"unit":"g","cat":"verduras","staple":false},{"name":"Caldo de verduras","qty":700,"unit":"ml","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── CARNE ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pollo al horno', '', 'carne', 60, '[{"name":"Pollo troceado","qty":1000,"unit":"g","cat":"carne","staple":false},{"name":"Patata","qty":4,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Vino blanco","qty":100,"unit":"ml","cat":"otros","staple":false},{"name":"Limón","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── ARROZ ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Paella', '', 'arroz', 60, '[{"name":"Arroz","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Pollo troceado","qty":400,"unit":"g","cat":"carne","staple":false},{"name":"Gambas peladas","qty":200,"unit":"g","cat":"congelados","staple":false},{"name":"Judías verdes","qty":150,"unit":"g","cat":"verduras","staple":false},{"name":"Pimiento rojo","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Azafrán","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Caldo de pescado","qty":500,"unit":"ml","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── ENSALADA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Gazpacho', '', 'ensalada', 15, '[{"name":"Tomate","qty":8,"unit":"ud","cat":"verduras","staple":false},{"name":"Pepino","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento verde","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Ajo","qty":1,"unit":"diente","cat":"verduras","staple":false},{"name":"Pan","qty":100,"unit":"g","cat":"panaderia","staple":false},{"name":"Vinagre","qty":1,"unit":"cda","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── HUEVO ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Tortilla de patata', '', 'huevo', 40, '[{"name":"Patata","qty":4,"unit":"ud","cat":"verduras","staple":false},{"name":"Huevos","qty":6,"unit":"ud","cat":"lacteos","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── OTROS ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Jamón ibérico', '', 'otros', 5, '[{"name":"Jamón ibérico","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Pan","qty":0.5,"unit":"ud","cat":"panaderia","staple":false},{"name":"Tomate","qty":1,"unit":"ud","cat":"verduras","staple":false}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── PATATA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Patatas bravas', '', 'patata', 35, '[{"name":"Patata","qty":5,"unit":"ud","cat":"verduras","staple":false},{"name":"Salsa brava","qty":100,"unit":"g","cat":"despensa","staple":false},{"name":"Mayonesa","qty":3,"unit":"cda","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── LEGUMBRE ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Cocido', '', 'legumbre', 90, '[{"name":"Garbanzos cocidos","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Morcillo de ternera","qty":300,"unit":"g","cat":"carne","staple":false},{"name":"Chorizo","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Morcilla","qty":1,"unit":"ud","cat":"carne","staple":false},{"name":"Repollo","qty":0.5,"unit":"ud","cat":"verduras","staple":false},{"name":"Patata","qty":3,"unit":"ud","cat":"verduras","staple":false},{"name":"Zanahoria","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Fideos","qty":80,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Fabada asturiana', '', 'legumbre', 60, '[{"name":"Alubias cocidas","qty":3,"unit":"lata","cat":"despensa","staple":false},{"name":"Chorizo","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Morcilla","qty":1,"unit":"ud","cat":"carne","staple":false},{"name":"Panceta","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Pimentón","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── HUEVO ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Huevos rotos', '', 'huevo', 25, '[{"name":"Patata","qty":4,"unit":"ud","cat":"verduras","staple":false},{"name":"Huevos","qty":4,"unit":"ud","cat":"lacteos","staple":false},{"name":"Jamón serrano","qty":100,"unit":"g","cat":"carne","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── PESCADO ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Gambas al ajillo', '', 'pescado', 15, '[{"name":"Gambas peladas","qty":400,"unit":"g","cat":"congelados","staple":false},{"name":"Ajo","qty":5,"unit":"diente","cat":"verduras","staple":false},{"name":"Guindilla","qty":1,"unit":"ud","cat":"despensa","staple":true},{"name":"Pan","qty":0.5,"unit":"ud","cat":"panaderia","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Calamares en su tinta', '', 'pescado', 45, '[{"name":"Anillas de calamar","qty":500,"unit":"g","cat":"congelados","staple":false},{"name":"Tinta de calamar","qty":2,"unit":"sobre","cat":"pescado","staple":false},{"name":"Cebolla","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Tomate triturado","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Arroz","qty":160,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── OTROS ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Migas', '', 'otros', 40, '[{"name":"Pan","qty":400,"unit":"g","cat":"panaderia","staple":false},{"name":"Chorizo","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Panceta","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Ajo","qty":4,"unit":"diente","cat":"verduras","staple":false},{"name":"Pimentón","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── PASTA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Fideuà', '', 'pasta', 45, '[{"name":"Fideos","qty":250,"unit":"g","cat":"despensa","staple":false},{"name":"Gambas peladas","qty":250,"unit":"g","cat":"congelados","staple":false},{"name":"Anillas de calamar","qty":200,"unit":"g","cat":"congelados","staple":false},{"name":"Caldo de pescado","qty":600,"unit":"ml","cat":"despensa","staple":false},{"name":"Tomate triturado","qty":150,"unit":"g","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── VERDURA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Escalivada', '', 'verdura', 60, '[{"name":"Berenjena","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento rojo","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── PESCADO ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Escabeche', '', 'pescado', 40, '[{"name":"Bonito","qty":400,"unit":"g","cat":"pescado","staple":false},{"name":"Cebolla","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Zanahoria","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Vinagre","qty":100,"unit":"ml","cat":"despensa","staple":false},{"name":"Laurel","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── LEGUMBRE ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Ropa vieja', '', 'legumbre', 30, '[{"name":"Garbanzos cocidos","qty":2,"unit":"lata","cat":"despensa","staple":false},{"name":"Carne de cocido","qty":300,"unit":"g","cat":"carne","staple":false},{"name":"Tomate frito","qty":200,"unit":"g","cat":"despensa","staple":false},{"name":"Pimiento verde","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── PESCADO ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Marmitako', '', 'pescado', 50, '[{"name":"Bonito","qty":400,"unit":"g","cat":"pescado","staple":false},{"name":"Patata","qty":4,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento verde","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Caldo de pescado","qty":500,"unit":"ml","cat":"despensa","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── VERDURA ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Pisto manchego', '', 'verdura', 45, '[{"name":"Calabacín","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Berenjena","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento rojo","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Pimiento verde","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Tomate triturado","qty":400,"unit":"g","cat":"despensa","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── LEGUMBRE ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Caparrones', '', 'legumbre', 60, '[{"name":"Alubias rojas","qty":3,"unit":"lata","cat":"despensa","staple":false},{"name":"Chorizo","qty":150,"unit":"g","cat":"carne","staple":false},{"name":"Panceta","qty":100,"unit":"g","cat":"carne","staple":false},{"name":"Cebolla","qty":1,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── CARNE ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Chistorra', '', 'carne', 15, '[{"name":"Chistorra","qty":300,"unit":"g","cat":"carne","staple":false},{"name":"Pan","qty":0.5,"unit":"ud","cat":"panaderia","staple":false},{"name":"Patata","qty":3,"unit":"ud","cat":"verduras","staple":false}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Morcilla', '', 'carne', 20, '[{"name":"Morcilla","qty":2,"unit":"ud","cat":"carne","staple":false},{"name":"Pan","qty":0.5,"unit":"ud","cat":"panaderia","staple":false},{"name":"Pimiento verde","qty":2,"unit":"ud","cat":"verduras","staple":false},{"name":"Aceite de oliva","qty":2,"unit":"cda","cat":"despensa","staple":true},{"name":"Sal","qty":1,"unit":"pizca","cat":"despensa","staple":true},{"name":"Pimienta","qty":1,"unit":"pizca","cat":"despensa","staple":true}]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


-- ── OTROS ──

insert into meals (name, description, category, prep_minutes, ingredients) values
    ('Burguer King', '', 'otros', 5, '[]'::jsonb)
on conflict (lower(name)) do update set
    category = excluded.category,
    prep_minutes = excluded.prep_minutes,
    ingredients = excluded.ingredients,
    description = case when excluded.description = '' then meals.description else excluded.description end;


commit;

-- Comprobación rápida:
--   select category, count(*) from meals group by category order by 2 desc;
