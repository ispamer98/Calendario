-- Migración: franja horaria en la agenda del día.
--
-- `day_items` ya guardaba una hora suelta (`time`). Con `end_time` pasa a ser
-- una franja de verdad: "09:00 – 09:30". Las horas se eligen en tramos de 15
-- minutos y se guardan como texto "HH:MM", igual que `time`.
--
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

alter table day_items add column if not exists end_time text;

-- La agenda se ordena por hora de inicio
create index if not exists day_items_time_idx on day_items (day_id, time);
