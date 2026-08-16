"""
Catálogo de comidas de CalendPy.

Fuente única de verdad para las comidas "de serie" de la app: nombre,
descripción, categoría, tiempo aproximado e **ingredientes estructurados**.
De aquí sale tanto el SQL de siembra (`005_seed_meals.sql`) como el script
`seed_meals.py`, así que si se toca una receta hay que regenerar el SQL con
`python -m Calendario.database.seeds.generate_sql`.

Formato de cada ingrediente:

    {"name": "Arroz", "qty": 160, "unit": "g", "cat": "despensa", "staple": False}

- `name`  nombre canónico del producto. **Importante**: dos recetas que usen
          el mismo producto deben escribirlo igual, porque la lista de la
          compra agrega por (nombre, unidad).
- `qty`   cantidad para 2 personas (el generador la multiplica por comensales).
- `unit`  g | ml | ud | lata | diente | cda | pizca | sobre | manojo
- `cat`   sección del súper, para agrupar la lista de la compra.
- `staple` despensa básica (aceite, sal, especias...). Por defecto el
          generador NO los añade a la lista, salvo que se marque la opción.
"""

# Secciones del supermercado (orden en el que se recorre la tienda)
SHOP_CATEGORIES = [
    "verduras",
    "carne",
    "pescado",
    "lacteos",
    "despensa",
    "congelados",
    "panaderia",
    "otros",
]

# Categorías de plato, para filtrar en la pestaña de comidas
MEAL_CATEGORIES = [
    "arroz",
    "pasta",
    "patata",
    "legumbre",
    "carne",
    "pescado",
    "huevo",
    "verdura",
    "ensalada",
    "sandwich",
    "otros",
]


def ing(name: str, qty: float, unit: str, cat: str, staple: bool = False) -> dict:
    """Atajo para no repetir las claves del diccionario en 100 recetas."""
    return {"name": name, "qty": qty, "unit": unit, "cat": cat, "staple": staple}


# Despensa básica que casi ninguna receta merece la pena listar
ACEITE = ing("Aceite de oliva", 2, "cda", "despensa", True)
SAL = ing("Sal", 1, "pizca", "despensa", True)
PIMIENTA = ing("Pimienta", 1, "pizca", "despensa", True)
BASE = [ACEITE, SAL, PIMIENTA]


def meal(name, description, category, prep_minutes, ingredients, base=True) -> dict:
    return {
        "name": name,
        "description": description,
        "category": category,
        "prep_minutes": prep_minutes,
        "ingredients": (ingredients + BASE) if base else ingredients,
    }


# ---------------------------------------------------------------------------
# ARROCES
# ---------------------------------------------------------------------------
ARROCES = [
    meal("Arroz con pollo", "Sofríes cebolla y pollo, echas el arroz y el doble de caldo, y a esperar.", "arroz", 30, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Pechuga de pollo", 300, "g", "carne"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Pimiento rojo", 0.5, "ud", "verduras"),
        ing("Caldo de pollo", 400, "ml", "despensa"),
    ]),
    meal("Arroz a la cubana", "Arroz blanco, tomate frito y huevo frito encima. Imbatible.", "arroz", 20, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Tomate frito", 200, "g", "despensa"),
        ing("Huevos", 2, "ud", "lacteos"),
        ing("Plátano", 1, "ud", "verduras"),
    ]),
    meal("Arroz con verduras", "Salteas verdura congelada, añades arroz y caldo. Cero esfuerzo.", "arroz", 25, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Menestra congelada", 300, "g", "congelados"),
        ing("Cebolla", 0.5, "ud", "verduras"),
        ing("Caldo de verduras", 400, "ml", "despensa"),
    ]),
    meal("Arroz con huevo", "Arroz blanco con dos huevos fritos y un chorro de soja.", "arroz", 15, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Huevos", 4, "ud", "lacteos"),
        ing("Salsa de soja", 2, "cda", "despensa"),
    ]),
    meal("Arroz al curry", "Arroz con leche de coco y curry: se hace solo y sabe a restaurante.", "arroz", 25, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Leche de coco", 200, "ml", "despensa"),
        ing("Curry en polvo", 1, "cda", "despensa", True),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Pechuga de pollo", 250, "g", "carne"),
    ]),
    meal("Arroz tres delicias", "Arroz del día anterior salteado con guisantes, jamón y huevo.", "arroz", 20, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Guisantes congelados", 100, "g", "congelados"),
        ing("Jamón cocido", 100, "g", "carne"),
        ing("Huevos", 2, "ud", "lacteos"),
        ing("Zanahoria", 1, "ud", "verduras"),
    ]),
    meal("Arroz con atún", "Arroz blanco, tomate y dos latas de atún. Diez minutos.", "arroz", 20, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Tomate frito", 150, "g", "despensa"),
        ing("Cebolla", 0.5, "ud", "verduras"),
    ]),
    meal("Arroz caldoso", "Más caldo de lo normal y lo dejas melosito. Reconforta.", "arroz", 35, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Muslos de pollo", 400, "g", "carne"),
        ing("Caldo de pollo", 700, "ml", "despensa"),
        ing("Pimiento verde", 1, "ud", "verduras"),
        ing("Tomate triturado", 100, "g", "despensa"),
    ]),
    meal("Arroz con champiñones", "Champiñones laminados salteados con ajo y arroz.", "arroz", 25, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Champiñones", 250, "g", "verduras"),
        ing("Ajo", 2, "diente", "verduras"),
        ing("Caldo de verduras", 400, "ml", "despensa"),
        ing("Perejil", 1, "manojo", "verduras"),
    ]),
    meal("Arroz con chorizo", "Chorizo, arroz y caldo. Contundente y baratísimo.", "arroz", 30, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Chorizo", 150, "g", "carne"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Pimentón", 1, "pizca", "despensa", True),
        ing("Caldo de pollo", 400, "ml", "despensa"),
    ]),
    meal("Arroz con gambas", "Gambas congeladas, ajo y arroz. Sabe a domingo.", "arroz", 30, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Gambas peladas", 250, "g", "congelados"),
        ing("Ajo", 3, "diente", "verduras"),
        ing("Caldo de pescado", 400, "ml", "despensa"),
        ing("Pimiento rojo", 0.5, "ud", "verduras"),
    ]),
    meal("Arroz negro", "Con sobre de tinta de calamar y anillas congeladas.", "arroz", 35, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Anillas de calamar", 250, "g", "congelados"),
        ing("Tinta de calamar", 2, "sobre", "pescado"),
        ing("Ajo", 2, "diente", "verduras"),
        ing("Caldo de pescado", 400, "ml", "despensa"),
    ]),
    meal("Risotto de champiñones", "El único que pide remover, pero merece la pena.", "arroz", 35, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Champiñones", 250, "g", "verduras"),
        ing("Caldo de verduras", 600, "ml", "despensa"),
        ing("Queso rallado", 60, "g", "lacteos"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Mantequilla", 20, "g", "lacteos"),
    ]),
    meal("Arroz con brócoli", "Brócoli hervido con el propio arroz y salteado con ajo.", "arroz", 25, [
        ing("Arroz", 160, "g", "despensa"),
        ing("Brócoli", 300, "g", "verduras"),
        ing("Ajo", 2, "diente", "verduras"),
        ing("Queso rallado", 40, "g", "lacteos"),
    ]),
]

# ---------------------------------------------------------------------------
# PASTAS
# ---------------------------------------------------------------------------
PASTAS = [
    meal("Espaguetis boloñesa", "Carne picada, tomate y a hervir pasta mientras.", "pasta", 30, [
        ing("Espaguetis", 200, "g", "despensa"),
        ing("Carne picada", 300, "g", "carne"),
        ing("Tomate triturado", 400, "g", "despensa"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Zanahoria", 1, "ud", "verduras"),
        ing("Queso rallado", 50, "g", "lacteos"),
    ]),
    meal("Espaguetis carbonara", "Bacon, huevo y queso fuera del fuego. Nada de nata.", "pasta", 20, [
        ing("Espaguetis", 200, "g", "despensa"),
        ing("Bacon", 150, "g", "carne"),
        ing("Huevos", 3, "ud", "lacteos"),
        ing("Queso rallado", 80, "g", "lacteos"),
    ]),
    meal("Macarrones con tomate", "El clásico de siempre, con chorizo si te apetece.", "pasta", 20, [
        ing("Macarrones", 200, "g", "despensa"),
        ing("Tomate frito", 300, "g", "despensa"),
        ing("Queso rallado", 50, "g", "lacteos"),
        ing("Orégano", 1, "pizca", "despensa", True),
    ]),
    meal("Macarrones con atún", "Pasta, tomate y dos latas de atún. Receta de urgencia.", "pasta", 20, [
        ing("Macarrones", 200, "g", "despensa"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Tomate frito", 250, "g", "despensa"),
        ing("Cebolla", 0.5, "ud", "verduras"),
    ]),
    meal("Pasta al pesto", "Hierves pasta, abres el bote de pesto y listo.", "pasta", 15, [
        ing("Fusilli", 200, "g", "despensa"),
        ing("Pesto", 100, "g", "despensa"),
        ing("Tomates cherry", 150, "g", "verduras"),
        ing("Queso rallado", 40, "g", "lacteos"),
    ]),
    meal("Pasta con nata y bacon", "Nata, bacon y champiñones. Cremosa y rapidísima.", "pasta", 20, [
        ing("Tallarines", 200, "g", "despensa"),
        ing("Nata líquida", 200, "ml", "lacteos"),
        ing("Bacon", 150, "g", "carne"),
        ing("Champiñones", 150, "g", "verduras"),
    ]),
    meal("Lasaña de carne", "Placas precocinadas y bechamel de brik: al horno y fuera.", "pasta", 45, [
        ing("Placas de lasaña", 12, "ud", "despensa"),
        ing("Carne picada", 400, "g", "carne"),
        ing("Tomate triturado", 400, "g", "despensa"),
        ing("Bechamel", 500, "ml", "despensa"),
        ing("Queso rallado", 100, "g", "lacteos"),
        ing("Cebolla", 1, "ud", "verduras"),
    ]),
    meal("Espaguetis al ajillo", "Ajo, aceite y guindilla. Tres ingredientes, cero excusas.", "pasta", 15, [
        ing("Espaguetis", 200, "g", "despensa"),
        ing("Ajo", 4, "diente", "verduras"),
        ing("Guindilla", 1, "ud", "despensa", True),
        ing("Perejil", 1, "manojo", "verduras"),
    ]),
    meal("Fusilli con verduras", "Salteas verduras congeladas y las mezclas con la pasta.", "pasta", 25, [
        ing("Fusilli", 200, "g", "despensa"),
        ing("Calabacín", 1, "ud", "verduras"),
        ing("Pimiento rojo", 1, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Queso rallado", 40, "g", "lacteos"),
    ]),
    meal("Pasta con pollo", "Tiras de pollo, champiñones y un poco de nata.", "pasta", 25, [
        ing("Penne", 200, "g", "despensa"),
        ing("Pechuga de pollo", 300, "g", "carne"),
        ing("Champiñones", 150, "g", "verduras"),
        ing("Nata líquida", 150, "ml", "lacteos"),
    ]),
    meal("Ensalada de pasta", "Se hace de un día para otro y aguanta perfecta en la nevera.", "pasta", 20, [
        ing("Fusilli", 200, "g", "despensa"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Tomates cherry", 150, "g", "verduras"),
        ing("Maíz dulce", 1, "lata", "despensa"),
        ing("Huevos", 2, "ud", "lacteos"),
        ing("Aceitunas", 80, "g", "despensa"),
    ]),
    meal("Macarrones gratinados", "Los de ayer con bechamel y queso, cinco minutos de grill.", "pasta", 30, [
        ing("Macarrones", 200, "g", "despensa"),
        ing("Bechamel", 300, "ml", "despensa"),
        ing("Queso rallado", 100, "g", "lacteos"),
        ing("Jamón cocido", 100, "g", "carne"),
    ]),
    meal("Noodles con verduras", "Wok rápido con noodles instantáneos y salsa de soja.", "pasta", 15, [
        ing("Noodles", 200, "g", "despensa"),
        ing("Verduras para wok", 300, "g", "congelados"),
        ing("Salsa de soja", 3, "cda", "despensa"),
        ing("Ajo", 2, "diente", "verduras"),
    ]),
    meal("Espaguetis con gambas", "Gambas congeladas, ajo, guindilla y pasta.", "pasta", 20, [
        ing("Espaguetis", 200, "g", "despensa"),
        ing("Gambas peladas", 250, "g", "congelados"),
        ing("Ajo", 3, "diente", "verduras"),
        ing("Tomates cherry", 150, "g", "verduras"),
    ]),
]

# ---------------------------------------------------------------------------
# BONIATO Y PATATA
# ---------------------------------------------------------------------------
TUBERCULOS = [
    meal("Boniato al horno", "Lo pinchas, 45 min a 200º y ya está. Literalmente cero trabajo.", "patata", 50, [
        ing("Boniato", 2, "ud", "verduras"),
    ]),
    meal("Boniato con miel", "Boniato asado con miel y un puñado de nueces por encima.", "patata", 50, [
        ing("Boniato", 2, "ud", "verduras"),
        ing("Miel", 2, "cda", "despensa"),
        ing("Nueces", 50, "g", "despensa"),
    ]),
    meal("Puré de boniato", "Boniato cocido, chorrito de leche y a machacar.", "patata", 30, [
        ing("Boniato", 3, "ud", "verduras"),
        ing("Leche", 100, "ml", "lacteos"),
        ing("Mantequilla", 20, "g", "lacteos"),
        ing("Nuez moscada", 1, "pizca", "despensa", True),
    ]),
    meal("Boniato relleno", "Boniato asado abierto y relleno de atún y mayonesa.", "patata", 50, [
        ing("Boniato", 2, "ud", "verduras"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Mayonesa", 2, "cda", "despensa"),
        ing("Queso rallado", 50, "g", "lacteos"),
    ]),
    meal("Chips de boniato", "En rodajas finas al horno o a la freidora de aire.", "patata", 30, [
        ing("Boniato", 2, "ud", "verduras"),
        ing("Pimentón", 1, "pizca", "despensa", True),
    ]),
    meal("Patatas al horno", "Patatas en gajos con especias, 40 minutos y a otra cosa.", "patata", 45, [
        ing("Patata", 4, "ud", "verduras"),
        ing("Romero", 1, "pizca", "despensa", True),
        ing("Ajo", 2, "diente", "verduras"),
    ]),
    meal("Puré de patata", "De sobre o cociendo patatas: en ambos casos, cinco minutos.", "patata", 20, [
        ing("Patata", 4, "ud", "verduras"),
        ing("Leche", 150, "ml", "lacteos"),
        ing("Mantequilla", 30, "g", "lacteos"),
    ]),
    meal("Patatas guisadas", "Con chorizo o sin él, en una olla y a fuego lento.", "patata", 40, [
        ing("Patata", 5, "ud", "verduras"),
        ing("Chorizo", 100, "g", "carne"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Pimiento verde", 1, "ud", "verduras"),
        ing("Pimentón", 1, "pizca", "despensa", True),
    ]),
    meal("Tortilla de boniato", "Como la de patata pero más dulce y jugosa.", "patata", 30, [
        ing("Boniato", 2, "ud", "verduras"),
        ing("Huevos", 5, "ud", "lacteos"),
        ing("Cebolla", 1, "ud", "verduras"),
    ]),
    meal("Patatas rellenas", "Patatas asadas rellenas de carne picada y queso gratinado.", "patata", 50, [
        ing("Patata", 4, "ud", "verduras"),
        ing("Carne picada", 250, "g", "carne"),
        ing("Queso rallado", 80, "g", "lacteos"),
        ing("Tomate frito", 100, "g", "despensa"),
    ]),
    meal("Boniato con garbanzos", "Boniato asado con garbanzos de bote y especias. Muy saciante.", "patata", 40, [
        ing("Boniato", 2, "ud", "verduras"),
        ing("Garbanzos cocidos", 1, "lata", "despensa"),
        ing("Comino", 1, "pizca", "despensa", True),
        ing("Limón", 1, "ud", "verduras"),
    ]),
    meal("Patatas panadera", "Patata y cebolla en láminas al horno. Acompaña cualquier cosa.", "patata", 45, [
        ing("Patata", 4, "ud", "verduras"),
        ing("Cebolla", 2, "ud", "verduras"),
        ing("Vino blanco", 100, "ml", "otros"),
    ]),
]

# ---------------------------------------------------------------------------
# LEGUMBRES
# ---------------------------------------------------------------------------
LEGUMBRES = [
    meal("Lentejas rápidas", "Bote de lentejas cocidas, sofrito y listo en 15 minutos.", "legumbre", 20, [
        ing("Lentejas cocidas", 2, "lata", "despensa"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Zanahoria", 1, "ud", "verduras"),
        ing("Chorizo", 80, "g", "carne"),
        ing("Pimentón", 1, "pizca", "despensa", True),
    ]),
    meal("Garbanzos con espinacas", "Garbanzos de bote, espinacas congeladas y comino.", "legumbre", 20, [
        ing("Garbanzos cocidos", 2, "lata", "despensa"),
        ing("Espinacas congeladas", 300, "g", "congelados"),
        ing("Ajo", 3, "diente", "verduras"),
        ing("Comino", 1, "pizca", "despensa", True),
    ]),
    meal("Hummus casero", "Garbanzos, tahini y limón a la batidora. Con pan de pita.", "legumbre", 10, [
        ing("Garbanzos cocidos", 1, "lata", "despensa"),
        ing("Tahini", 2, "cda", "despensa"),
        ing("Limón", 1, "ud", "verduras"),
        ing("Pan de pita", 4, "ud", "panaderia"),
    ]),
    meal("Ensalada de garbanzos", "En frío, con tomate, pepino y atún. Ideal en verano.", "legumbre", 15, [
        ing("Garbanzos cocidos", 1, "lata", "despensa"),
        ing("Tomate", 2, "ud", "verduras"),
        ing("Pepino", 1, "ud", "verduras"),
        ing("Atún en lata", 1, "lata", "despensa"),
        ing("Cebolla", 0.5, "ud", "verduras"),
    ]),
    meal("Alubias con chorizo", "Alubias de bote con sofrito y chorizo. Cuchara de la buena.", "legumbre", 25, [
        ing("Alubias cocidas", 2, "lata", "despensa"),
        ing("Chorizo", 150, "g", "carne"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Pimiento verde", 1, "ud", "verduras"),
    ]),
    meal("Lentejas con verduras", "Versión ligera, solo con verdura y un buen chorro de aceite.", "legumbre", 25, [
        ing("Lentejas cocidas", 2, "lata", "despensa"),
        ing("Zanahoria", 2, "ud", "verduras"),
        ing("Calabacín", 1, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Caldo de verduras", 200, "ml", "despensa"),
    ]),
    meal("Garbanzos al curry", "Garbanzos con leche de coco y curry. Sabe a mucho más.", "legumbre", 25, [
        ing("Garbanzos cocidos", 2, "lata", "despensa"),
        ing("Leche de coco", 200, "ml", "despensa"),
        ing("Curry en polvo", 1, "cda", "despensa", True),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Tomate triturado", 200, "g", "despensa"),
    ]),
    meal("Sopa de lentejas", "Lentejas trituradas con caldo: crema calentita en 20 minutos.", "legumbre", 25, [
        ing("Lentejas cocidas", 2, "lata", "despensa"),
        ing("Caldo de verduras", 500, "ml", "despensa"),
        ing("Zanahoria", 2, "ud", "verduras"),
        ing("Patata", 1, "ud", "verduras"),
    ]),
    meal("Alubias con atún", "Alubias blancas, atún, cebolla y vinagre. Sin fuego.", "legumbre", 10, [
        ing("Alubias cocidas", 1, "lata", "despensa"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Cebolla", 0.5, "ud", "verduras"),
        ing("Vinagre", 1, "cda", "despensa", True),
        ing("Perejil", 1, "manojo", "verduras"),
    ]),
    meal("Chili con carne", "Carne picada, alubias rojas y especias. Mejor al día siguiente.", "legumbre", 35, [
        ing("Carne picada", 400, "g", "carne"),
        ing("Alubias rojas", 2, "lata", "despensa"),
        ing("Tomate triturado", 400, "g", "despensa"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Pimiento rojo", 1, "ud", "verduras"),
        ing("Comino", 1, "pizca", "despensa", True),
    ]),
]

# ---------------------------------------------------------------------------
# POLLO Y CARNES
# ---------------------------------------------------------------------------
CARNES = [
    meal("Pollo al limón", "Pechuga a la sartén con limón y ajo. Diez minutos.", "carne", 20, [
        ing("Pechuga de pollo", 400, "g", "carne"),
        ing("Limón", 1, "ud", "verduras"),
        ing("Ajo", 2, "diente", "verduras"),
    ]),
    meal("Pollo a la plancha", "Lo más básico del mundo, y con especias está buenísimo.", "carne", 15, [
        ing("Pechuga de pollo", 400, "g", "carne"),
        ing("Especias variadas", 1, "pizca", "despensa", True),
    ]),
    meal("Pechuga empanada", "Huevo, pan rallado y sartén. Como en casa de tu madre.", "carne", 25, [
        ing("Pechuga de pollo", 400, "g", "carne"),
        ing("Pan rallado", 100, "g", "despensa"),
        ing("Huevos", 2, "ud", "lacteos"),
    ]),
    meal("Pollo teriyaki", "Pollo en dados con salsa teriyaki y arroz al lado.", "carne", 25, [
        ing("Pechuga de pollo", 400, "g", "carne"),
        ing("Salsa teriyaki", 60, "ml", "despensa"),
        ing("Arroz", 160, "g", "despensa"),
        ing("Sésamo", 1, "cda", "despensa", True),
    ]),
    meal("Alitas al horno", "Alitas con especias, 35 minutos al horno y a comer con las manos.", "carne", 45, [
        ing("Alitas de pollo", 800, "g", "carne"),
        ing("Pimentón", 1, "pizca", "despensa", True),
        ing("Miel", 1, "cda", "despensa"),
        ing("Limón", 1, "ud", "verduras"),
    ]),
    meal("Muslos asados", "Muslos con patatas debajo: una bandeja, una comida.", "carne", 55, [
        ing("Muslos de pollo", 4, "ud", "carne"),
        ing("Patata", 3, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Vino blanco", 100, "ml", "otros"),
    ]),
    meal("Fajitas de pollo", "Pollo con pimientos y tortillas de trigo. Cada uno se la monta.", "carne", 25, [
        ing("Pechuga de pollo", 400, "g", "carne"),
        ing("Tortillas de trigo", 6, "ud", "panaderia"),
        ing("Pimiento rojo", 1, "ud", "verduras"),
        ing("Pimiento verde", 1, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Queso rallado", 80, "g", "lacteos"),
    ]),
    meal("Albóndigas con tomate", "Las compras hechas o las lías en 5 minutos. Con tomate frito.", "carne", 30, [
        ing("Carne picada", 400, "g", "carne"),
        ing("Tomate frito", 300, "g", "despensa"),
        ing("Huevos", 1, "ud", "lacteos"),
        ing("Pan rallado", 50, "g", "despensa"),
        ing("Ajo", 2, "diente", "verduras"),
    ]),
    meal("Hamburguesa casera", "Carne picada, pan, queso y lo que pilles en la nevera.", "carne", 20, [
        ing("Carne picada", 400, "g", "carne"),
        ing("Pan de hamburguesa", 2, "ud", "panaderia"),
        ing("Queso en lonchas", 4, "ud", "lacteos"),
        ing("Tomate", 1, "ud", "verduras"),
        ing("Lechuga", 0.5, "ud", "verduras"),
    ]),
    meal("Filete de ternera", "A la plancha, vuelta y vuelta, con patatas o ensalada.", "carne", 15, [
        ing("Filete de ternera", 400, "g", "carne"),
        ing("Ajo", 2, "diente", "verduras"),
    ]),
    meal("Carne guisada", "Ternera con patatas y zanahoria a fuego lento. Se hace sola.", "carne", 70, [
        ing("Ternera para guisar", 500, "g", "carne"),
        ing("Patata", 3, "ud", "verduras"),
        ing("Zanahoria", 2, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Vino tinto", 100, "ml", "otros"),
    ]),
    meal("Salteado de pavo", "Pavo en tiras con verduras y soja. Ligero y rápido.", "carne", 20, [
        ing("Pavo en filetes", 400, "g", "carne"),
        ing("Verduras para wok", 300, "g", "congelados"),
        ing("Salsa de soja", 2, "cda", "despensa"),
    ]),
    meal("Lomo a la plancha", "Lomo de cerdo con ajo y perejil. Cinco minutos por lado.", "carne", 15, [
        ing("Lomo de cerdo", 400, "g", "carne"),
        ing("Ajo", 2, "diente", "verduras"),
        ing("Perejil", 1, "manojo", "verduras"),
    ]),
    meal("Pollo al ajillo", "Pollo troceado con mucho ajo y un chorro de vino blanco.", "carne", 35, [
        ing("Pollo troceado", 800, "g", "carne"),
        ing("Ajo", 6, "diente", "verduras"),
        ing("Vino blanco", 150, "ml", "otros"),
        ing("Perejil", 1, "manojo", "verduras"),
    ]),
]

# ---------------------------------------------------------------------------
# PESCADOS
# ---------------------------------------------------------------------------
PESCADOS = [
    meal("Salmón al horno", "Lomos con limón y eneldo, 15 minutos a 200º.", "pescado", 25, [
        ing("Salmón", 400, "g", "pescado"),
        ing("Limón", 1, "ud", "verduras"),
        ing("Eneldo", 1, "pizca", "despensa", True),
    ]),
    meal("Merluza a la plancha", "Con un chorrito de limón y ajo picado por encima.", "pescado", 15, [
        ing("Merluza", 400, "g", "pescado"),
        ing("Ajo", 2, "diente", "verduras"),
        ing("Limón", 1, "ud", "verduras"),
    ]),
    meal("Bacalao al horno", "Bacalao con patata panadera debajo. Plato único.", "pescado", 45, [
        ing("Bacalao", 400, "g", "pescado"),
        ing("Patata", 3, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Pimentón", 1, "pizca", "despensa", True),
    ]),
    meal("Atún a la plancha", "Lomo de atún fresco vuelta y vuelta con soja.", "pescado", 15, [
        ing("Atún fresco", 400, "g", "pescado"),
        ing("Salsa de soja", 2, "cda", "despensa"),
        ing("Sésamo", 1, "cda", "despensa", True),
    ]),
    meal("Lubina al horno", "Entera con limón y patatas. Impresiona y no tiene mérito.", "pescado", 40, [
        ing("Lubina", 2, "ud", "pescado"),
        ing("Patata", 3, "ud", "verduras"),
        ing("Limón", 1, "ud", "verduras"),
        ing("Vino blanco", 100, "ml", "otros"),
    ]),
    meal("Tortilla de atún", "Huevos, atún y cebolla. Cena resuelta en 10 minutos.", "pescado", 15, [
        ing("Huevos", 4, "ud", "lacteos"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Cebolla", 0.5, "ud", "verduras"),
    ]),
    meal("Salmón teriyaki", "Salmón glaseado con teriyaki y arroz blanco.", "pescado", 25, [
        ing("Salmón", 400, "g", "pescado"),
        ing("Salsa teriyaki", 60, "ml", "despensa"),
        ing("Arroz", 160, "g", "despensa"),
    ]),
    meal("Dorada al horno", "Con ajo, limón y perejil. Sana y sin complicaciones.", "pescado", 35, [
        ing("Dorada", 2, "ud", "pescado"),
        ing("Ajo", 3, "diente", "verduras"),
        ing("Limón", 1, "ud", "verduras"),
        ing("Perejil", 1, "manojo", "verduras"),
    ]),
    meal("Bacalao con tomate", "Bacalao desalado en salsa de tomate con cebolla.", "pescado", 30, [
        ing("Bacalao", 400, "g", "pescado"),
        ing("Tomate triturado", 400, "g", "despensa"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Pimiento rojo", 0.5, "ud", "verduras"),
    ]),
    meal("Mejillones al vapor", "Una olla, un dedo de agua y limón. Cinco minutos.", "pescado", 15, [
        ing("Mejillones", 1000, "g", "pescado"),
        ing("Limón", 1, "ud", "verduras"),
        ing("Laurel", 1, "pizca", "despensa", True),
    ]),
]

# ---------------------------------------------------------------------------
# HUEVOS
# ---------------------------------------------------------------------------
HUEVOS = [
    meal("Huevos revueltos", "A fuego bajo y removiendo. Con tostada al lado.", "huevo", 10, [
        ing("Huevos", 4, "ud", "lacteos"),
        ing("Mantequilla", 15, "g", "lacteos"),
        ing("Pan de molde", 4, "ud", "panaderia"),
    ]),
    meal("Tortilla francesa", "La cena de emergencia por excelencia.", "huevo", 10, [
        ing("Huevos", 4, "ud", "lacteos"),
    ]),
    meal("Huevos al plato", "Huevos sobre tomate frito al horno con jamón.", "huevo", 20, [
        ing("Huevos", 4, "ud", "lacteos"),
        ing("Tomate frito", 200, "g", "despensa"),
        ing("Jamón cocido", 100, "g", "carne"),
        ing("Queso rallado", 50, "g", "lacteos"),
    ]),
    meal("Shakshuka", "Huevos escalfados en salsa de tomate con pimiento y comino.", "huevo", 25, [
        ing("Huevos", 4, "ud", "lacteos"),
        ing("Tomate triturado", 400, "g", "despensa"),
        ing("Pimiento rojo", 1, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Comino", 1, "pizca", "despensa", True),
        ing("Pan", 0.5, "ud", "panaderia"),
    ]),
    meal("Tortilla de calabacín", "Como la de patata pero más ligera y más rápida.", "huevo", 25, [
        ing("Huevos", 5, "ud", "lacteos"),
        ing("Calabacín", 2, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
    ]),
    meal("Huevos rellenos", "Huevos cocidos rellenos de atún y mayonesa. Se hacen antes.", "huevo", 20, [
        ing("Huevos", 6, "ud", "lacteos"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Mayonesa", 3, "cda", "despensa"),
        ing("Tomate frito", 50, "g", "despensa"),
    ]),
    meal("Tortilla de espinacas", "Con espinacas congeladas y un poco de queso.", "huevo", 20, [
        ing("Huevos", 5, "ud", "lacteos"),
        ing("Espinacas congeladas", 200, "g", "congelados"),
        ing("Queso rallado", 50, "g", "lacteos"),
    ]),
    meal("Huevos con atún", "Huevos cocidos, atún y ensalada. Cero cocina.", "huevo", 15, [
        ing("Huevos", 4, "ud", "lacteos"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Lechuga", 1, "ud", "verduras"),
        ing("Tomate", 2, "ud", "verduras"),
    ]),
]

# ---------------------------------------------------------------------------
# VERDURAS
# ---------------------------------------------------------------------------
VERDURAS = [
    meal("Crema de calabacín", "Calabacín, patata y caldo a la batidora. Infalible.", "verdura", 30, [
        ing("Calabacín", 3, "ud", "verduras"),
        ing("Patata", 1, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Caldo de verduras", 500, "ml", "despensa"),
        ing("Quesitos", 2, "ud", "lacteos"),
    ]),
    meal("Crema de calabaza", "Dulce y naranja. Con un poco de nata queda de restaurante.", "verdura", 35, [
        ing("Calabaza", 600, "g", "verduras"),
        ing("Zanahoria", 2, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Caldo de verduras", 500, "ml", "despensa"),
        ing("Nata líquida", 100, "ml", "lacteos"),
    ]),
    meal("Verduras al horno", "Todo troceado en una bandeja con aceite y sal. 40 minutos.", "verdura", 45, [
        ing("Calabacín", 1, "ud", "verduras"),
        ing("Berenjena", 1, "ud", "verduras"),
        ing("Pimiento rojo", 1, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Patata", 2, "ud", "verduras"),
    ]),
    meal("Pisto rápido", "Con verdura ya troceada congelada y tomate frito.", "verdura", 25, [
        ing("Pisto congelado", 400, "g", "congelados"),
        ing("Tomate frito", 200, "g", "despensa"),
        ing("Huevos", 2, "ud", "lacteos"),
    ]),
    meal("Salteado de brócoli", "Brócoli con ajo y guindilla. Crujiente, no papilla.", "verdura", 15, [
        ing("Brócoli", 400, "g", "verduras"),
        ing("Ajo", 3, "diente", "verduras"),
        ing("Guindilla", 1, "ud", "despensa", True),
        ing("Almendras", 40, "g", "despensa"),
    ]),
    meal("Berenjenas rellenas", "Rellenas de carne picada y gratinadas con queso.", "verdura", 45, [
        ing("Berenjena", 2, "ud", "verduras"),
        ing("Carne picada", 300, "g", "carne"),
        ing("Tomate frito", 150, "g", "despensa"),
        ing("Queso rallado", 80, "g", "lacteos"),
        ing("Cebolla", 1, "ud", "verduras"),
    ]),
    meal("Espinacas salteadas", "Espinacas con pasas y piñones. Suena fino, cuesta nada.", "verdura", 15, [
        ing("Espinacas congeladas", 400, "g", "congelados"),
        ing("Pasas", 40, "g", "despensa"),
        ing("Piñones", 30, "g", "despensa"),
        ing("Ajo", 2, "diente", "verduras"),
    ]),
    meal("Coliflor al horno", "En ramilletes con especias, queda crujiente y adictiva.", "verdura", 40, [
        ing("Coliflor", 1, "ud", "verduras"),
        ing("Pimentón", 1, "pizca", "despensa", True),
        ing("Queso rallado", 50, "g", "lacteos"),
    ]),
]

# ---------------------------------------------------------------------------
# ENSALADAS Y PLATOS FRÍOS
# ---------------------------------------------------------------------------
ENSALADAS = [
    meal("Ensalada mixta", "Lechuga, tomate, atún, maíz y huevo. La de toda la vida.", "ensalada", 10, [
        ing("Lechuga", 1, "ud", "verduras"),
        ing("Tomate", 2, "ud", "verduras"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Maíz dulce", 1, "lata", "despensa"),
        ing("Huevos", 2, "ud", "lacteos"),
        ing("Aceitunas", 60, "g", "despensa"),
    ]),
    meal("Ensalada de tomate", "Tomate bueno, cebolla, aceite y sal. No hace falta más.", "ensalada", 10, [
        ing("Tomate", 4, "ud", "verduras"),
        ing("Cebolla", 0.5, "ud", "verduras"),
        ing("Orégano", 1, "pizca", "despensa", True),
    ]),
    meal("Ensalada de quinoa", "Quinoa cocida con verduras crudas y limón. Aguanta días.", "ensalada", 25, [
        ing("Quinoa", 150, "g", "despensa"),
        ing("Pepino", 1, "ud", "verduras"),
        ing("Tomates cherry", 150, "g", "verduras"),
        ing("Aguacate", 1, "ud", "verduras"),
        ing("Limón", 1, "ud", "verduras"),
    ]),
    meal("Ensalada campera", "Patata cocida, tomate, cebolla, atún y huevo. Muy de verano.", "ensalada", 30, [
        ing("Patata", 3, "ud", "verduras"),
        ing("Tomate", 2, "ud", "verduras"),
        ing("Cebolla", 0.5, "ud", "verduras"),
        ing("Atún en lata", 2, "lata", "despensa"),
        ing("Huevos", 2, "ud", "lacteos"),
    ]),
    meal("Ensalada de aguacate", "Aguacate, tomate cherry, cebolla morada y lima.", "ensalada", 10, [
        ing("Aguacate", 2, "ud", "verduras"),
        ing("Tomates cherry", 200, "g", "verduras"),
        ing("Cebolla morada", 0.5, "ud", "verduras"),
        ing("Lima", 1, "ud", "verduras"),
    ]),
    meal("Salmorejo", "Tomate, pan, ajo y aceite a la batidora. Con jamón y huevo.", "ensalada", 15, [
        ing("Tomate", 8, "ud", "verduras"),
        ing("Pan", 200, "g", "panaderia"),
        ing("Ajo", 1, "diente", "verduras"),
        ing("Jamón serrano", 80, "g", "carne"),
        ing("Huevos", 2, "ud", "lacteos"),
    ]),
]

# ---------------------------------------------------------------------------
# BOCADILLOS Y SANDWICHES
# ---------------------------------------------------------------------------
SANDWICHES = [
    meal("Sándwich mixto", "Jamón y queso a la plancha. La cena de los días perdidos.", "sandwich", 10, [
        ing("Pan de molde", 4, "ud", "panaderia"),
        ing("Jamón cocido", 100, "g", "carne"),
        ing("Queso en lonchas", 4, "ud", "lacteos"),
        ing("Mantequilla", 15, "g", "lacteos"),
    ]),
    meal("Wrap de pollo", "Tortilla de trigo con pollo, lechuga y salsa césar.", "sandwich", 15, [
        ing("Tortillas de trigo", 4, "ud", "panaderia"),
        ing("Pechuga de pollo", 300, "g", "carne"),
        ing("Lechuga", 0.5, "ud", "verduras"),
        ing("Salsa césar", 3, "cda", "despensa"),
        ing("Tomate", 1, "ud", "verduras"),
    ]),
    meal("Bocadillo de tortilla", "Tortilla francesa dentro de una barra. Sagrado.", "sandwich", 15, [
        ing("Pan", 1, "ud", "panaderia"),
        ing("Huevos", 4, "ud", "lacteos"),
        ing("Tomate", 1, "ud", "verduras"),
    ]),
    meal("Tostada de aguacate", "Pan tostado con aguacate machacado y huevo poché.", "sandwich", 15, [
        ing("Pan", 0.5, "ud", "panaderia"),
        ing("Aguacate", 1, "ud", "verduras"),
        ing("Huevos", 2, "ud", "lacteos"),
        ing("Limón", 0.5, "ud", "verduras"),
    ]),
]


NEW_MEALS = (
    ARROCES + PASTAS + TUBERCULOS + LEGUMBRES + CARNES
    + PESCADOS + HUEVOS + VERDURAS + ENSALADAS + SANDWICHES
)


# ---------------------------------------------------------------------------
# Comidas que YA estaban en la base de datos: solo se les añaden ingredientes,
# categoría y tiempo (no se toca su descripción original si ya tienen una).
# ---------------------------------------------------------------------------
EXISTING_MEALS = [
    meal("Pizza", "Al horno mientras pones la mesa. Un poco más de queso y orégano por encima y parece de pizzería.", "otros", 20, [
        ing("Pizza congelada", 2, "ud", "congelados"),
        ing("Queso rallado", 50, "g", "lacteos"),
        ing("Orégano", 1, "pizca", "despensa", True),
    ], base=False),
    meal("Ensalada César", "Lechuga romana, pollo a la plancha, picatostes y una lluvia de parmesano.", "ensalada", 20, [
        ing("Lechuga romana", 1, "ud", "verduras"),
        ing("Pechuga de pollo", 300, "g", "carne"),
        ing("Salsa césar", 4, "cda", "despensa"),
        ing("Picatostes", 80, "g", "panaderia"),
        ing("Queso parmesano", 50, "g", "lacteos"),
    ]),
    meal("Sopa de verduras", "Todo a la olla con caldo y media hora de fuego suave. La cena de los días de frío.", "verdura", 35, [
        ing("Puerro", 2, "ud", "verduras"),
        ing("Zanahoria", 2, "ud", "verduras"),
        ing("Patata", 2, "ud", "verduras"),
        ing("Judías verdes", 200, "g", "verduras"),
        ing("Caldo de verduras", 700, "ml", "despensa"),
    ]),
    meal("Pollo al horno", "Pollo, patata y cebolla a la bandeja con vino y limón. El horno hace el trabajo.", "carne", 60, [
        ing("Pollo troceado", 1000, "g", "carne"),
        ing("Patata", 4, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Vino blanco", 100, "ml", "otros"),
        ing("Limón", 1, "ud", "verduras"),
    ]),
    meal("Paella", "La del domingo: sofrito, arroz, el caldo bien medido y no volver a tocarla.", "arroz", 60, [
        ing("Arroz", 200, "g", "despensa"),
        ing("Pollo troceado", 400, "g", "carne"),
        ing("Gambas peladas", 200, "g", "congelados"),
        ing("Judías verdes", 150, "g", "verduras"),
        ing("Pimiento rojo", 1, "ud", "verduras"),
        ing("Azafrán", 1, "pizca", "despensa", True),
        ing("Caldo de pescado", 500, "ml", "despensa"),
    ]),
    meal("Gazpacho", "Todo a la batidora, un buen rato de nevera y a beberlo bien frío.", "ensalada", 15, [
        ing("Tomate", 8, "ud", "verduras"),
        ing("Pepino", 1, "ud", "verduras"),
        ing("Pimiento verde", 1, "ud", "verduras"),
        ing("Ajo", 1, "diente", "verduras"),
        ing("Pan", 100, "g", "panaderia"),
        ing("Vinagre", 1, "cda", "despensa", True),
    ]),
    meal("Tortilla de patata", "Patata pochada con calma, huevo y el momento de darle la vuelta con el plato.", "huevo", 40, [
        ing("Patata", 4, "ud", "verduras"),
        ing("Huevos", 6, "ud", "lacteos"),
        ing("Cebolla", 1, "ud", "verduras"),
    ]),
    meal("Jamón ibérico", "Un buen plato de jamón con pan y tomate. No necesita nada más.", "otros", 5, [
        ing("Jamón ibérico", 150, "g", "carne"),
        ing("Pan", 0.5, "ud", "panaderia"),
        ing("Tomate", 1, "ud", "verduras"),
    ], base=False),
    meal("Patatas bravas", "Patata en dados bien frita, salsa brava por encima y un hilo de mayonesa.", "patata", 35, [
        ing("Patata", 5, "ud", "verduras"),
        ing("Salsa brava", 100, "g", "despensa"),
        ing("Mayonesa", 3, "cda", "despensa"),
    ]),
    meal("Cocido", "Puchero de domingo: primero la sopa de fideos y después los garbanzos con la carne.", "legumbre", 90, [
        ing("Garbanzos cocidos", 2, "lata", "despensa"),
        ing("Morcillo de ternera", 300, "g", "carne"),
        ing("Chorizo", 150, "g", "carne"),
        ing("Morcilla", 1, "ud", "carne"),
        ing("Repollo", 0.5, "ud", "verduras"),
        ing("Patata", 3, "ud", "verduras"),
        ing("Zanahoria", 2, "ud", "verduras"),
        ing("Fideos", 80, "g", "despensa"),
    ]),
    meal("Fabada asturiana", "Alubias con el compango a fuego lento. La siesta de después va incluida.", "legumbre", 60, [
        ing("Alubias cocidas", 3, "lata", "despensa"),
        ing("Chorizo", 150, "g", "carne"),
        ing("Morcilla", 1, "ud", "carne"),
        ing("Panceta", 150, "g", "carne"),
        ing("Pimentón", 1, "pizca", "despensa", True),
    ]),
    meal("Huevos rotos", "Patatas fritas, jamón serrano y dos huevos rotos por encima con el tenedor.", "huevo", 25, [
        ing("Patata", 4, "ud", "verduras"),
        ing("Huevos", 4, "ud", "lacteos"),
        ing("Jamón serrano", 100, "g", "carne"),
    ]),
    meal("Gambas al ajillo", "Gambas, mucho ajo y una guindilla en aceite hirviendo. Pan para mojar, obligatorio.", "pescado", 15, [
        ing("Gambas peladas", 400, "g", "congelados"),
        ing("Ajo", 5, "diente", "verduras"),
        ing("Guindilla", 1, "ud", "despensa", True),
        ing("Pan", 0.5, "ud", "panaderia"),
    ]),
    meal("Calamares en su tinta", "Calamares guisados en su tinta, con arroz blanco al lado para acompañar.", "pescado", 45, [
        ing("Anillas de calamar", 500, "g", "congelados"),
        ing("Tinta de calamar", 2, "sobre", "pescado"),
        ing("Cebolla", 2, "ud", "verduras"),
        ing("Tomate triturado", 200, "g", "despensa"),
        ing("Arroz", 160, "g", "despensa"),
    ]),
    meal("Migas", "Pan del día anterior con chorizo y panceta, removiendo sin parar hasta que quedan sueltas.", "otros", 40, [
        ing("Pan", 400, "g", "panaderia"),
        ing("Chorizo", 150, "g", "carne"),
        ing("Panceta", 150, "g", "carne"),
        ing("Ajo", 4, "diente", "verduras"),
        ing("Pimentón", 1, "pizca", "despensa", True),
    ]),
    meal("Fideuà", "Como la paella pero con fideos: se hacen en el caldo del marisco y quedan de pie.", "pasta", 45, [
        ing("Fideos", 250, "g", "despensa"),
        ing("Gambas peladas", 250, "g", "congelados"),
        ing("Anillas de calamar", 200, "g", "congelados"),
        ing("Caldo de pescado", 600, "ml", "despensa"),
        ing("Tomate triturado", 150, "g", "despensa"),
    ]),
    meal("Escalivada", "Berenjena, pimiento y cebolla asados enteros, pelados en tiras y con su aceite.", "verdura", 60, [
        ing("Berenjena", 2, "ud", "verduras"),
        ing("Pimiento rojo", 2, "ud", "verduras"),
        ing("Cebolla", 2, "ud", "verduras"),
    ]),
    meal("Escabeche", "Bonito con cebolla, zanahoria y vinagre. Está mejor hecho de un día para otro.", "pescado", 40, [
        ing("Bonito", 400, "g", "pescado"),
        ing("Cebolla", 2, "ud", "verduras"),
        ing("Zanahoria", 2, "ud", "verduras"),
        ing("Vinagre", 100, "ml", "despensa"),
        ing("Laurel", 1, "pizca", "despensa", True),
    ]),
    meal("Ropa vieja", "Lo que sobró del cocido, salteado con los garbanzos y tomate. Cero desperdicio.", "legumbre", 30, [
        ing("Garbanzos cocidos", 2, "lata", "despensa"),
        ing("Carne de cocido", 300, "g", "carne"),
        ing("Tomate frito", 200, "g", "despensa"),
        ing("Pimiento verde", 1, "ud", "verduras"),
    ]),
    meal("Marmitako", "Guiso de patata y bonito: la patata se chasca al cortarla para que espese el caldo.", "pescado", 50, [
        ing("Bonito", 400, "g", "pescado"),
        ing("Patata", 4, "ud", "verduras"),
        ing("Pimiento verde", 1, "ud", "verduras"),
        ing("Cebolla", 1, "ud", "verduras"),
        ing("Caldo de pescado", 500, "ml", "despensa"),
    ]),
    meal("Pisto manchego", "Verdura pochada con calma y tomate. Con un huevo frito encima ya es cena completa.", "verdura", 45, [
        ing("Calabacín", 2, "ud", "verduras"),
        ing("Berenjena", 1, "ud", "verduras"),
        ing("Pimiento rojo", 1, "ud", "verduras"),
        ing("Pimiento verde", 1, "ud", "verduras"),
        ing("Tomate triturado", 400, "g", "despensa"),
        ing("Cebolla", 1, "ud", "verduras"),
    ]),
    meal("Caparrones", "Alubia roja con chorizo y panceta, a fuego bajo y sin ninguna prisa.", "legumbre", 60, [
        ing("Alubias rojas", 3, "lata", "despensa"),
        ing("Chorizo", 150, "g", "carne"),
        ing("Panceta", 100, "g", "carne"),
        ing("Cebolla", 1, "ud", "verduras"),
    ]),
    meal("Chistorra", "Dos minutos de sartén y a la mesa, en pan o con unas patatas.", "carne", 15, [
        ing("Chistorra", 300, "g", "carne"),
        ing("Pan", 0.5, "ud", "panaderia"),
        ing("Patata", 3, "ud", "verduras"),
    ], base=False),
    meal("Morcilla", "Morcilla a la plancha con pimiento verde frito y pan para acompañar.", "carne", 20, [
        ing("Morcilla", 2, "ud", "carne"),
        ing("Pan", 0.5, "ud", "panaderia"),
        ing("Pimiento verde", 2, "ud", "verduras"),
    ]),
    meal("Burguer King", "Día de no cocinar: se pide, se recoge y a cenar en el sofá.", "otros", 5, [], base=False),
]


ALL_MEALS = NEW_MEALS + EXISTING_MEALS
