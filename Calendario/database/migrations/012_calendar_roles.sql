-- Migración: roles en los calendarios (propietario / admin / invitado).
--
-- Hasta ahora `calendars.shared_with` era un array plano: todos los invitados
-- tenían el mismo poder. Esta tabla añade el rol sin tocar ese array (se
-- mantiene sincronizado para no romper nada de lo que ya funciona).
--
--   propietario -> calendars.owner_id (no está en esta tabla)
--   admin       -> puede compartir y expulsar
--   invitado    -> solo ve y edita el contenido
--
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

create table if not exists calendar_members (
    id bigint generated always as identity primary key,
    calendar_id bigint not null references calendars(id) on delete cascade,
    user_id bigint not null references "user"(id) on delete cascade,
    role text not null default 'member' check (role in ('admin', 'member')),
    created_at timestamptz not null default now()
);
create unique index if not exists calendar_members_pair_key on calendar_members (calendar_id, user_id);
create index if not exists calendar_members_user_idx on calendar_members (user_id);

-- Los que ya estaban compartidos entran como invitados
insert into calendar_members (calendar_id, user_id, role)
select c.id, u.user_id, 'member'
from calendars c
cross join lateral unnest(coalesce(c.shared_with, '{}')) as u(user_id)
on conflict (calendar_id, user_id) do nothing;
