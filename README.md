# 👋 CalendPy

Aplicación web para **planificar las comidas de casa y salir con la compra hecha**,
construida con [Reflex](https://reflex.dev) (Python full-stack) y Supabase.

En producción: <https://calendpy.noxuscmmd.uk>

## Qué hace

- **Calendario por mes** — comida y cena para cada día, comentarios y agenda
  diaria (tareas, eventos y notas). Al entrar se selecciona solo el calendario
  del **mes en curso**, sea tuyo o compartido contigo.
- **Menú semanal** (`/menu_semanal`) — vista de lunes a domingo para rellenar la
  semana de una sentada, con "Sorpréndeme" (rellena huecos al azar sin repetir)
  y "Copiar semana anterior".
- **Lista de la compra automática** — suma los ingredientes de todos los platos
  de la semana, escala por comensales y agrupa por sección del súper. Se puede
  editar, marcar como comprado y vaciar lo ya comprado. Los productos generados
  se distinguen de los añadidos a mano y solo se recalculan esos.
- **Despensa** (`/despensa`) — el stock de casa, y **se llena sola**: lo que
  marcas como comprado en la lista entra aquí (desmarcarlo lo saca). Agrupada
  por dónde se guarda (nevera, congelador, despensa), con caducidades, aviso de
  mínimos y un botón que devuelve a la compra todo lo que se está acabando. En
  la lista, cada producto enseña lo que ya tienes en casa antes de comprarlo.
- **Descontar lo cocinado** — a la hora de comer (15:00) y de cenar (23:00, o
  las que pongas en tu perfil) llega un aviso que abre la ventana de descuento:
  enseña qué pide la receta, qué hay en casa y qué se va a restar, distingue lo
  que **no** está en la despensa (para guardarlo o comprarlo) y solo resta
  cuando lo autorizas. Cada día queda con su tick de "ya descontado", con quién
  lo hizo y las cantidades exactas. También se puede hacer en cualquier momento
  desde el calendario, comida y cena por separado.
- **Recetario** (`/meal_list`) — más de 100 platos fáciles con ingredientes,
  categoría y tiempo. Cuadrícula con búsqueda por plato o ingrediente y filtros
  por categoría.
- **Compartido** — calendarios, lista de la compra y despensa con otros
  usuarios. La despensa es una lista **independiente**: se comparte por su
  cuenta (fusionando los dos stocks), no va atada a la de la compra.
- **Notificaciones push** por dispositivo.

## Puesta en marcha

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\Activate
pip install -r requirements.txt
reflex run
```

Hace falta un `.env` con las claves de Supabase (`SUPABASE_URL`, `SUPABASE_KEY`),
el SMTP para la recuperación de contraseña y las claves VAPID de las
notificaciones push.

## Base de datos

El esquema **no se migra solo**: la API REST de Supabase no ejecuta DDL. Los
`.sql` de `Calendario/database/migrations/` se pegan en el SQL Editor de
Supabase. Ver [`migrations/README.md`](Calendario/database/migrations/README.md)
para el orden y el estado de cada uno.

⚠️ El backend usa la **service_role key**, que se salta Row Level Security: todo
el control de acceso vive en `Calendario/database/database.py`. Cualquier
escritura nueva debe comprobar allí que el usuario tiene acceso a la fila.

## Estructura

```
Calendario/
├── components/     piezas de UI (ui.py es el kit común: paneles, cabeceras, chips...)
├── database/
│   ├── database.py capa de acceso a Supabase + comprobaciones de acceso
│   ├── migrations/ SQL a ejecutar a mano
│   └── seeds/      catálogo de comidas (fuente del SQL de siembra)
├── model/          modelos de datos compartidos entre estado y UI
├── pages/          una por ruta
├── state/          estados de Reflex
├── theme.py        tokens de diseño (colores, radios, categorías)
└── utils/          api.py (puente estado ↔ base de datos), correo
```
