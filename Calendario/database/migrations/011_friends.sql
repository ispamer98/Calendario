-- Migración: amistades y preferencia de avisos.
--
-- Puramente aditivo: nada de lo que ya existe cambia de forma.
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

create table if not exists friendships (
    id bigint generated always as identity primary key,
    requester_id bigint not null references "user"(id) on delete cascade,
    addressee_id bigint not null references "user"(id) on delete cascade,
    status text not null default 'pending',   -- pending | accepted
    created_at timestamptz not null default now()
);

-- Una sola solicitud por pareja, mires por donde mires
create unique index if not exists friendships_pair_key
    on friendships (least(requester_id, addressee_id), greatest(requester_id, addressee_id));
create index if not exists friendships_addressee_idx on friendships (addressee_id, status);
create index if not exists friendships_requester_idx on friendships (requester_id, status);

-- Cada uno decide si quiere que le avisen de los cambios en calendarios compartidos
alter table "user" add column if not exists notify_calendar_changes boolean not null default true;
