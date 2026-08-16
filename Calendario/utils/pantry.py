# Calendario/utils/pantry.py
"""
Reglas de la despensa: qué entra en el stock, dónde se guarda y cuándo caduca.

Vive aparte (y sin tocar la base de datos) porque es la parte delicada: sumar
lo que compras a lo que ya tienes en casa hay que hacerlo bien a la primera. Si
se equivoca, la despensa deja de valer para nada — nadie confía en un stock que
dice "3 litros de leche" cuando en la nevera hay uno.

Dos reglas mandan sobre todo lo demás:

- **Se suma en la unidad que ya tenía el producto en casa.** Si tienes 500 ml de
  leche y compras 1 l, quedan 1,5 l. Cuando las unidades no se pueden mezclar
  (2 latas y 300 g), no se inventa una suma: va a una fila aparte, igual que
  hace la lista de la compra con lo que genera el menú semanal.
- **Desmarcar es deshacer.** Quitar el tic de "comprado" resta exactamente lo
  que había sumado, y si el producto se queda a cero y no tenías nada anotado
  sobre él (mínimo, caducidad, nota), la fila desaparece: era un despiste, no
  un producto que se te ha acabado.
"""

from datetime import date, datetime
from typing import Optional

from Calendario.utils.purchase import convert_qty

#Dónde se guarda lo que compras, según la sección del súper de la que venga.
#Es solo el valor de partida: se puede cambiar producto a producto.
PLACE_BY_CATEGORY = {
    "verduras":   "nevera",
    "carne":      "nevera",
    "pescado":    "nevera",
    "lacteos":    "nevera",
    "congelados": "congelador",
    "panaderia":  "despensa",
    "despensa":   "despensa",
    "otros":      "despensa",
}

#Lo que va a la sección de fruta y verdura pero en casa NO se mete en la nevera
FUERA_DE_LA_NEVERA = (
    "patata", "boniato", "cebolla", "ajo", "calabaza", "plátano", "platano",
    "melón", "melon", "sandía", "sandia", "aguacate",
)

#Si el propio nombre dice que viene congelado, manda el nombre
CONGELADO_HINTS = ("congelad", "helado")

#A partir de aquí se avisa de que algo está a punto de caducar
DIAS_AVISO_CADUCIDAD = 3


def guess_place(cat: str, name: str = "") -> str:
    """Dónde se guarda un producto, a partir de su sección del súper y su nombre.

        guess_place("lacteos")                -> "nevera"
        guess_place("verduras", "Patatas")    -> "despensa"
        guess_place("verduras", "Guisantes congelados") -> "congelador"
    """
    lowered = (name or "").strip().lower()
    for hint in CONGELADO_HINTS:
        if hint in lowered:
            return "congelador"
    place = PLACE_BY_CATEGORY.get((cat or "").strip().lower(), "despensa")
    if place == "nevera" and any(hint in lowered for hint in FUERA_DE_LA_NEVERA):
        return "despensa"
    return place


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def new_entry(
    qty: float,
    unit: str = "ud",
    place: str = "despensa",
    cat: str = "otros",
    shop: str = "",
    note: str = "",
    min_qty: float = 0,
    expires: str = "",
) -> dict:
    """Una fila de despensa recién creada, con todos sus campos puestos."""
    return {
        "quantity": round(float(qty), 3),
        "unit": unit or "ud",
        "place": place if place in ("nevera", "congelador", "despensa", "otros") else "despensa",
        "cat": cat or "otros",
        "shop": shop or "",
        "note": note or "",
        "min_qty": round(float(min_qty or 0), 3),
        "expires": expires or "",
        "updated_at": now_iso(),
    }


def normalize_entry(data: dict) -> dict:
    """Rellena los campos que falten (filas viejas o escritas a medias)."""
    data = data or {}
    return {
        "quantity": float(data.get("quantity", 0) or 0),
        "unit": data.get("unit") or "ud",
        "place": data.get("place") or "despensa",
        "cat": data.get("cat") or "otros",
        "shop": data.get("shop") or "",
        "note": data.get("note") or "",
        "min_qty": float(data.get("min_qty", 0) or 0),
        "expires": data.get("expires") or "",
        "updated_at": data.get("updated_at") or "",
    }


def stock_key(items: dict, name: str, unit: str) -> str:
    """Bajo qué clave hay que guardar `name` medido en `unit`.

    Si ya está en casa con una unidad que se puede convertir, es la suya: se
    suma dentro de la misma fila. Si no, "Leche (lata)" aparte, porque sumar
    2 latas con 300 ml daría un número que no significa nada.
    """
    actual = items.get(name)
    if actual is None:
        return name
    if convert_qty(1, unit, actual.get("unit") or "ud") is not None:
        return name
    return f"{name} ({unit})"


def add_to_stock(items: dict, name: str, qty: float, unit: str, defaults: Optional[dict] = None) -> dict:
    """Suma al stock lo que acabas de comprar. Devuelve el JSON nuevo.

    `defaults` son los datos del producto en la lista de la compra (sección,
    supermercado, nota): solo se usan para **estrenar** la fila. Lo que ya
    tuvieras anotado en casa (dónde se guarda, cuándo caduca, el mínimo) no se
    pisa nunca: lo sabes tú mejor que el ticket del súper.
    """
    defaults = defaults or {}
    cantidad = float(qty or 0)
    if cantidad <= 0:
        return dict(items or {})

    result = {n: dict(d) for n, d in (items or {}).items()}
    clave = stock_key(result, name, unit)
    actual = result.get(clave)

    if actual is None:
        cat = defaults.get("cat") or "otros"
        result[clave] = new_entry(
            qty=cantidad,
            unit=unit,
            place=defaults.get("place") or guess_place(cat, name),
            cat=cat,
            shop=defaults.get("shop") or "",
            note=defaults.get("note") or "",
        )
        return result

    actual = normalize_entry(actual)
    convertida = convert_qty(cantidad, unit, actual["unit"])
    #`stock_key` ya ha garantizado que se pueden mezclar; esto es el cinturón
    if convertida is None:
        convertida = cantidad
    actual["quantity"] = round(actual["quantity"] + convertida, 3)
    actual["updated_at"] = now_iso()
    result[clave] = actual
    return result


def take_from_stock(items: dict, name: str, qty: float, unit: str) -> dict:
    """Resta del stock. Devuelve el JSON nuevo.

    Vale para las dos formas de gastar: deshacer un "comprado" marcado sin
    querer y descontar lo que te acabas de comer.

    Se resta de la fila **que se pueda medir en esa unidad**, que no siempre es
    la que se llama igual: si en casa hay "Atún" en latas y "Atún (g)" en
    gramos, deshacer una compra de 200 g tiene que tocar la segunda. Si no hay
    ninguna que encaje, no se toca nada: restar 200 g de 3 latas no significa
    nada, y hacerlo dejaba la fila en negativo y la borraba.
    """
    cantidad = float(qty or 0)
    if cantidad <= 0:
        return dict(items or {})

    result = {n: dict(d) for n, d in (items or {}).items()}
    clave = next(
        (
            c for c in (name, f"{name} ({unit})")
            if c in result and convert_qty(1, unit, result[c].get("unit") or "ud") is not None
        ),
        None,
    )
    if clave is None:
        return result

    actual = normalize_entry(result[clave])
    convertida = convert_qty(cantidad, unit, actual["unit"])
    restante = round(actual["quantity"] - (cantidad if convertida is None else convertida), 3)

    #A cero, la fila sobra: era un tic sin querer. Solo se conserva (en cero) lo
    #que tenía un mínimo puesto, porque eso es justamente lo que dice "de esto
    #quiero estar pendiente" — y así se ve que se ha acabado y se manda a la
    #compra de un toque.
    if restante <= 0 and not actual["min_qty"]:
        del result[clave]
        return result

    actual["quantity"] = max(0.0, restante)
    actual["updated_at"] = now_iso()
    result[clave] = actual
    return result


def convert_with_pack(
    qty: float, origen: str, destino: str, pack_qty: float = 0, pack_unit: str = ""
) -> Optional[float]:
    """Convierte una cantidad usando además **el formato del envase**.

    `convert_qty` solo sabe de magnitudes (g↔kg, ml↔l), y eso deja fuera el caso
    más normal de todos: la receta pide "300 ml de leche" y en la despensa hay
    "2 briks". No son la misma magnitud, pero sí la misma cosa — lo que falta es
    saber que un brik trae 1 l, que es justo lo que guarda el catálogo
    (`pack_qty` / `pack_unit`).

        convert_with_pack(300, "ml", "brik", 1, "l")   -> 0.3
        convert_with_pack(2, "brik", "ml", 1, "l")     -> 2000.0
        convert_with_pack(300, "ml", "lata", 0, "")    -> None  (no se sabe)

    Devuelve `None` cuando sigue sin poder saberse: quien llame avisa en vez de
    inventarse un número.
    """
    directa = convert_qty(qty, origen, destino)
    if directa is not None:
        return directa
    if not pack_qty or pack_qty <= 0 or not pack_unit:
        return None

    #De medida a envases: 300 ml -> 0,3 briks
    contenido = convert_qty(qty, origen, pack_unit)
    if contenido is not None:
        return round(contenido / float(pack_qty), 3)

    #De envases a medida: 2 briks -> 2000 ml
    envasado = convert_qty(float(qty) * float(pack_qty), pack_unit, destino)
    if envasado is not None:
        return round(envasado, 3)
    return None


def is_low(entry: dict) -> bool:
    """¿Hay que reponerlo? (por debajo del mínimo que le pusiste, o a cero)."""
    entry = normalize_entry(entry)
    if entry["min_qty"] > 0:
        return entry["quantity"] <= entry["min_qty"]
    return entry["quantity"] <= 0


def parse_date(iso: str) -> Optional[date]:
    """'2026-08-20' -> date. `None` si está vacío o mal escrito."""
    if not iso:
        return None
    try:
        return date.fromisoformat(str(iso)[:10])
    except ValueError:
        return None


def expiry_status(iso: str, today: Optional[date] = None) -> tuple[str, str]:
    """(etiqueta, estado) de la caducidad, tal y como se pinta en la fila.

    El estado es "expired" | "today" | "soon" | "ok" | "" (sin fecha), y quien
    pinte decide el color: aquí no se sabe nada de la paleta.

        expiry_status("2026-08-10", date(2026, 8, 12)) -> ("Caducó hace 2 días", "expired")
        expiry_status("2026-08-14", date(2026, 8, 12)) -> ("Caduca en 2 días", "soon")
    """
    fecha = parse_date(iso)
    if fecha is None:
        return "", ""
    hoy = today or date.today()
    dias = (fecha - hoy).days
    if dias < 0:
        falta = abs(dias)
        return ("Caducó ayer" if falta == 1 else f"Caducó hace {falta} días"), "expired"
    if dias == 0:
        return "Caduca hoy", "today"
    if dias <= DIAS_AVISO_CADUCIDAD:
        return ("Caduca mañana" if dias == 1 else f"Caduca en {dias} días"), "soon"
    return f"Caduca el {fecha.strftime('%d/%m')}", "ok"


def since_label(iso: str, now: Optional[datetime] = None) -> str:
    """'Repuesto hoy', 'hace 3 días'... para saber si el dato está fresco."""
    if not iso:
        return ""
    try:
        momento = datetime.fromisoformat(str(iso))
    except ValueError:
        return ""
    ahora = now or datetime.now()
    #Las fechas se guardan sin zona; si alguna llega con ella, se compara igual
    if momento.tzinfo is not None:
        momento = momento.replace(tzinfo=None)
    dias = (ahora.date() - momento.date()).days
    if dias <= 0:
        return "hoy"
    if dias == 1:
        return "ayer"
    if dias < 30:
        return f"hace {dias} días"
    meses = dias // 30
    return "hace 1 mes" if meses == 1 else f"hace {meses} meses"
