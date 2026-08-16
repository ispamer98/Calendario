-- Migración: tabla de suscripciones a notificaciones push.
-- Sustituye a suscriptores.json (fichero plano que estaba versionado en git).
-- Ejecutar en el SQL Editor de Supabase antes de desplegar el código que la usa.

create table if not exists push_subscriptions (
    id bigint generated always as identity primary key,
    user_id bigint not null references "user"(id) on delete cascade,
    endpoint text not null unique,
    p256dh text not null,
    auth text not null,
    alias text not null default '',
    created_at timestamptz not null default now()
);

create index if not exists push_subscriptions_user_id_idx
    on push_subscriptions (user_id);
