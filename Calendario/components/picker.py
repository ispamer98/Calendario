# Calendario/components/picker.py
"""
Desplegables con buscador.

`rx.select` (el desplegable de Radix) no deja escribir para filtrar: con 40
unidades, 200 productos o las 96 horas del día en tramos de 15 minutos, eso es
una lista imposible de recorrer. Aquí está la versión con buscador, generalizada
a partir del `meal_picker` que ya existía para los platos.

**El buscador es el propio campo, no una caja dentro del desplegable.** Y no es
un capricho: dentro de un diálogo, Radix atrapa el foco, y un campo de texto
colocado dentro del desplegable (que cuelga del `body`, fuera del diálogo) NUNCA
llega a recibirlo — se podía abrir la lista pero no escribir para filtrarla.
Poniendo el buscador en el propio campo, que sí está dentro del diálogo, el foco
se queda donde tiene que estar.

Un solo `PickerState` para todos: solo hay un desplegable abierto a la vez.
`open_id` dice cuál, para que lo que escribes se vea únicamente en ese campo y
no en todos a la vez. El filtrado se hace en el navegador, sin recalcular listas
en el servidor.
"""

import itertools
from typing import Optional, Sequence

import reflex as rx

from Calendario import theme

#Identificador estable para cada desplegable: los componentes se construyen
#siempre en el mismo orden al compilar, así que el número no baila.
_SECUENCIA = itertools.count()


class PickerState(rx.State):
    """Qué desplegable está abierto y qué se está escribiendo en él."""

    open_id: str = ""
    query: str = ""

    @rx.event
    def start(self, picker_id: str):
        """Este campo pasa a ser el abierto, y el buscador empieza en blanco.

        **Es idempotente a propósito.** Se dispara desde `on_focus` y también
        desde `on_click`, porque hacía falta: al elegir una opción, `finish()`
        suelta el campo (`open_id = ""`) pero el navegador lo deja ENFOCADO. Un
        segundo clic en él no volvía a disparar `on_focus` (ya lo tenía), así
        que `open_id` se quedaba vacío, el `value` del campo seguía forzado a
        "" y **lo que se escribía no aparecía**: el desplegable parecía colgado
        hasta pinchar otro campo y volver. Con el `on_click` se recupera; con la
        guarda, un clic dentro del campo que ya está abierto no borra lo escrito.
        """
        if self.open_id != picker_id:
            self.open_id = picker_id
            self.query = ""

    @rx.event
    def type_in(self, picker_id: str, value: str):
        """Escribir en un campo lo reclama: lo tecleado siempre es suyo.

        Antes esto era un `set_query` a secas y dependía de que `start` hubiera
        pasado antes. Si por lo que fuera no había pasado (el caso del párrafo
        de arriba, o un autorrelleno del navegador), el texto se guardaba pero
        no se pintaba en ningún sitio.
        """
        self.open_id = picker_id
        self.query = value

    @rx.event
    def set_query(self, value: str):
        self.query = value

    @rx.event
    def finish(self):
        """Al elegir una opción: se cierra el buscador y el campo vuelve a
        enseñar el valor elegido."""
        self.open_id = ""
        self.query = ""

    @rx.event
    def leave(self, picker_id: str):
        """Al salir del campo: se olvida lo tecleado y vuelve el valor elegido.

        Sin esto, escribir en un desplegable y pinchar en otra parte dejaba el
        campo enseñando la búsqueda a medias en vez del valor que tiene de
        verdad — el clásico "se ha quedado buggeado". Solo suelta el campo si
        el que se va es el que estaba abierto: si no, pisaría al recién abierto.
        """
        if self.open_id == picker_id:
            self.open_id = ""
            self.query = ""

    @rx.event
    def set_open(self, picker_id: str, opened: bool):
        """Radix pide abrir o cerrar la lista (Escape, por ejemplo).

        Quien manda sobre si la lista está desplegada es `open_id`, no Radix:
        por eso esto se limita a traducir la petición al estado.
        """
        if opened:
            if self.open_id != picker_id:
                self.open_id = picker_id
                self.query = ""
        elif self.open_id == picker_id:
            self.open_id = ""
            self.query = ""


def _matches(label):
    """Var booleana: ¿esta etiqueta encaja con lo que se está escribiendo?"""
    query = PickerState.query.lower()
    if isinstance(label, str):
        return rx.Var.create(label.lower()).contains(query)
    return label.lower().contains(query)


def option(
    label,
    value,
    on_change,
    color=None,
    icon=None,
    hint=None,
    selected=None,
) -> rx.Component:
    """Una opción del desplegable, ya envuelta en su filtro."""
    #Distintivo: icono si lo hay, y si no un punto del color de la categoría
    if icon is not None:
        mark = [rx.icon(icon, size=13, color=color if color is not None else theme.MUTED, flex_shrink="0")]
    elif color is not None:
        mark = [rx.box(width="7px", height="7px", border_radius="50%", background=color, flex_shrink="0")]
    else:
        mark = []

    row = rx.popover.close(
        rx.hstack(
            *mark,
            rx.box(
                rx.text(
                    label,
                    size="2",
                    color=theme.TEXT,
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                flex="1 1 0",
                min_width="0",
                overflow="hidden",
            ),
            *([rx.text(hint, size="1", color=theme.DIM, flex_shrink="0", white_space="nowrap")]
              if hint is not None else []),
            #El tick solo si se ha dicho cuál es el valor elegido
            *([rx.cond(selected, rx.icon("check", size=13, color=theme.MEAL, flex_shrink="0"))]
              if selected is not None else []),
            width="100%",
            align="center",
            spacing="2",
            padding="7px 9px",
            border_radius="8px",
            cursor="pointer",
            #Sin esto, pulsar una opción le quita el foco al campo; el campo lo
            #recupera al soltar, dispara `start` y borra lo escrito, y encima el
            #repintado cambia el elemento entre pulsar y soltar, así que el clic
            #se pierde y no se selecciona nada. Cancelando el `mousedown` el foco
            #no se mueve y el clic llega entero.
            on_mouse_down=rx.noop().prevent_default,
            #Elegir hace dos cosas: guardar el valor y cerrar el buscador, para
            #que el campo vuelva a enseñar lo elegido en vez de lo tecleado
            on_click=[on_change(value), PickerState.finish],
            _hover={"background": theme.BG_CARD_HOVER},
        )
    )
    #Si no encaja con el buscador, no se pinta nada (ni un hueco): así el
    #contenedor se queda vacío de verdad y salta el aviso de "nada coincide"
    return rx.cond(_matches(label), row)


def picker_trigger(display, placeholder: str, picker_id: str) -> rx.Component:
    """El campo: enseña lo elegido y, al escribir en él, filtra la lista.

    Es un `input` de verdad (no una caja de texto decorativa) porque tiene que
    poder recibir el foco dentro de un diálogo. Mientras no sea el desplegable
    abierto, su contenido es "" y lo que se ve es el marcador de posición con el
    valor elegido.
    """
    #La caja exterior es la que hace de disparador y de ANCLA del desplegable.
    #Es importante que el ancla sea ella y no el campo: al escribir, el campo se
    #vuelve a montar, Radix perdía la referencia y colocaba la lista fuera de la
    #pantalla (llegué a medirla en y=-278).
    return rx.box(
        #Campo HTML pelado a propósito, NO `rx.input`: ese se convierte en un
        #`DebounceInput`, que se guarda su propio texto y no hace caso a lo que
        #le manda el servidor. Con él, al elegir una opción el texto tecleado no
        #se borraba y se iba acumulando ("hue" -> "huepas" -> "huepashue"),
        #dejando el campo enseñando lo último que buscaste en vez de lo elegido.
        rx.el.input(
            value=rx.cond(PickerState.open_id == picker_id, PickerState.query, ""),
            placeholder=rx.cond(display != "", display, placeholder),
            #Si el campo fuese el disparador, Radix le pondría `type="button"` y
            #dejaría de poder escribirse.
            type="text",
            auto_complete="off",
            on_focus=PickerState.start(picker_id),
            #El clic también reclama el campo: enfocar no basta cuando ya lo
            #estaba (ver `PickerState.start`). Y **no se deja subir**: si llega
            #al disparador, Radix lo interpreta como "alternar", y pinchar en un
            #campo ya desplegado lo cerraba en vez de dejarte poner el cursor.
            on_click=PickerState.start(picker_id).stop_propagation,
            on_change=lambda value: PickerState.type_in(picker_id, value),
            #Al salir, el campo vuelve a enseñar lo elegido en vez de la
            #búsqueda a medias. Elegir una opción NO pasa por aquí: esas
            #cancelan el `mousedown`, así que el campo no llega a perder el foco.
            on_blur=PickerState.leave(picker_id),
            class_name="picker-field",
            style={
                "width": "100%",
                "height": "32px",
                #Hueco a la derecha para la flechita
                "padding": "0 30px 0 10px",
                "borderRadius": theme.RADIUS_SM,
                "background": theme.BG_SUNKEN,
                "border": f"1px solid {theme.BORDER}",
                "color": theme.TEXT,
                "fontSize": "14px",
                "outline": "none",
                "cursor": "pointer",
            },
        ),
        rx.icon(
            "chevron-down",
            size=14,
            color=theme.MUTED,
            style={
                "position": "absolute",
                "right": "9px",
                "top": "50%",
                "transform": "translateY(-50%)",
                #La flecha no debe robar el clic al campo
                "pointerEvents": "none",
            },
        ),
        position="relative",
        width="100%",
        max_width="100%",
    )


def manage_button(on_click, title: str) -> rx.Component:
    """El engranaje que hay junto a cada desplegable para ampliar su lista.

    Es el mismo de siempre (el de unidades y categorías), ahora en **todos** los
    desplegables que salen de un catálogo: si te falta la unidad, el
    supermercado o el producto, se añade desde ahí sin salir de lo que estabas
    haciendo.
    """
    return rx.icon(
        "settings-2",
        size=15,
        color=theme.MUTED,
        cursor="pointer",
        on_click=on_click,
        _hover={"color": theme.ACCENT, "transform": "scale(1.15)"},
        transition="all 0.15s ease",
        flex_shrink="0",
        title=title,
    )


def picker(
    display,
    options,
    placeholder: str = "Elegir...",
    #Se conserva por compatibilidad con las llamadas: ya no hay caja de búsqueda
    #aparte, se escribe en el propio campo
    search_placeholder: str = "",
    footer: Optional[rx.Component] = None,
    width: str = "260px",
    size: str = "2",
    on_add=None,
    add_title: str = "Añadir a la lista",
) -> rx.Component:
    """Desplegable con buscador (y con «+» al lado si su lista se puede ampliar).

    `options` es lo que se pinta dentro: un `rx.foreach` de `option(...)`, o una
    lista de `option(...)` si las opciones son fijas.
    """
    if isinstance(options, (list, tuple)):
        options = list(options)
    else:
        options = [options]

    picker_id = f"pk{next(_SECUENCIA)}"
    campo = _popover(display, options, placeholder, footer, width, picker_id)
    if on_add is None:
        return campo
    return rx.hstack(
        rx.box(campo, flex="1 1 0", min_width="0"),
        manage_button(on_add, add_title),
        width="100%",
        spacing="2",
        align="center",
    )


def _popover(display, options, placeholder, footer, width, picker_id) -> rx.Component:
    """La lista desplegada, **abierta o cerrada según el estado**.

    Antes la abría Radix por su cuenta al pulsar el disparador, y ahí estaba el
    fallo que quedaba: si elegías una opción y seguías escribiendo sin salir del
    campo, el texto entraba (el campo tiene el foco) pero la lista NO se volvía
    a desplegar, porque nadie había vuelto a pulsar el disparador. Había que
    salir del campo y entrar otra vez para que reaccionara.

    Atando `open` a `open_id`, escribir es lo que despliega la lista: elegir,
    seguir escribiendo y elegir otra vez funciona sin tocar nada más.
    """
    return rx.popover.root(
        rx.popover.trigger(picker_trigger(display, placeholder, picker_id)),
        rx.popover.content(
            rx.vstack(
                rx.vstack(
                    *options,
                    spacing="1",
                    width="100%",
                    max_height="230px",
                    overflow_y="auto",
                    #Si el filtro no deja ninguna opción, el contenedor se queda
                    #vacío: este pseudoelemento es el "no hay resultados" sin
                    #tener que contar coincidencias en el servidor
                    style={
                        "&:empty::after": {
                            "content": '"Nada coincide con la búsqueda"',
                            "color": theme.DIM,
                            "fontSize": "12px",
                            "padding": "10px 4px",
                            "display": "block",
                        }
                    },
                ),
                *([footer] if footer is not None else []),
                spacing="2",
                width="100%",
            ),
            side="bottom",
            align="start",
            #ESTO es lo que hacía que dentro de un diálogo el desplegable se
            #abriera y se cerrara en el mismo instante: al abrirse, el popover
            #se lleva el foco, el diálogo (que atrapa el foco) se lo devuelve,
            #y el popover interpreta que ha perdido el foco y se cierra solo.
            #Cancelando ese enfoque automático se acabó la pelea.
            on_open_auto_focus=rx.noop().prevent_default,
            #Y al cerrarse, que tampoco lo mueva: el foco tiene que quedarse en
            #el campo. Es lo que permite elegir una opción y **seguir
            #escribiendo** para buscar la siguiente, sin salir y volver a entrar.
            on_close_auto_focus=rx.noop().prevent_default,
            on_focus_outside=rx.noop().prevent_default,
            #Cerrar lo decide el estado (elegir una opción o salir del campo),
            #no el detector de clics de Radix: si no, el clic de fuera cerraba
            #por su cuenta y el estado se quedaba creyendo que seguía abierto.
            on_pointer_down_outside=rx.noop().prevent_default,
            style={
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS,
                "padding": "12px",
                "width": width,
                "max_width": "92vw",
                "box_shadow": theme.SHADOW_LG,
                #OJO: aquí NO se toca el z-index. Ponerle uno propio (probé con
                #60) lo mete por debajo del velo del diálogo de Radix, y el
                #desplegable se abre pero no se puede tocar nada: parece vacío.
                #Radix ya apila bien el popover sobre el diálogo por su cuenta.
            },
        ),
        #Desplegado = este es el campo activo. Ni más ni menos.
        open=PickerState.open_id == picker_id,
        on_open_change=lambda opened: PickerState.set_open(picker_id, opened),
    )


def clear_option(on_change, label: str = "Dejar en blanco") -> rx.Component:
    """Pie del desplegable para vaciar el campo (Radix no admite valor vacío)."""
    return rx.popover.close(
        rx.hstack(
            rx.icon("eraser", size=13, color=theme.DANGER, flex_shrink="0"),
            rx.text(label, size="1", color=theme.DANGER),
            spacing="2",
            align="center",
            width="100%",
            padding="7px 9px",
            border_radius="8px",
            cursor="pointer",
            on_mouse_down=rx.noop().prevent_default,
            on_click=[on_change(""), PickerState.finish],
            _hover={"background": theme.alpha(theme.DANGER, 0.10)},
        )
    )


def manage_option(on_click, label: str, icon: str = "settings-2") -> rx.Component:
    """Pie del desplegable que lleva al gestor del catálogo correspondiente."""
    return rx.popover.close(
        rx.hstack(
            rx.icon(icon, size=13, color=theme.ACCENT, flex_shrink="0"),
            rx.text(label, size="1", color=theme.ACCENT),
            spacing="2",
            align="center",
            width="100%",
            padding="7px 9px",
            border_radius="8px",
            cursor="pointer",
            on_mouse_down=rx.noop().prevent_default,
            on_click=on_click,
            _hover={"background": theme.alpha(theme.ACCENT, 0.10)},
            border_top=f"1px solid {theme.BORDER}",
        )
    )


def static_options(entries: Sequence[tuple], on_change) -> list:
    """Opciones fijas: `(valor, etiqueta, color, icono)`."""
    return [
        option(label, value, on_change, color=color, icon=icon)
        for value, label, color, icon in entries
    ]
