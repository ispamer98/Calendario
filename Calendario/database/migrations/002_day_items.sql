-- Migración: agenda diaria (tareas, eventos y notas por día).
-- Ejecutar en el SQL Editor de Supabase antes de desplegar el código que la usa.

create table if not exists day_items (
    id bigint generated always as identity primary key,
    day_id bigint not null references days(id) on delete cascade,
    calendar_id bigint not null references calendars(id) on delete cascade,
    owner_id bigint not null references "user"(id) on delete cascade,
    item_type text not null default 'task' check (item_type in ('task', 'event', 'note')),
    title text not null,
    description text not null default '',
    time text,
    completed boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists day_items_day_id_idx on day_items (day_id);
create index if not exists day_items_calendar_id_idx on day_items (calendar_id);
