-- Migración: la despensa (el "stock" de casa).
--
-- La lista de la compra sabía qué falta, pero nadie sabía qué HAY. Cada semana
-- tocaba abrir la nevera y el armario para decidir si hacía falta leche, y aun
-- así se compraba dos veces lo mismo.
--
-- Esta tabla guarda lo que hay en casa. Se llena sola: al marcar un producto
-- como comprado en la lista, su cantidad se suma aquí (y si lo desmarcas, se
-- resta, porque desmarcar es deshacer). Cada producto sabe además dónde se
-- guarda (nevera, congelador, despensa), cuándo caduca y por debajo de qué
-- cantidad hay que reponerlo.
--
-- Es una lista **independiente**, con la misma forma y las mismas reglas que la
-- de la compra: `user_ids` + un JSON con los productos, y se comparte igual
-- (por nombre de usuario, fusionando el stock del otro). Compartir la compra no
-- comparte la despensa ni al revés: cada una lleva su propia gente.
--
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

create table if not exists pantries (
    id bigint generated always as identity primary key,
    user_ids bigint[] not null default '{}',
    items jsonb not null default '{}'::jsonb,
    -- Sumar a la despensa al marcar algo como comprado. Se apaga desde la app
    -- si prefieres llevar el stock a mano.
    auto_stock boolean not null default true,
    created_at timestamptz not null default now()
);

-- Se busca siempre por "¿de qué despensa formo parte?"
create index if not exists pantries_user_ids_idx on pantries using gin (user_ids);

-- ---------------------------------------------------------------------------
-- Una despensa vacía para cada usuario. Cada uno empieza con la suya y decide
-- con quién la comparte desde la app, igual que con la lista de la compra.
--
-- El `&&` (¿está ya este usuario en alguna despensa?) es lo que lo hace
-- idempotente: se puede volver a ejecutar sin duplicar nada.
--
-- Los `::bigint[]` no son adorno: los `user_ids` que ya hay en la base son
-- `integer[]` y `&&` exige que los dos lados sean del mismo tipo, así que sin
-- castear falla con "operator does not exist: bigint[] && integer[]".
-- ---------------------------------------------------------------------------
insert into pantries (user_ids, items)
select array[u.id]::bigint[], '{}'::jsonb
from "user" u
where not exists (
    select 1 from pantries p where p.user_ids && array[u.id]::bigint[]
);
