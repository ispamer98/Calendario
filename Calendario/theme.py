"""
Tokens de diseño de CalendPy.

Centraliza aquí los colores/superficies que antes se repetían como literales
sueltos en cada componente (rgba(255,255,255,0.05), "var(--green-9)", etc.),
para que toda la app comparta un único lenguaje visual: fondo casi negro,
tarjetas "cristal" translúcidas con blur, y los colores semánticos que ya
usaba la app (verde=comida, azul=cena/acento, naranja=comentarios,
jade=agenda, dorado=propietario).
"""

BG_APP = "#05070a"
BG_SIDEBAR = "#0a0f16"
BG_TOPBAR = "rgba(10, 15, 22, 0.85)"
BG_CARD = "rgba(255, 255, 255, 0.035)"
BG_CARD_HOVER = "rgba(255, 255, 255, 0.06)"
BG_WINDOW = "#0d1420"
#Superficie un punto más elevada, para paneles dentro de paneles
BG_RAISED = "rgba(255, 255, 255, 0.055)"
BG_SUNKEN = "rgba(0, 0, 0, 0.22)"

BORDER = "rgba(255, 255, 255, 0.08)"
BORDER_STRONG = "rgba(255, 255, 255, 0.16)"

ACCENT = "#38bdf8"    # acento general / cena
MEAL = "#22c55e"      # comida
DINNER = "#38bdf8"    # cena (mismo que ACCENT)
COMMENT = "#f97316"   # comentarios
AGENDA = "#34d399"    # agenda (tareas/eventos/notas)
OWNER = "#eab308"     # propietario de calendario
PANTRY = "#f59e0b"    # despensa (lo que hay en casa)
DANGER = "#ef4444"
SUCCESS = "#22c55e"
WARNING = "#f97316"
PURPLE = "#a78bfa"
PINK = "#f472b6"
MUTED = "#94a3b8"
TEXT = "#e2e8f0"
#Texto todavía más apagado, para metadatos y pies de tarjeta
DIM = "#64748b"

FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"

#Radios y sombras: se repetían a ojo en cada componente
RADIUS_SM = "10px"
RADIUS = "14px"
RADIUS_LG = "20px"
SHADOW_SM = "0 2px 8px rgba(0, 0, 0, 0.28)"
SHADOW = "0 10px 30px -12px rgba(0, 0, 0, 0.6)"
SHADOW_LG = "0 24px 70px -12px rgba(0, 0, 0, 0.7)"

#Degradado de marca, usado en cabeceras y botones principales
GRADIENT = f"linear-gradient(135deg, {ACCENT} 0%, {PURPLE} 100%)"
GRADIENT_MEAL = f"linear-gradient(135deg, {MEAL} 0%, {AGENDA} 100%)"


def alpha(hex_color: str, a: float) -> str:
    """rgba() a partir de un hex '#rrggbb' — para fondos translúcidos de icono/estado."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {a})"


# ---------------------------------------------------------------------------
# Categorías de plato: color + icono, para que una comida se reconozca de un
# vistazo en la cuadrícula, en el menú semanal y en el calendario.
# ---------------------------------------------------------------------------
MEAL_CATEGORY_STYLE = {
    "arroz":    {"label": "Arroz",     "color": "#f59e0b", "icon": "wheat"},
    "pasta":    {"label": "Pasta",     "color": "#fbbf24", "icon": "wheat"},
    "patata":   {"label": "Patata",    "color": "#d97706", "icon": "cookie"},
    "legumbre": {"label": "Legumbre",  "color": "#a16207", "icon": "bean"},
    "carne":    {"label": "Carne",     "color": "#ef4444", "icon": "beef"},
    "pescado":  {"label": "Pescado",   "color": "#38bdf8", "icon": "fish"},
    "huevo":    {"label": "Huevo",     "color": "#eab308", "icon": "egg"},
    "verdura":  {"label": "Verdura",   "color": "#22c55e", "icon": "carrot"},
    "ensalada": {"label": "Ensalada",  "color": "#34d399", "icon": "salad"},
    "sandwich": {"label": "Bocadillo", "color": "#f472b6", "icon": "sandwich"},
    "otros":    {"label": "Otros",     "color": "#94a3b8", "icon": "utensils"},
}

MEAL_CATEGORY_ORDER = list(MEAL_CATEGORY_STYLE.keys())


def category_color(category: str) -> str:
    return MEAL_CATEGORY_STYLE.get(category, MEAL_CATEGORY_STYLE["otros"])["color"]


def category_icon(category: str) -> str:
    return MEAL_CATEGORY_STYLE.get(category, MEAL_CATEGORY_STYLE["otros"])["icon"]


def category_label(category: str) -> str:
    return MEAL_CATEGORY_STYLE.get(category, MEAL_CATEGORY_STYLE["otros"])["label"]


# ---------------------------------------------------------------------------
# Secciones del supermercado, en el orden en el que se recorre la tienda.
# Agrupan la lista de la compra para no ir de un pasillo a otro.
# ---------------------------------------------------------------------------
SHOP_CATEGORY_STYLE = {
    "verduras":   {"label": "Frutas y verduras", "color": "#22c55e", "icon": "carrot"},
    "carne":      {"label": "Carnicería",        "color": "#ef4444", "icon": "beef"},
    "pescado":    {"label": "Pescadería",        "color": "#38bdf8", "icon": "fish"},
    "lacteos":    {"label": "Lácteos y huevos",  "color": "#fbbf24", "icon": "milk"},
    "panaderia":  {"label": "Panadería",         "color": "#d97706", "icon": "croissant"},
    "congelados": {"label": "Congelados",        "color": "#67e8f9", "icon": "snowflake"},
    "despensa":   {"label": "Despensa",          "color": "#a78bfa", "icon": "package"},
    "otros":      {"label": "Otros",             "color": "#94a3b8", "icon": "shopping-basket"},
}

SHOP_CATEGORY_ORDER = list(SHOP_CATEGORY_STYLE.keys())


def shop_color(category: str) -> str:
    return SHOP_CATEGORY_STYLE.get(category, SHOP_CATEGORY_STYLE["otros"])["color"]


def shop_icon(category: str) -> str:
    return SHOP_CATEGORY_STYLE.get(category, SHOP_CATEGORY_STYLE["otros"])["icon"]


def shop_label(category: str) -> str:
    return SHOP_CATEGORY_STYLE.get(category, SHOP_CATEGORY_STYLE["otros"])["label"]


# ---------------------------------------------------------------------------
# Sitios donde se guarda la comida en casa. Agrupan la despensa igual que las
# secciones del súper agrupan la lista de la compra: ahí lo que importa es el
# pasillo, y aquí, el mueble que hay que abrir para verlo.
# ---------------------------------------------------------------------------
PANTRY_PLACE_STYLE = {
    "nevera":     {"label": "Nevera",     "color": "#38bdf8", "icon": "refrigerator"},
    "congelador": {"label": "Congelador", "color": "#67e8f9", "icon": "snowflake"},
    "despensa":   {"label": "Despensa",   "color": "#a78bfa", "icon": "package"},
    "otros":      {"label": "Otros",      "color": "#94a3b8", "icon": "boxes"},
}

PANTRY_PLACE_ORDER = list(PANTRY_PLACE_STYLE.keys())


def place_color(place: str) -> str:
    return PANTRY_PLACE_STYLE.get(place, PANTRY_PLACE_STYLE["otros"])["color"]


def place_icon(place: str) -> str:
    return PANTRY_PLACE_STYLE.get(place, PANTRY_PLACE_STYLE["otros"])["icon"]


def place_label(place: str) -> str:
    return PANTRY_PLACE_STYLE.get(place, PANTRY_PLACE_STYLE["otros"])["label"]


MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DIAS_SEMANA_CORTOS = ["L", "M", "X", "J", "V", "S", "D"]
