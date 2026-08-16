#Calendario/model/model.py

from typing import Optional
import reflex as rx
from datetime import datetime

#Modelos de objetos que se crearán en la app a partir de los registros en base de datos

class User(rx.Base):
    #Modelo para el usuario
    id: int
    username: str
    pasw: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[str] = None
    created_at: Optional[datetime] = None


class Calendar(rx.Base):
    #Modelo para el calendario
    id: int
    name: str
    owner_id: int
    shared_with: Optional[list[int]] = []
    created_at: datetime
    start_date : datetime
    end_date : datetime


class Ingredient(rx.Base):
    """Ingrediente de una comida, tal y como se guarda en meals.ingredients (JSONB).

    Las cantidades están pensadas para 2 comensales; el generador de la lista
    de la compra las escala según las personas que se indiquen.

    Lleva los **mismos campos** que un producto de la lista de la compra
    (sección, supermercado, básico, nota): así, al generar la compra desde el
    menú semanal, no se pierde por el camino nada de lo que escribiste en la
    receta.
    """
    name: str
    qty: float = 1
    unit: str = "ud"          # g | ml | ud | lata | diente | cda | pizca | sobre | manojo
    cat: str = "otros"        # sección del súper (ver SHOP_CATEGORIES)
    shop: str = ""            # supermercado donde se compra (opcional)
    staple: bool = False      # despensa básica: no se añade a la compra por defecto
    note: str = ""            # apunte libre: marca, tamaño, "el del pasillo 3"...


class Product(rx.Base):
    """Producto del catálogo: el ingrediente "preestablecido".

    Es la plantilla de un ingrediente. Al elegirlo en una receta o en la lista
    de la compra, sus valores por defecto (unidad, sección, supermercado,
    básico, nota) se copian al ingrediente, donde se pueden cambiar sin tocar
    el catálogo.
    """
    id: int = 0
    name: str
    qty: float = 1            # lo que pide una receta (cantidad de cocina)
    unit: str = "ud"
    #La medida EXACTA con la que se compra en el súper: un brik de leche es
    #1 l, un paquete de arroz 1 kg. Es lo que se propone al guardar algo en la
    #despensa, y lo que permite restar "300 ml" de una despensa que cuenta
    #briks. `pack_qty = 0` significa "no se ha dicho": se usa `qty`.
    pack_qty: float = 0
    pack_unit: str = ""
    cat: str = "otros"
    shop: str = ""
    staple: bool = False
    note: str = ""
    #Resueltos al cargar, para pintarlos sin hacer cuentas en el `rx.foreach`
    cat_label: str = "Otros"
    cat_color: str = "#94a3b8"
    cat_icon: str = "shopping-basket"


class UnitUsage(rx.Base):
    """Una unidad de medida con la cuenta de dónde está escrita.

    La unidad se guarda como texto en el catálogo, en los ingredientes y en la
    lista de la compra, no como referencia a la tabla `units`. Por eso hay dos
    clases de unidad y hacen falta las dos en el gestor:

    - las de la tabla (`orphan=False`): las que salen en los desplegables;
    - las **huérfanas** (`orphan=True`): las que se borraron del desplegable
      pero siguen escritas en las recetas. Se ven, pero no se pueden volver a
      elegir, así que hay que convertirlas o recuperarlas.
    """
    name: str
    count: int = 0
    orphan: bool = False


class CalendarOption(rx.Base):
    """Calendario tal y como se muestra en el selector de la barra superior.

    Lleva ya calculado lo que el selector necesita pintar (mes al que se
    refiere, si es tuyo o compartido, cuánto lo tienes planificado), para que
    el componente no tenga que hacer cuentas dentro de un `rx.foreach`.
    """
    id: int
    name: str
    month_label: str = ""      # "Julio 2026"
    month_abbr: str = ""       # "JUL"
    year_abbr: str = ""        # "26"
    is_owner: bool = True
    is_current_month: bool = False   # el mes en curso cae dentro del calendario
    is_past: bool = False
    days_total: int = 0
    days_planned: int = 0
    percent: int = 0


class Meal(rx.Base):
    #Modelo para las comidas
    id: int
    name: str
    description: Optional[str] = None
    #Campos añadidos por la migración 004: si aún no está aplicada, quedan
    #con estos valores por defecto y la app sigue funcionando igual
    ingredients: list[Ingredient] = []
    category: str = "otros"
    prep_minutes: int = 20


class Day(rx.Base):
    #Modelo para cada dia en el calendario
    id: int
    calendar_id: int
    date: datetime
    meal: Optional[str] = None
    dinner: Optional[str] = None
    comments: bool = False
    #Resumen de la agenda del día (tareas/eventos/notas), para mostrar indicadores
    agenda_total: int = 0
    pending_tasks: int = 0
    #Si ya se descontaron de la despensa los ingredientes de la comida/cena, y
    #quién lo hizo. En una casa compartida, un tick sin nombre no dice nada.
    meal_consumed: bool = False
    dinner_consumed: bool = False
    meal_consumed_by: str = ""
    dinner_consumed_by: str = ""
    #"Ruben · 12/08 15:34", ya montado para pintarlo
    meal_consumed_label: str = ""
    dinner_consumed_label: str = ""
    #Lo que se restó exactamente: ["Arroz — 300 g", "Cebolla — 1 ud"]
    meal_consumed_items: list[str] = []
    dinner_consumed_items: list[str] = []


class DayItem(rx.Base):
    """Modelo para un elemento de la agenda diaria (tarea, evento o nota)."""
    id: int
    day_id: int
    calendar_id: int
    owner_id: int
    item_type: str  # "task" | "event" | "note"
    title: str
    description: Optional[str] = ""
    time: Optional[str] = None      # hora de inicio, "HH:MM"
    end_time: Optional[str] = None  # hora de fin, "HH:MM" (migración 008)
    completed: bool = False
    created_at: Optional[datetime] = None
    #Etiqueta ya montada para pintar: "09:00 – 09:30", "09:00" o ""
    time_label: str = ""
    #Icono, color y etiqueta del tipo, resueltos desde el catálogo task_types
    type_icon: str = "list-checks"
    type_color: str = "#34d399"
    type_label: str = ""
    completable: bool = False


class CalendarMember(rx.Base):
    """Alguien con acceso a un calendario, con su rol ya resuelto."""
    user_id: int
    username: str
    role: str = "member"          # owner | admin | member
    role_label: str = "Invitado"
    is_owner: bool = False
    is_admin: bool = False
    is_me: bool = False


class CatalogEntry(rx.Base):
    """Elemento de un catálogo configurable: categorías de plato y tipos de
    agenda comparten forma (clave, etiqueta, color, icono)."""
    key: str
    label: str
    color: str = "#94a3b8"
    icon: str = "utensils"
    completable: bool = False   # solo lo usan los tipos de agenda


class MealCard(rx.Base):
    """Plato con su categoría ya resuelta (color, icono, etiqueta).

    Las categorías son configurables, así que no se pueden resolver con un
    `rx.match` estático en el componente: llegan resueltas desde el estado.
    """
    id: int
    name: str
    description: str = ""
    prep_minutes: int = 20
    ingredient_count: int = 0
    cat_key: str = "otros"
    cat_label: str = "Otros"
    cat_color: str = "#94a3b8"
    cat_icon: str = "utensils"


class MealGroup(rx.Base):
    """Comidas agrupadas por categoría, para los desplegables.

    Con 100+ platos, una lista plana es inmanejable: agrupada por categoría
    (arroz, pasta, carne...) se encuentra lo que buscas de un vistazo.
    """
    key: str
    label: str
    meals: list["Meal"] = []


class WeekDay(rx.Base):
    """Un día dentro del planificador semanal.

    Es una vista "aplanada" del `Day` real: trae ya calculadas las etiquetas y
    los colores que la cuadrícula necesita, para no hacer cuentas de fechas
    dentro del `rx.foreach`.
    """
    day_id: int
    date_iso: str
    day_name: str = ""        # "Lunes"
    date_label: str = ""      # "4 ago"
    meal: str = ""
    dinner: str = ""
    meal_category: str = "otros"
    dinner_category: str = "otros"
    is_today: bool = False
    is_past: bool = False
    is_weekend: bool = False
    calendar_name: str = ""


class GeneratedItem(rx.Base):
    """Producto calculado a partir de los ingredientes del menú de la semana."""
    name: str
    qty: float = 0
    unit: str = "ud"
    cat: str = "otros"
    shop: str = ""            # supermercado heredado del ingrediente
    note: str = ""            # nota heredada del ingrediente
    source: str = ""          # comidas que lo piden
    qty_label: str = ""       # "400 g", "2 ud"...
    staple: bool = False
    key: str = ""             # "nombre|unidad", para marcar/desmarcar
    selected: bool = True     # si se añade o no a la lista de la compra


class Comment(rx.Base):
    #Modelo para los comentarios
    id: int
    day_id: int  
    content: str 
    owner_id: int 
    created_at: datetime
    user: User


class ShoppingList(rx.Base):
    """Modelo para la lista de la compra"""
    id: int
    user_ids: list[int] = []
    items: dict = {}   # El JSON con los productos
    created_at: Optional[datetime] = None

class Supermarket(rx.Base):
    """Supermercado con su color, para distinguirlos de un vistazo.

    En la lista solo se pinta `initial` sobre `color`; el nombre completo sale
    al tocar el círculo.
    """
    name: str
    color: str = "#38bdf8"
    initial: str = "?"


class ShoppingRow(rx.Base):
    """Producto de la lista de la compra, listo para pintar.

    El JSON de `shopping_lists.items` es un diccionario suelto; esto lo
    normaliza (con valores por defecto para las listas antiguas, que no
    tenían unidad ni categoría) y añade la etiqueta ya formateada.
    """
    name: str
    quantity: float = 1
    qty_label: str = ""
    unit: str = "ud"
    supermarket: str = ""
    bought: bool = False
    auto: bool = False
    source: str = ""
    cat: str = "otros"
    staple: bool = False      # básico de despensa, igual que en el recetario
    note: str = ""            # apunte libre
    #Color e inicial del supermercado, resueltos al construir la fila
    shop_color: str = ""
    shop_initial: str = ""
    #Lo que ya tienes de eso en casa ("2 briks"), para no comprarlo dos veces.
    #Vacío si no hay nada en la despensa o si aún no está aplicada la 018.
    at_home: str = ""


class ShoppingGroup(rx.Base):
    """Productos agrupados por sección del súper."""
    cat: str
    label: str
    color: str
    icon: str
    items: list[ShoppingRow] = []
    total: int = 0
    bought: int = 0


class PantryRow(rx.Base):
    """Producto de la despensa, listo para pintar.

    Igual que `ShoppingRow`, pero de lo que **hay** en casa en vez de lo que
    falta: dónde está guardado, cuánto queda, si hay que reponerlo y si está a
    punto de caducar. Todo lo que hace falta calcular (etiquetas, colores,
    avisos) llega ya resuelto, para no hacer cuentas dentro del `rx.foreach`.
    """
    name: str
    quantity: float = 0
    qty_label: str = ""
    unit: str = "ud"
    place: str = "despensa"     # nevera | congelador | despensa | otros
    cat: str = "otros"          # sección del súper, para volver a la compra
    shop: str = ""
    note: str = ""
    min_qty: float = 0
    min_label: str = ""         # "Mínimo: 2 ud"
    low: bool = False           # por debajo del mínimo (o a cero)
    empty: bool = False         # se ha acabado del todo
    expires: str = ""           # "2026-08-20"
    expiry_label: str = ""      # "Caduca en 2 días"
    expiry_color: str = ""
    expired: bool = False
    expiring: bool = False      # caduca hoy o en los próximos días
    updated_label: str = ""     # "hace 3 días"


class ConsumeRow(rx.Base):
    """Un ingrediente de la comida que se va a descontar de la despensa.

    Trae ya resuelto lo que hace falta para decidir de un vistazo: cuánto pide
    la receta, cuánto hay en casa, cuánto se va a restar (en la unidad de la
    despensa) y en qué estado queda. Los estados son los tres que importan:

    - `ok`: hay de sobra;
    - `justo`: hay, pero se queda a cero o por debajo del mínimo;
    - `falta`: hay menos de lo que pide la receta;
    - `nuevo`: **no está en la despensa** — ni se puede restar ni se sabía que
      lo tenías, así que se ofrece guardarlo o mandarlo a la compra.
    """
    name: str
    need_qty: float = 0        # lo que pide la receta, ya escalado
    need_unit: str = "ud"
    need_label: str = ""       # "300 ml"
    have_qty: float = 0        # lo que hay en casa
    have_unit: str = "ud"
    have_label: str = ""       # "2 briks"
    take_qty: float = 0        # lo que se va a restar, en la unidad de casa
    take_label: str = ""
    after_label: str = ""      # cómo se queda la despensa: "1,7 briks"
    status: str = "ok"         # ok | justo | falta | nuevo
    status_label: str = ""
    status_color: str = ""
    in_pantry: bool = True
    selected: bool = True      # se resta o no
    staple: bool = False
    cat: str = "otros"
    shop: str = ""
    note: str = ""
    key: str = ""              # "nombre|unidad", para marcar/desmarcar


class PantryGroup(rx.Base):
    """Lo que hay en casa, agrupado por dónde está guardado."""
    place: str
    label: str
    color: str
    icon: str
    items: list[PantryRow] = []
    total: int = 0
    low: int = 0


class ShoppingItem(rx.Base):
    """Modelo para un producto dentro de la lista (opcional, para tipado)"""
    name: str
    quantity: float
    supermarket: str = ""
    bought: bool = False
    unit: str = "ud"       # unidad de medida ("g", "ml", "ud"...)
    cat: str = "otros"     # sección del súper, para agrupar la lista
    staple: bool = False   # básico de despensa (mismo campo que en el recetario)
    note: str = ""         # apunte libre
    auto: bool = False     # generado desde el menú semanal (no añadido a mano)
    source: str = ""       # comidas que lo pidieron, p.ej. "Paella, Arroz con pollo"