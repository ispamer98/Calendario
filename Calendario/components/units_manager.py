# Calendario/components/units_manager.py
"""
Gestor de unidades de medida.

Un diálogo pequeño para añadir las unidades que uses de verdad y quitar las que
sobren. Se abre desde el icono de ajustes que hay junto a cualquier desplegable
de unidad (recetario, catálogo y lista de la compra).

Lo que este gestor tiene que dejar claro es que **la unidad es texto guardado en
cada ingrediente**, no una referencia a la tabla. Así que:

- cada unidad enseña **cuántas veces está escrita**: se ve de un vistazo si
  quitarla va a dejar cosas colgando;
- borrar una que esté en uso **pregunta antes**, y ofrece convertirla a otra;
- las que ya quedaron huérfanas (borradas del desplegable pero todavía escritas
  en las recetas) salen en su propio apartado, en rojo, con las dos salidas:
  recuperarlas o convertirlas.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.picker import option, picker
from Calendario.components.ui import icon_badge, info_banner
from Calendario.model.model import UnitUsage
from Calendario.state.units_state import UnitsState


def manage_units_button(title: str = "Gestionar unidades") -> rx.Component:
    """Icono de ajustes que abre el gestor. Va pegado al desplegable de unidad."""
    return rx.icon(
        "settings-2",
        size=15,
        color=theme.MUTED,
        cursor="pointer",
        on_click=UnitsState.open_manager,
        _hover={"color": theme.ACCENT, "transform": "scale(1.15)"},
        transition="all 0.15s ease",
        flex_shrink="0",
        title=title,
    )


def _target_picker() -> rx.Component:
    """Desplegable de «a qué unidad se convierte». Se usa en los dos flujos."""
    return picker(
        display=UnitsState.convert_to,
        options=[
            rx.foreach(
                UnitsState.convert_targets,
                lambda u: option(
                    u, u, UnitsState.set_convert_to, selected=u == UnitsState.convert_to
                ),
            )
        ],
        placeholder="Elegir unidad...",
        width="200px",
    )


def _unit_chip(row: UnitUsage) -> rx.Component:
    """Una unidad del desplegable, con la cuenta de dónde está escrita."""
    en_uso = row.count > 0
    return rx.hstack(
        rx.text(row.name, size="2", color=theme.TEXT, weight="medium"),
        #El recuento es la información que faltaba: sin él no había forma de
        #saber que borrar "g" iba a dejar 168 ingredientes señalando al vacío
        rx.cond(
            en_uso,
            rx.text(
                row.count.to_string(),
                size="1",
                color=theme.DIM,
                title="Veces que está escrita en recetas, catálogo y compra",
            ),
        ),
        #Renombrar: se carga arriba en el campo de texto
        rx.icon(
            "pencil",
            size=12,
            color=theme.MUTED,
            cursor="pointer",
            on_click=UnitsState.edit(row.name),
            _hover={"color": theme.ACCENT, "transform": "scale(1.25)"},
            transition="all 0.15s ease",
            title="Renombrar esta unidad (se cambia también donde ya se usa)",
        ),
        rx.icon(
            "x",
            size=13,
            color=theme.MUTED,
            cursor="pointer",
            on_click=UnitsState.remove(row.name),
            _hover={"color": theme.DANGER, "transform": "scale(1.25)"},
            transition="all 0.15s ease",
            title="Quitar del desplegable",
        ),
        spacing="2",
        align="center",
        padding="6px 10px",
        border_radius="999px",
        background=rx.cond(
            UnitsState.editing_unit == row.name,
            theme.alpha(theme.ACCENT, 0.14),
            theme.BG_SUNKEN,
        ),
        border=rx.cond(
            UnitsState.editing_unit == row.name,
            f"1px solid {theme.alpha(theme.ACCENT, 0.45)}",
            f"1px solid {theme.BORDER}",
        ),
        flex_shrink="0",
    )


def _delete_confirm() -> rx.Component:
    """Lo que sale al intentar borrar una unidad que está en uso.

    Es el paso que no existía: antes el aspa borraba y punto, y todo lo que
    usaba esa unidad se quedaba apuntando a algo que ya no se podía elegir.
    """
    return rx.vstack(
        rx.hstack(
            rx.icon("triangle-alert", size=15, color=theme.WARNING, flex_shrink="0"),
            rx.text(
                "'" + UnitsState.pending_delete + "' se usa en "
                + UnitsState.pending_delete_count.to_string() + " sitios",
                size="2",
                color=theme.TEXT,
                weight="medium",
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        rx.text(
            "Si la borras sin más, esas cantidades seguirán diciéndolo pero ya no podrás "
            "volver a elegirla. Lo normal es convertirlas a otra unidad.",
            size="1",
            color=theme.MUTED,
        ),
        rx.hstack(
            rx.text("CONVERTIR A", size="1", color=theme.MUTED, weight="medium", flex_shrink="0"),
            rx.box(_target_picker(), flex="1 1 0", min_width="0"),
            spacing="2",
            align="center",
            width="100%",
            wrap="wrap",
        ),
        rx.hstack(
            rx.button(
                "Cancelar",
                on_click=UnitsState.cancel_delete,
                variant="soft",
                color_scheme="gray",
                size="1",
                type="button",
                cursor="pointer",
            ),
            rx.button(
                "Borrar igualmente",
                on_click=UnitsState.confirm_delete_keeping_usages,
                variant="soft",
                color_scheme="red",
                size="1",
                type="button",
                cursor="pointer",
                loading=UnitsState.loading,
            ),
            rx.spacer(),
            rx.button(
                rx.icon("arrow-right-left", size=14),
                rx.text("Convertir y borrar", size="1"),
                on_click=UnitsState.convert_and_delete,
                color_scheme="amber",
                size="1",
                type="button",
                cursor="pointer",
                loading=UnitsState.loading,
            ),
            spacing="2",
            align="center",
            width="100%",
            wrap="wrap",
        ),
        spacing="2",
        width="100%",
        padding="12px",
        border_radius=theme.RADIUS_SM,
        background=theme.alpha(theme.WARNING, 0.08),
        border=f"1px solid {theme.alpha(theme.WARNING, 0.35)}",
    )


def _orphan_row(row: UnitUsage) -> rx.Component:
    """Una unidad que se quedó escrita en los datos sin estar en la lista."""
    convirtiendo = UnitsState.converting_orphan == row.name
    return rx.vstack(
        rx.hstack(
            rx.icon("unlink", size=13, color=theme.DANGER, flex_shrink="0"),
            rx.text(row.name, size="2", color=theme.TEXT, weight="bold"),
            rx.text(
                "en " + row.count.to_string() + " sitios",
                size="1",
                color=theme.MUTED,
                white_space="nowrap",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("undo-2", size=13),
                rx.text("Recuperar", size="1"),
                on_click=UnitsState.restore_orphan(row.name),
                variant="soft",
                color_scheme="gray",
                size="1",
                type="button",
                cursor="pointer",
                title="Volver a meterla en el desplegable tal cual está escrita",
            ),
            rx.button(
                rx.icon("arrow-right-left", size=13),
                rx.text("Convertir", size="1"),
                on_click=UnitsState.start_orphan_convert(row.name),
                variant="soft",
                color_scheme="amber",
                size="1",
                type="button",
                cursor="pointer",
                title="Reescribirla como una de las unidades que sí existen",
            ),
            spacing="2",
            align="center",
            width="100%",
            wrap="wrap",
        ),
        rx.cond(
            convirtiendo,
            rx.hstack(
                rx.text("PASAR TODO A", size="1", color=theme.MUTED, weight="medium", flex_shrink="0"),
                rx.box(_target_picker(), flex="1 1 0", min_width="0"),
                rx.button(
                    rx.icon("check", size=14),
                    on_click=UnitsState.convert_orphan,
                    color_scheme="amber",
                    size="1",
                    type="button",
                    cursor="pointer",
                    loading=UnitsState.loading,
                ),
                rx.button(
                    rx.icon("x", size=14),
                    on_click=UnitsState.cancel_orphan_convert,
                    variant="soft",
                    color_scheme="gray",
                    size="1",
                    type="button",
                    cursor="pointer",
                ),
                spacing="2",
                align="center",
                width="100%",
                wrap="wrap",
            ),
        ),
        spacing="2",
        width="100%",
        padding="10px 12px",
        border_radius=theme.RADIUS_SM,
        background=theme.alpha(theme.DANGER, 0.07),
        border=f"1px solid {theme.alpha(theme.DANGER, 0.3)}",
    )


def _orphans_section() -> rx.Component:
    return rx.cond(
        UnitsState.has_orphans,
        rx.vstack(
            rx.hstack(
                rx.icon("unlink", size=13, color=theme.DANGER),
                rx.text(
                    "UNIDADES SIN LISTA",
                    size="1",
                    color=theme.DANGER,
                    weight="bold",
                    letter_spacing="0.1em",
                ),
                rx.text(UnitsState.orphan_count.to_string(), size="1", color=theme.DIM),
                spacing="2",
                align="center",
            ),
            rx.text(
                "Están escritas en tus recetas, en el catálogo o en la compra, pero ya no "
                "salen en ningún desplegable. Recupéralas o conviértelas.",
                size="1",
                color=theme.MUTED,
            ),
            rx.vstack(
                rx.foreach(UnitsState.orphans, _orphan_row),
                spacing="2",
                width="100%",
                max_height="200px",
                overflow_y="auto",
                overflow_x="hidden",
            ),
            spacing="2",
            width="100%",
            align="start",
        ),
    )


def units_manager_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("ruler", theme.ACCENT, size=18, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Unidades de medida", margin="0", size="4", weight="bold"),
                        rx.text(
                            "Las que uses tú, no las que traía la app",
                            size="1",
                            color=theme.MUTED,
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.icon(
                        "x",
                        size=18,
                        color=theme.MUTED,
                        cursor="pointer",
                        on_click=UnitsState.close_manager,
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),

                #Alta y renombrado
                rx.vstack(
                    rx.hstack(
                        rx.icon(
                            rx.cond(UnitsState.is_editing, "pencil", "plus"),
                            size=13,
                            color=rx.cond(UnitsState.is_editing, theme.ACCENT, theme.MEAL),
                        ),
                        rx.text(
                            rx.cond(UnitsState.is_editing, "RENOMBRANDO UNIDAD", "NUEVA UNIDAD"),
                            size="1",
                            color=theme.MUTED,
                            weight="medium",
                        ),
                        rx.spacer(),
                        rx.cond(
                            UnitsState.is_editing,
                            rx.text(
                                "Cancelar",
                                size="1",
                                color=theme.MUTED,
                                cursor="pointer",
                                on_click=UnitsState.cancel_edit,
                                _hover={"color": theme.DANGER, "text_decoration": "underline"},
                            ),
                        ),
                        width="100%",
                        align="center",
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.input(
                            placeholder="Nueva unidad (ej. bote, bolsa, docena...)",
                            value=UnitsState.new_unit,
                            on_change=UnitsState.set_new_unit,
                            size="2",
                            max_length=12,
                            flex="1 1 0",
                            min_width="0",
                            id="unidad-nombre",
                        ),
                        rx.button(
                            rx.icon(rx.cond(UnitsState.is_editing, "check", "plus"), size=16),
                            rx.text(rx.cond(UnitsState.is_editing, "Guardar", "Añadir"), size="2"),
                            on_click=UnitsState.add,
                            color_scheme=rx.cond(UnitsState.is_editing, "blue", "green"),
                            size="2",
                            type="button",
                            loading=UnitsState.loading,
                            flex_shrink="0",
                            cursor="pointer",
                        ),
                        width="100%",
                        spacing="2",
                        align="center",
                    ),
                    spacing="2",
                    width="100%",
                ),

                #Confirmación de borrado, solo cuando la unidad está en uso
                rx.cond(UnitsState.is_confirming_delete, _delete_confirm()),

                #Listado actual
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            "EN EL DESPLEGABLE",
                            size="1",
                            color=theme.DIM,
                            weight="bold",
                            letter_spacing="0.1em",
                        ),
                        rx.text(UnitsState.unit_count.to_string(), size="1", color=theme.DIM),
                        spacing="2",
                        align="center",
                    ),
                    rx.flex(
                        rx.foreach(UnitsState.rows, _unit_chip),
                        wrap="wrap",
                        gap="8px",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                    align="start",
                    max_height="200px",
                    overflow_y="auto",
                ),

                _orphans_section(),

                info_banner(
                    "El número que hay junto a cada unidad es las veces que está escrita en tus "
                    "recetas, catálogo y compra. Renombrarla la cambia en todas ellas; borrarla "
                    "solo la quita del desplegable, y por eso se avisa antes.",
                    icon="info",
                    color=theme.ACCENT,
                ),

                rx.hstack(
                    rx.button(
                        "Listo",
                        on_click=UnitsState.close_manager,
                        color_scheme="gray",
                        variant="soft",
                        size="2",
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            style={
                "max_width": "460px",
                "max_height": "88vh",
                "overflow_y": "auto",
                "overflow_x": "hidden",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=UnitsState.show_manager,
        #`open` es un estado controlado: sin `on_open_change`, Radix pide cerrar
        #(Escape, clic fuera) y nadie le hace caso, así que el gestor solo se
        #podía cerrar con la X o con "Listo". Con esto se cierra como cualquier
        #otro diálogo, y el estado se entera.
        on_open_change=UnitsState.toggle_manager,
    )
