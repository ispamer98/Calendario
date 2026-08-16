# Migraciones de CalendPy

Estos `.sql` **no se aplican solos**: la app habla con Supabase por su API REST,
que no puede crear tablas ni columnas. Hay que pegarlos en el **SQL Editor** de
Supabase y ejecutarlos, en orden.

Estado comprobado contra la base de datos el 2026-08-12: de la `001` a la `016`
están todas aplicadas. Pendientes: la `017`, la `018` y la `019`. La `017` es
independiente; la `019` **necesita la `018`** (descuenta de la despensa), así que
esas dos van en ese orden.

Todos son idempotentes (`if not exists`, `on conflict`): se pueden volver a
ejecutar sin romper nada.

| Archivo | Qué hace | Estado |
|---|---|---|
| `001_push_subscriptions.sql` | Tabla de suscripciones push | Aplicada (la tabla existe) |
| `002_day_items.sql` | Agenda diaria (tareas/eventos/notas) | Aplicada |
| `003_push_subscriptions_alias.sql` | **Añade `alias` a `push_subscriptions`** | Aplicada |
| `004_meal_ingredients.sql` | Columnas `ingredients`, `category`, `prep_minutes` en `meals` | Aplicada |
| `005_seed_meals.sql` | 100 comidas nuevas + ingredientes de las 25 que ya había | Aplicada, pero **anulada por la 014** (borró las comidas sin dueño). Ver `017` |
| `006_units.sql` | Tabla `units`: unidades de medida editables desde la app | Aplicada |
| `007_supermarkets.sql` | Tabla `supermarkets`: supermercados con color | Aplicada |
| `008_day_item_end_time.sql` | `end_time` en `day_items`: franjas horarias | Aplicada |
| `009_task_types.sql` | Tabla `task_types`: tipos de agenda configurables | Aplicada |
| `010_meal_categories.sql` | Tabla `meal_categories`: categorías de plato configurables | Aplicada |
| `011_friends.sql` | Tabla `friendships` | Aplicada |
| `012_calendar_roles.sql` | Tabla `calendar_members`: roles por calendario | Aplicada |
| `013_products.sql` | **Catálogo de productos**: los ingredientes dejan de ser texto libre | Aplicada |
| `014_recipe_books.sql` | **Recetario con propietario**: `recipe_books` + `meals.book_id` | Aplicada |
| `015_product_qty.sql` | `qty` en `products`: cantidad habitual del producto | Aplicada |
| `016_chat.sql` | **Chat entre amigos**: tabla `messages` | Aplicada |
| `017_recetario_ruben_gaby.sql` | Recetario **compartido** de Ruben y Gaby: 125 comidas + 132 productos | ⚠️ Pendiente (sus requisitos, de la 004 a la 015, ya están puestos) |
| `018_pantry.sql` | **Despensa**: tabla `pantries` con el stock de casa | ⚠️ Pendiente (no depende de la 017; se puede aplicar sola) |
| `019_meal_stock.sql` | **Descontar lo cocinado**: medida de compra en `products`, marcas de descontado en `days`, ajustes de aviso y `meal_reminders` | ⚠️ Pendiente (requiere la `018`) |

## Orden de ejecución

```sql
-- 1) Arregla la campana de notificaciones
--    (003_push_subscriptions_alias.sql)
-- 2) Prepara las comidas para la lista de la compra automática
--    (004_meal_ingredients.sql)
-- 3) Carga el recetario
--    (005_seed_meals.sql)
-- 4) Catálogos configurables (units, supermarkets, task_types, meal_categories...)
--    (006 a 012)
-- 5) Catálogo de productos: rellena solo con los ingredientes que ya usabas
--    (013_products.sql — requiere 004)
-- 6) Recetario por propietario, compartible y fusionable
--    (014_recipe_books.sql — requiere 004)
```

## 016: el chat de amigos

Sin `016_chat.sql` la pestaña de amigos funciona (solicitudes, lista,
preferencia de avisos) pero **no se puede escribir**: la conversación sale
vacía y al enviar aparece un aviso pidiendo la migración. Es una tabla nueva y
nada más; no toca nada de lo que ya existe.

## 013 y 014: qué pasa si no se aplican

- Sin `013_products.sql`, el desplegable de producto sale vacío y avisa: los
  ingredientes se eligen de un catálogo y ese catálogo vive en la tabla nueva.
- Sin `014_recipe_books.sql`, **no se pueden crear ni editar comidas**: cada
  comida tiene que colgar de un recetario (`meals.book_id`) y sin la columna no
  hay dónde colgarla. El resto de la app sigue funcionando.

`014` conserva lo que hay: como hoy el recetario es común a todos, mete todas
las comidas existentes en **un único recetario compartido por todos los usuarios
actuales**. Quien se dé de alta a partir de entonces empieza con el suyo vacío.
Si prefieres quedártelo solo tú, hay una línea comentada dentro del archivo.

## ¿Por qué fallaba la campana?

La tabla `push_subscriptions` se creó en producción **sin la columna `alias`**,
pero el código la enviaba en cada `insert`. PostgREST respondía
`PGRST204: Could not find the 'alias' column` y el usuario solo veía
*"Ocurrió un error inesperado al guardar la suscripción"*.

El código ya lleva un apaño: si la columna no existe, reintenta guardando sin
alias, así que la suscripción funciona igual. Ejecutando `003` se recupera el
nombre del dispositivo en `/profile`.

## 017: el recetario compartido de dos usuarios

`005_seed_meals.sql` siembra el recetario **común** de antes de la `014`, que ya
no existe: la `014` borra las comidas sin dueño. A partir de ahí las comidas
tienen que colgar del recetario de alguien, y eso es lo que hace `017`.

Deja a Ruben y a Gaby compartiendo **un solo** recetario con las 125 comidas
del catálogo (descripción, categoría, minutos e ingredientes) y siembra los 132
productos del catálogo común. Si cada uno ya tenía recetario, los fusiona igual
que el botón de compartir de la app: las recetas del segundo pasan al primero y
las repetidas por nombre se descartan. También los deja como amigos aceptados.

Es idempotente y **no pisa nada de lo que ya haya**: una comida que ya esté en
el recetario con ese nombre se queda tal cual (con sus notas, su supermercado y
el tiempo que le hayas puesto) y solo se añaden las que faltan. Igual con los
productos. Por eso se puede lanzar las veces que haga falta.

Para otra pareja de usuarios, se regenera con sus nombres:

```bash
python -m Calendario.database.seeds.generate_book_sql Ruben Gaby
```

Y si lo que se quiere es justo lo contrario —que el catálogo mande y sobrescriba
las recetas que ya existan con ese nombre— hay que pedirlo a propósito:

```bash
python -m Calendario.database.seeds.generate_book_sql Ruben Gaby --pisar
```

Los nombres se buscan en `user.username` sin distinguir mayúsculas. Si alguno no
existe, el script aborta entero sin tocar nada y dice cuál falta.

## 018: la despensa

Crea la tabla `pantries` (`user_ids` + un JSON de productos, la misma forma que
`shopping_lists`) y siembra una despensa vacía para cada usuario.

Es una **lista independiente** de la de la compra: se comparte desde su propia
pantalla, por nombre de usuario y fusionando los dos stocks. Compartir la compra
no comparte la despensa ni al revés.

No depende de la `017` ni de ninguna otra pendiente: se puede ejecutar sola.

**Sin ella, la app funciona igual**, solo que:

- `/despensa` sale vacía y avisa de que falta esta migración;
- marcar productos como comprados **no** suma stock (y no se ralentiza: al
  primer fallo se deja de preguntar por la tabla durante unos minutos);
- la lista de la compra no puede enseñar el "ya tienes X en casa".

Aplicada, el circuito queda cerrado en los dos sentidos: la compra llena la
despensa al marcar lo comprado, y la despensa devuelve a la compra lo que baja
del mínimo. Desmarcar un producto **resta** lo que había sumado, así que un tic
sin querer no deja basura en el stock.

## 019: descontar de la despensa lo que se cocina

Cierra el circuito por el último lado. La compra llena la despensa (018) y esto
la vacía a medida que se cocina, **siempre con autorización**: a la hora de
comer llega un aviso, se abre la ventana con las cuentas hechas y se le da a
restar.

Lo que añade:

- `products.pack_qty` / `pack_unit`: **la medida con la que se compra** cada
  producto (un brik son 1 l). Es lo que se propone al guardar algo en la
  despensa o en la compra —la `qty` de siempre pasa a ser solo la cantidad de
  receta— y lo que permite restar "300 ml" de una despensa que cuenta briks.
- `days.meal_consumed` / `dinner_consumed` (+ `_by`, `_at`, `_items`): si esa
  comida ya se descontó, quién lo hizo, cuándo y **qué cantidades exactas**. De
  ahí salen el tick del calendario, la "i" que lo explica y el "deshacer".
- Ajustes por usuario: `notify_meal_stock`, `meal_notify_time` (15:00) y
  `dinner_notify_time` (23:00), que se editan en `/profile`.
- `meal_reminders`: registro de avisos enviados, con índice único por usuario,
  día y comida. Es lo que impide que el recordatorio salga repetido aunque el
  servidor corra con varios procesos o se reinicie a esa hora.

**Sin ella** la app funciona igual: no se puede descontar (la ventana avisa), no
hay medida de compra en el catálogo y no salen los recordatorios.

## Regenerar el catálogo de comidas

`005_seed_meals.sql` está **generado**. La fuente es
`Calendario/database/seeds/meals_catalog.py`. Si tocas una receta:

```bash
python -m Calendario.database.seeds.generate_sql
```

Como alternativa al SQL, una vez aplicada la `004` se puede sembrar por API:

```bash
python -m Calendario.database.seeds.seed_meals --dry   # ver qué haría
python -m Calendario.database.seeds.seed_meals         # sembrar
```

## Mientras no se apliquen

La app funciona igual, pero degradada:

- Todas las comidas salen como categoría "Otros" y sin ingredientes.
- El menú semanal se puede rellenar, pero al generar la lista avisa de que no
  hay ingredientes que sumar.
- Los dispositivos de notificaciones aparecen como "Dispositivo sin nombre".
- Las unidades de medida salen de la lista de reserva de `SupabaseAPI.DEFAULT_UNITS`
  y el gestor avisa de que no puede guardar cambios.
