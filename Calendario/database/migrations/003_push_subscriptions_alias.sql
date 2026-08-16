-- Migración: columna `alias` en push_subscriptions.
--
-- La tabla ya existía en producción pero SIN la columna `alias`, así que
-- cada intento de suscribir un dispositivo desde la campana fallaba con
-- PGRST204 ("Could not find the 'alias' column"). El código lleva un
-- fallback que inserta sin alias si la columna no existe, pero conviene
-- ejecutar esto para poder distinguir los dispositivos en /profile.
--
-- Ejecutar en el SQL Editor de Supabase.

alter table push_subscriptions
    add column if not exists alias text not null default '';

-- El endpoint identifica de forma única a cada navegador/dispositivo:
-- sin esto, volver a suscribir el mismo PC duplicaría filas.
create unique index if not exists push_subscriptions_endpoint_key
    on push_subscriptions (endpoint);
