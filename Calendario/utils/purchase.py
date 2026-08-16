# Calendario/utils/purchase.py
"""
Conversión de unidades de cocina a unidades de compra.

Una receta se escribe como se cocina ("1 pizca de sal", "2 cucharadas de
aceite", "3 dientes de ajo"), pero en el súper eso no se compra así: compras un
bote de sal, una botella de aceite y una cabeza de ajos.

Aquí se traduce lo uno a lo otro, justo antes de volcar los ingredientes en la
lista de la compra. Es una función pura para poder comprobarla sin levantar la
app ni tocar la base de datos.
"""

import math
from typing import Optional

#Cómo se compra cada producto: nombre canónico -> (unidad de compra, cuánto
#trae un envase medido en la unidad de la receta).
#`None` en el contenido = compras un envase y te sobra (especias, aceite...).
PURCHASE_RULES: dict[str, tuple[str, Optional[float]]] = {
    # Especias y condimentos: da igual la cantidad, compras el bote
    "Sal": ("bote", None),
    "Pimienta": ("bote", None),
    "Pimentón": ("bote", None),
    "Orégano": ("bote", None),
    "Comino": ("bote", None),
    "Curry en polvo": ("bote", None),
    "Laurel": ("bote", None),
    "Romero": ("bote", None),
    "Eneldo": ("bote", None),
    "Nuez moscada": ("bote", None),
    "Especias variadas": ("bote", None),
    "Sésamo": ("bote", None),
    "Azafrán": ("sobre", None),
    "Guindilla": ("bolsa", None),
    # Líquidos de despensa
    "Aceite de oliva": ("botella", None),
    "Vinagre": ("botella", None),
    "Salsa de soja": ("botella", None),
    "Salsa teriyaki": ("botella", None),
    "Vino blanco": ("botella", 750),
    "Vino tinto": ("botella", 750),
    # Cosas que se compran por envase entero
    "Miel": ("bote", None),
    "Mayonesa": ("bote", None),
    "Salsa césar": ("bote", None),
    "Salsa brava": ("bote", None),
    "Pesto": ("bote", None),
    "Tahini": ("bote", None),
    "Aceitunas": ("bote", None),
    "Pan rallado": ("paquete", None),
    "Bechamel": ("brik", 500),
    "Leche de coco": ("brik", 400),
    "Nata líquida": ("brik", 200),
    "Caldo de pollo": ("brik", 1000),
    "Caldo de verduras": ("brik", 1000),
    "Caldo de pescado": ("brik", 1000),
    "Leche": ("brik", 1000),
    # Unidades de cocina que no son de compra
    "Ajo": ("cabeza", 10),          # ~10 dientes por cabeza
    "Perejil": ("manojo", 1),
}

#Reglas por unidad, cuando el producto no tiene una regla propia
UNIT_RULES: dict[str, tuple[str, Optional[float]]] = {
    "pizca": ("bote", None),        # si se mide en pizcas, es un condimento
    "cda": ("bote", None),          # cucharadas de algo que se compra envasado
    "diente": ("cabeza", 10),
}

#El gramo y el mililitro se han escrito de las dos formas a lo largo del
#tiempo (las unidades son configurables y "g" convivió con "gr"). Todo lo que
#mida en gramos tiene que escalar igual a kilos, se llame como se llame.
GRAM_UNITS = {"g", "gr", "grs", "gramo", "gramos"}
MILLILITRE_UNITS = {"ml", "mls", "mililitro", "mililitros"}

#Unidades que ya son de compra: se dejan como están
PASSTHROUGH_UNITS = {"ud", "lata", "sobre", "manojo", "paquete", "bote", "botella", "brik", "bolsa", "cabeza"}

#Plurales, para que la lista no diga "2 lata"
PLURALS = {
    "lata": "latas",
    "bote": "botes",
    "botella": "botellas",
    "brik": "briks",
    "bolsa": "bolsas",
    "paquete": "paquetes",
    "sobre": "sobres",
    "manojo": "manojos",
    "cabeza": "cabezas",
    "diente": "dientes",
    "docena": "docenas",
}


#Pistas para adivinar la sección del súper a partir del nombre del producto.
#No pretende ser exhaustivo: acierta en lo habitual y el usuario puede cambiarlo.
#Vive aquí (y no en el estado del formulario) porque lo usan tanto el recetario
#como el catálogo de productos.
CATEGORY_HINTS = {
    "verduras": (
        "cebolla", "ajo", "tomate", "pimiento", "calabac", "berenjen", "zanahoria",
        "brocoli", "brócoli", "champi", "espinac", "lechuga", "aguacate", "patata",
        "boniato", "calabaza", "coliflor", "pepino", "limon", "limón", "lima",
        "puerro", "judias", "judías", "perejil", "platano", "plátano", "repollo",
        "cherry", "manzana", "naranja",
    ),
    "carne": (
        "pollo", "ternera", "cerdo", "pavo", "carne", "chorizo", "bacon", "jamon",
        "jamón", "lomo", "panceta", "morcilla", "chistorra", "alitas", "muslo",
        "pechuga", "filete", "morcillo",
    ),
    "pescado": (
        "salmon", "salmón", "merluza", "bacalao", "atun fresco", "atún fresco",
        "lubina", "dorada", "mejill", "bonito", "gamba fresca", "tinta",
    ),
    "lacteos": (
        "leche", "nata", "queso", "yogur", "mantequilla", "huevo", "quesito", "parmesano",
    ),
    "panaderia": (
        "pan", "tortilla de trigo", "tortillas", "pita", "picatoste", "hamburguesa",
    ),
    "congelados": (
        "congelad", "guisantes", "gambas", "menestra", "anillas", "helado",
    ),
    "despensa": (
        "arroz", "pasta", "espagueti", "macarr", "fusilli", "penne", "tallarin",
        "fideo", "lenteja", "garbanzo", "alubia", "aceite", "sal", "pimienta",
        "especias", "harina", "azucar", "azúcar", "tomate frito", "tomate triturado",
        "caldo", "soja", "curry", "pimenton", "pimentón", "atun", "atún", "maiz",
        "maíz", "aceituna", "mayonesa", "vinagre", "miel", "nuez", "nueces",
        "almendra", "quinoa", "noodles", "bechamel", "pesto", "teriyaki", "coco",
        "pan rallado", "laurel", "oregano", "orégano", "comino", "sesamo", "sésamo",
    ),
}


def guess_category(name: str) -> str:
    """Adivina la sección del súper de un producto por su nombre."""
    lowered = (name or "").strip().lower()
    if not lowered:
        return "otros"
    #Se recorre en orden de especificidad: las pistas concretas (pescado,
    #panadería) deben ganar a "despensa"
    for cat in ("pescado", "panaderia", "congelados", "lacteos", "carne", "verduras", "despensa"):
        for hint in CATEGORY_HINTS.get(cat, ()):
            if hint in lowered:
                return cat
    return "otros"


def to_purchase(name: str, qty: float, unit: str) -> tuple[float, str]:
    """Traduce (producto, cantidad, unidad de receta) a unidad de compra.

    Devuelve (cantidad, unidad) tal y como debe aparecer en la lista.

        to_purchase("Sal", 5, "pizca")         -> (1, "bote")
        to_purchase("Aceite de oliva", 12, "cda") -> (1, "botella")
        to_purchase("Ajo", 14, "diente")       -> (2, "cabeza")
        to_purchase("Arroz", 1200, "g")        -> (1.2, "kg")
    """
    rule = PURCHASE_RULES.get(name) or UNIT_RULES.get(unit)

    if rule:
        pack_unit, pack_size = rule
        if pack_size:
            #Se redondea hacia arriba: no puedes comprar media cabeza de ajos
            return float(math.ceil(qty / pack_size)), pack_unit
        return 1.0, pack_unit

    #Normalización de magnitudes: 1200 g se escribe 1,2 kg.
    #Se aceptan las dos formas de escribir el gramo: la app dejaba elegir "g" o
    #"gr" y las recetas viejas usaban una u otra. Comparar solo con "g" hacía
    #que una receta en "gr" se quedara en "1200 gr" en la lista de la compra.
    if unit.strip().lower() in GRAM_UNITS and qty >= 1000:
        return round(qty / 1000, 2), "kg"
    if unit.strip().lower() in MILLILITRE_UNITS and qty >= 1000:
        return round(qty / 1000, 2), "l"

    return qty, unit


#Equivalencias dentro de una misma magnitud, para poder sumar cantidades que
#están escritas en unidades distintas. El valor es cuánto vale 1 de esa unidad
#en la unidad base de su magnitud (gramos y mililitros).
_EQUIVALENCIAS: dict[str, tuple[str, float]] = {
    **{u: ("masa", 1.0) for u in GRAM_UNITS},
    "kg": ("masa", 1000.0),
    "kilo": ("masa", 1000.0),
    "kilos": ("masa", 1000.0),
    **{u: ("volumen", 1.0) for u in MILLILITRE_UNITS},
    "l": ("volumen", 1000.0),
    "litro": ("volumen", 1000.0),
    "litros": ("volumen", 1000.0),
}


def convert_qty(qty: float, origen: str, destino: str) -> Optional[float]:
    """Pasa una cantidad de una unidad a otra de la misma magnitud.

    Devuelve `None` si no se pueden mezclar (no hay forma de sumar "2 latas" y
    "300 gr"), y quien llame decide qué hacer con ese caso en vez de inventarse
    un número.

        convert_qty(500, "gr", "kg")   -> 0.5
        convert_qty(1.5, "l", "ml")    -> 1500.0
        convert_qty(2, "lata", "gr")   -> None
    """
    a = (origen or "").strip().lower()
    b = (destino or "").strip().lower()
    if a == b:
        return float(qty)
    uno, otro = _EQUIVALENCIAS.get(a), _EQUIVALENCIAS.get(b)
    if not uno or not otro or uno[0] != otro[0]:
        return None
    return round(float(qty) * uno[1] / otro[1], 3)


def format_qty(qty: float, unit: str) -> str:
    """'400 g', '2 botes', '1,5 kg'. Coma decimal, que es lo que se lee aquí."""
    rounded = round(float(qty), 2)
    if abs(rounded - round(rounded)) < 0.01:
        number = str(int(round(rounded)))
    else:
        number = f"{rounded:.2f}".rstrip("0").rstrip(".").replace(".", ",")
    if rounded > 1 and unit in PLURALS:
        unit = PLURALS[unit]
    return f"{number} {unit}"
