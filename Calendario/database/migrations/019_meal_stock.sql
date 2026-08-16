-- Migración: descontar de la despensa lo que se cocina.
--
-- Cierra el último hueco del circuito. Hasta ahora la despensa sabía lo que
-- entraba (la compra) pero no lo que salía: había que restar a mano lo que te
-- comías, y eso no lo hace nadie. Con esto, cada comida planificada avisa a su
-- hora y descuenta sus ingredientes **con tu autorización**, nunca a tus
-- espaldas.
--
-- Cuatro cosas:
--
-- 1. `products.pack_qty` / `pack_unit` — **la medida exacta con la que se
--    compra** ese producto en el súper (un brik de leche son 1 l, un paquete de
--    arroz 1 kg). Sirve para dos cosas: proponer esa cantidad al guardar algo
--    en la despensa, y poder restar "300 ml" de una despensa que cuenta briks.
--    La `qty` de siempre se queda como lo que pide una receta.
-- 2. `days.meal_consumed` / `dinner_consumed` — si ya se descontó esa comida.
--    Sin esto, dos avisos seguidos restarían la cena dos veces.
-- 3. Ajustes por usuario: si quiere estos avisos y a qué hora (15:00 la comida
--    y 23:00 la cena, por defecto).
-- 4. `meal_reminders` — el registro de avisos ya enviados. Es lo que impide que
--    el recordatorio salga repetido (varios procesos del servidor, reinicios...).
--
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

-- 1) La medida de compra del producto -----------------------------------------
alter table products add column if not exists pack_qty numeric not null default 0;
alter table products add column if not exists pack_unit text not null default '';

-- 2) Qué comidas ya se han descontado, por quién y cuándo ----------------------
-- El "por quién" no es un adorno: en una casa compartida, ver el tick sin saber
-- si lo has restado tú o el otro no vale de nada.
alter table days add column if not exists meal_consumed boolean not null default false;
alter table days add column if not exists dinner_consumed boolean not null default false;
alter table days add column if not exists meal_consumed_by text not null default '';
alter table days add column if not exists dinner_consumed_by text not null default '';
alter table days add column if not exists meal_consumed_at timestamptz;
alter table days add column if not exists dinner_consumed_at timestamptz;

-- Y **qué** se restó exactamente: [{"name": "Arroz", "qty": 0.3, "unit": "kg"}].
-- Sin el detalle, el tick es un acto de fe: no hay forma de comprobar si lo que
-- se descontó era lo que había que descontar.
alter table days add column if not exists meal_consumed_items jsonb not null default '[]'::jsonb;
alter table days add column if not exists dinner_consumed_items jsonb not null default '[]'::jsonb;

-- 3) Ajustes de aviso, por usuario --------------------------------------------
alter table "user" add column if not exists notify_meal_stock boolean not null default true;
alter table "user" add column if not exists meal_notify_time text not null default '15:00';
alter table "user" add column if not exists dinner_notify_time text not null default '23:00';

-- 4) Avisos ya enviados (para no repetirlos) -----------------------------------
create table if not exists meal_reminders (
    id bigint generated always as identity primary key,
    user_id bigint not null,
    day_id bigint not null,
    slot text not null,              -- 'meal' | 'dinner'
    sent_on date not null default current_date,
    created_at timestamptz not null default now()
);

-- La clave de todo: un aviso por usuario, día y comida. El servidor intenta
-- insertar antes de enviar; si choca, es que ya se envió y no manda nada.
create unique index if not exists meal_reminders_unique
    on meal_reminders (user_id, day_id, slot, sent_on);

-- Se consulta "¿qué mandé hoy?", así que el índice va por fecha
create index if not exists meal_reminders_sent_on_idx on meal_reminders (sent_on);
