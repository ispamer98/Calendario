-- Migración: supermercados con color.
--
-- El supermercado era texto libre en cada producto, y pintarlo entero en la
-- fila ocupaba media pantalla. Ahora es una lista con su color: en la lista de
-- la compra sale solo un círculo con la inicial, y al tocarlo se ve el nombre.
--
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

create table if not exists supermarkets (
    id bigint generated always as identity primary key,
    name text not null,
    color text not null default '#38bdf8',
    position integer not null default 0,
    created_at timestamptz not null default now()
);

-- Evita "Lidl" y "lidl" como dos supermercados distintos
create unique index if not exists supermarkets_name_lower_key on supermarkets (lower(name));

-- Semilla con los habituales. Bórralos desde la app y pon los tuyos.
insert into supermarkets (name, color, position) values
    ('Mercadona',  '#22c55e', 10),
    ('Lidl',       '#38bdf8', 20),
    ('Aldi',       '#0ea5e9', 30),
    ('Carrefour',  '#3b82f6', 40),
    ('Dia',        '#ef4444', 50),
    ('Alcampo',    '#f97316', 60),
    ('Consum',     '#a78bfa', 70),
    ('Eroski',     '#eab308', 80)
on conflict (lower(name)) do nothing;
