-- Migración: unidades de medida configurables.
--
-- Las unidades estaban escritas a fuego en el código ("cda", "pizca",
-- "manojo"...). Con esta tabla cada uno pone las suyas y borra las que no usa.
-- Son comunes a toda la app, igual que el recetario.
--
-- Borrar una unidad NO toca los ingredientes que ya la usaban: solo deja de
-- ofrecerse en los desplegables.
--
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

create table if not exists units (
    id bigint generated always as identity primary key,
    name text not null,
    position integer not null default 0,
    created_at timestamptz not null default now()
);

-- Evita "Ud" y "ud" como dos unidades distintas
create unique index if not exists units_name_lower_key on units (lower(name));

-- Semilla con las que usa el catálogo de comidas, para que nada quede huérfano.
-- Quita luego desde la app las que te sobren.
insert into units (name, position) values
    ('ud', 10),
    ('g', 20),
    ('kg', 30),
    ('ml', 40),
    ('l', 50),
    ('lata', 60),
    ('paquete', 70),
    ('bote', 80),
    ('botella', 85),
    ('brik', 87),
    ('bolsa', 88),
    ('bandeja', 90),
    ('cabeza', 95),
    ('cda', 100),
    ('diente', 110),
    ('sobre', 120),
    ('manojo', 130),
    ('pizca', 140)
on conflict (lower(name)) do nothing;
