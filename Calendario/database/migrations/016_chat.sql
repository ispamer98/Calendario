-- Migración: chat entre amigos.
--
-- Los amigos ya podían mandarse un aviso suelto al móvil, pero el aviso se
-- perdía en cuanto lo cerrabas: no quedaba conversación, ni sabías si lo había
-- leído, ni podías contestar. Esta tabla es esa conversación.
--
-- Puramente aditivo: nada de lo que ya existe cambia de forma.
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

create table if not exists messages (
    id bigint generated always as identity primary key,
    sender_id bigint not null references "user"(id) on delete cascade,
    recipient_id bigint not null references "user"(id) on delete cascade,
    body text not null,
    created_at timestamptz not null default now(),
    read_at timestamptz
);

-- Leer una conversación es "dame los mensajes entre A y B, los últimos
-- primero": el índice por pareja + id sirve para los dos sentidos del or().
create index if not exists messages_sender_idx on messages (sender_id, recipient_id, id desc);
create index if not exists messages_recipient_idx on messages (recipient_id, sender_id, id desc);

-- El contador de "sin leer" de la barra de navegación se pide en cada sondeo,
-- así que tiene que ser barato. Índice parcial: solo las filas sin leer.
create index if not exists messages_unread_idx on messages (recipient_id, sender_id)
    where read_at is null;

-- La app no habla con Postgres directamente, sino con PostgREST, que trabaja
-- con una copia en memoria del esquema. Si esa copia no se refresca, la tabla
-- existe pero la app sigue diciendo que no ("PGRST205"). Esto se lo recuerda.
notify pgrst, 'reload schema';
