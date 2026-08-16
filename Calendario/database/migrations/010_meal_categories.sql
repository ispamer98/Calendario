-- Migración: categorías de plato configurables.
--
-- Estaban escritas a fuego en theme.py. Ahora salen de esta tabla y se
-- gestionan desde el formulario de comida, con su color y su icono.
-- Ejecutar en el SQL Editor de Supabase. Es idempotente.

create table if not exists meal_categories (
    id bigint generated always as identity primary key,
    key text not null,
    label text not null,
    color text not null default '#94a3b8',
    icon text not null default 'utensils',
    position integer not null default 0,
    created_at timestamptz not null default now()
);
create unique index if not exists meal_categories_key_lower_key on meal_categories (lower(key));

insert into meal_categories (key, label, color, icon, position) values
    ('arroz','Arroz','#f59e0b','wheat',10),
    ('pasta','Pasta','#fbbf24','wheat',20),
    ('patata','Patata','#d97706','cookie',30),
    ('legumbre','Legumbre','#a16207','bean',40),
    ('carne','Carne','#ef4444','beef',50),
    ('pescado','Pescado','#38bdf8','fish',60),
    ('huevo','Huevo','#eab308','egg',70),
    ('verdura','Verdura','#22c55e','carrot',80),
    ('ensalada','Ensalada','#34d399','salad',90),
    ('sandwich','Bocadillo','#f472b6','sandwich',100),
    ('otros','Otros','#94a3b8','utensils',110)
on conflict (lower(key)) do nothing;
