-- Migración: tipos de entrada de agenda configurables.
--
-- `item_type` estaba limitado por un CHECK a 'task' | 'event' | 'note'. Ahora
-- los tipos salen de una tabla y se gestionan desde la app, igual que las
-- unidades y los supermercados.
--
-- `completable` marca los tipos que llevan casilla de hecho/pendiente.
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

alter table day_items drop constraint if exists day_items_item_type_check;

create table if not exists task_types (
    id bigint generated always as identity primary key,
    key text not null,
    label text not null,
    color text not null default '#34d399',
    icon text not null default 'list-checks',
    completable boolean not null default false,
    position integer not null default 0,
    created_at timestamptz not null default now()
);
create unique index if not exists task_types_key_lower_key on task_types (lower(key));

insert into task_types (key, label, color, icon, completable, position) values
    ('task',  'Tarea',  '#eab308', 'square-check',   true,  10),
    ('event', 'Evento', '#38bdf8', 'calendar-clock', false, 20),
    ('note',  'Nota',   '#a78bfa', 'sticky-note',    false, 30)
on conflict (lower(key)) do nothing;
