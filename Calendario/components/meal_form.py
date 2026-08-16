# Calendario/components/meal_form.py
"""
Diálogo de alta/edición de comidas.

Sustituye al antiguo `new_meal_input` (nombre + descripción y poco más). Ahora
además de la categoría y el tiempo, se editan los **ingredientes**, que son la
materia prima de la lista de la compra automática.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import icon_badge, info_banner, pill
from Calendario.components.item_fields import (
    field,
    field_label,
    note_input,
    qty_input,
    section_select,
    shop_select,
    staple_switch,
    units_select,
)
from Calendario.components.picker import manage_option, option, picker
from Calendario.components.products_manager import product_picker
from Calendario.state.calendar_state import CalendarState
from Calendario.model.model import Ingredient
from Calendario.state.meal_form_state import MealFormState


def _label(text: str) -> rx.Component:
    return field_label(text)


def _category_select() -> rx.Component:
    """Categoría del plato, con buscador y acceso al gestor."""
    return picker(
        display=MealFormState.category_label,
        options=[
            rx.foreach(
                CalendarState.categories,
                lambda cat: option(
                    cat.label, cat.key, MealFormState.set_category,
                    color=cat.color, icon=cat.icon,
                    selected=cat.key == MealFormState.category,
                ),
            )
        ],
        placeholder="Categoría",
        search_placeholder="Buscar categoría...",
        footer=manage_option(CalendarState.open_category_manager, "Gestionar categorías"),
        width="250px",
        on_add=CalendarState.open_category_manager,
        add_title="Añadir una categoría nueva",
    )


def _section_color(cat: rx.Var[str]):
    """Color de la sección del súper. `rx.match` porque las secciones son fijas."""
    return rx.match(
        cat,
        *[(key, style["color"]) for key, style in theme.SHOP_CATEGORY_STYLE.items()],
        theme.MUTED,
    )


def _section_label(cat: rx.Var[str]):
    return rx.match(
        cat,
        *[(key, style["label"]) for key, style in theme.SHOP_CATEGORY_STYLE.items()],
        "Otros",
    )


def _mini_chip(text, color: str, icon: str = "") -> rx.Component:
    """Etiqueta diminuta para los datos secundarios del ingrediente."""
    return rx.hstack(
        #El icono se decide en Python, no con `rx.cond`: sin icono no debe
        #llegar a construirse un `rx.icon("")`
        *([rx.icon(icon, size=10, color=color, flex_shrink="0")] if icon else []),
        rx.text(
            text,
            size="1",
            color=color,
            white_space="nowrap",
            overflow="hidden",
            text_overflow="ellipsis",
        ),
        spacing="1",
        align="center",
        padding="1px 7px",
        border_radius="999px",
        background=theme.alpha(theme.TEXT, 0.04),
        border=f"1px solid {theme.BORDER}",
        max_width="130px",
        flex_shrink="0",
    )


def _ingredient_row(item: rx.Var[Ingredient], index: rx.Var[int]) -> rx.Component:
    """Un ingrediente ya añadido, con TODOS sus datos a la vista y editable."""
    color = _section_color(item.cat)
    return rx.hstack(
        rx.box(
            width="6px",
            height="6px",
            border_radius="50%",
            background=color,
            flex_shrink="0",
            title="Sección del súper",
        ),
        #`min_width: 0` es lo que permite que el texto se recorte en vez de
        #empujar la cantidad y la papelera fuera de la tarjeta
        rx.box(
          rx.popover.root(
            rx.popover.trigger(
                rx.text(
                    item.name,
                    size="2",
                    weight="medium",
                    color=theme.TEXT,
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                    cursor="pointer",
                    width="100%",
                    title="Ver la ficha completa",
                ),
            ),
            rx.popover.content(
                rx.vstack(
                    rx.text(item.name, size="2", weight="bold", color=theme.TEXT),
                    rx.hstack(
                        rx.icon("scale", size=12, color=theme.MUTED),
                        rx.text(
                            item.qty.to_string() + " " + item.unit,
                            size="1",
                            color=theme.MUTED,
                        ),
                        spacing="2", align="center",
                    ),
                    rx.hstack(
                        rx.icon("layout-grid", size=12, color=color),
                        rx.text(_section_label(item.cat), size="1", color=theme.MUTED),
                        spacing="2", align="center",
                    ),
                    rx.cond(
                        item.shop != "",
                        rx.hstack(
                            rx.icon("store", size=12, color=theme.WARNING),
                            rx.text(item.shop, size="1", color=theme.MUTED),
                            spacing="2", align="center",
                        ),
                    ),
                    rx.cond(
                        item.staple,
                        rx.hstack(
                            rx.icon("package", size=12, color=theme.PURPLE),
                            rx.text("Básico de despensa", size="1", color=theme.MUTED),
                            spacing="2", align="center",
                        ),
                    ),
                    rx.cond(
                        item.note != "",
                        rx.hstack(
                            rx.icon("sticky-note", size=12, color=theme.ACCENT),
                            rx.text(item.note, size="1", color=theme.MUTED),
                            spacing="2", align="start",
                        ),
                    ),
                    spacing="1",
                    align="start",
                ),
                side="top",
                style={
                    "background": theme.BG_WINDOW,
                    "border": f"1px solid {theme.BORDER_STRONG}",
                    "border_radius": "10px",
                    "padding": "10px 12px",
                    "max_width": "280px",
                    "width": "auto",
                    "box_shadow": theme.SHADOW,
                },
            ),
          ),
          #Los datos secundarios, en su propia línea de etiquetas. La cantidad
          #va aquí también: así el nombre se queda la primera línea entera.
          rx.hstack(
              _mini_chip(item.qty.to_string() + " " + item.unit, theme.TEXT, "scale"),
              _mini_chip(_section_label(item.cat), color),
              rx.cond(item.shop != "", _mini_chip(item.shop, theme.WARNING, "store")),
              rx.cond(item.staple, _mini_chip("Básico", theme.PURPLE, "package")),
              rx.cond(item.note != "", _mini_chip(item.note, theme.ACCENT, "sticky-note")),
              spacing="1",
              align="center",
              wrap="wrap",
              width="100%",
              margin_top="3px",
          ),
          #Es este contenedor el que necesita `min-width: 0`: sin él, el nombre
          #empuja la cantidad y la papelera fuera de la tarjeta
          flex="1 1 0",
          min_width="0",
          width="100%",
          overflow="hidden",
        ),
        #Sin `rx.spacer()`: era otro hijo flexible y se comía el hueco del nombre
        rx.icon(
            "pencil",
            size=15,
            color=theme.MUTED,
            cursor="pointer",
            on_click=MealFormState.edit_ingredient(index),
            _hover={"color": theme.ACCENT, "transform": "scale(1.25)"},
            flex_shrink="0",
            title="Editar este ingrediente (nombre, cantidad, unidad, súper...)",
        ),
        rx.icon(
            "x",
            size=15,
            color=theme.DANGER,
            cursor="pointer",
            on_click=MealFormState.remove_ingredient(index),
            _hover={"transform": "scale(1.25)"},
            flex_shrink="0",
            title="Quitar",
        ),
        #Ancla para `rx.scroll_to`: al añadir o al toparse con uno repetido, la
        #vista baja hasta él. Sin esto el ingrediente se añadía al final de una
        #lista con scroll propio y no se veía nada moverse — de ahí el "dice que
        #ya está pero no lo veo".
        id="ingrediente-" + index.to_string(),
        width="100%",
        max_width="100%",
        align="center",
        spacing="3",
        padding="10px 12px",
        min_height="62px",
        #La lista de ingredientes también tiene altura limitada: sin esto sus
        #fichas se encogen y el nombre sale cortado
        flex_shrink="0",
        border_radius=theme.RADIUS_SM,
        background=rx.cond(
            MealFormState.ing_index == index,
            theme.alpha(theme.ACCENT, 0.1),
            theme.BG_SUNKEN,
        ),
        border=rx.cond(
            MealFormState.ing_index == index,
            f"1px solid {theme.alpha(theme.ACCENT, 0.45)}",
            f"1px solid {theme.BORDER}",
        ),
        overflow="hidden",
    )


def _add_ingredient_button() -> rx.Component:
    """Lo único que se ve del formulario cuando está plegado.

    El formulario del ingrediente son ocho campos, y tenerlos siempre a la
    vista dejaba la lista de lo que lleva la receta arrinconada abajo del todo.
    Plegado por defecto, se despliega al pulsar aquí (o el lápiz de cualquier
    ingrediente ya añadido).
    """
    return rx.hstack(
        rx.icon("plus", size=16, color=theme.MEAL, flex_shrink="0"),
        rx.text("Añadir ingrediente", size="2", color=theme.MEAL, weight="medium"),
        rx.spacer(),
        rx.text("del catálogo de productos", size="1", color=theme.DIM, white_space="nowrap"),
        width="100%",
        align="center",
        spacing="2",
        padding="10px 12px",
        cursor="pointer",
        border_radius=theme.RADIUS_SM,
        background=theme.alpha(theme.MEAL, 0.07),
        border=f"1px dashed {theme.alpha(theme.MEAL, 0.45)}",
        on_click=MealFormState.open_ingredient_form,
        _hover={"background": theme.alpha(theme.MEAL, 0.14)},
        transition="background 0.15s ease",
    )


def _ingredient_form() -> rx.Component:
    """Alta y edición de un ingrediente, con todos sus campos etiquetados.

    Antes esto era una sola fila con cinco controles apretados: en el diálogo
    (520 px) la sección del súper quedaba reducida a un desplegable ilegible y
    el supermercado directamente no existía. Ahora cada campo lleva su etiqueta
    y un ancho mínimo, así que si no caben saltan de línea en vez de encogerse
    hasta desaparecer.
    """
    return rx.vstack(
        rx.hstack(
            rx.icon(
                rx.cond(MealFormState.is_editing_ingredient, "pencil", "plus"),
                size=13,
                color=rx.cond(MealFormState.is_editing_ingredient, theme.ACCENT, theme.MEAL),
            ),
            _label(MealFormState.ingredient_form_title),
            rx.spacer(),
            #Plegarlo sin guardar. Vale para los dos casos (alta y edición), así
            #que sustituye al antiguo "Cancelar edición" que solo salía al editar
            rx.icon(
                "x",
                size=15,
                color=theme.MUTED,
                cursor="pointer",
                on_click=MealFormState.cancel_ingredient_edit,
                _hover={"color": theme.DANGER, "transform": "scale(1.2)"},
                title="Cerrar sin guardar",
                flex_shrink="0",
            ),
            width="100%",
            align="center",
            spacing="2",
        ),

        rx.vstack(
            _label("PRODUCTO"),
            #Del catálogo, no a mano: dentro del desplegable se busca, se crea
            #el que falte y se corrige cualquiera con el lápiz
            product_picker(
                MealFormState.ing_name,
                MealFormState.pick_ingredient,
                placeholder="Elegir producto del catálogo...",
            ),
            spacing="1",
            width="100%",
            align="start",
        ),

        #Los cuatro campos que definen dónde y cómo se compra. `wrap` para que
        #en el móvil bajen de línea enteros en vez de estrujarse.
        rx.flex(
            field(
                "CANTIDAD",
                rx.input(
                    value=MealFormState.ing_qty,
                    on_change=MealFormState.set_ing_qty,
                    type="number",
                    size="2",
                    width="100%",
                    #Al editar un ingrediente de la lista, el foco sube aquí
                    id="ingrediente-cantidad",
                ),
                "88px",
                grow=False,
            ),
            field("UNIDAD", units_select(MealFormState.ing_unit, MealFormState.set_ing_unit), "140px"),
            field("SECCIÓN DEL SÚPER", section_select(MealFormState.ing_cat, MealFormState.set_ing_cat), "160px"),
            field("SUPERMERCADO", shop_select(MealFormState.ing_shop, MealFormState.set_ing_shop), "170px"),
            wrap="wrap",
            gap="12px",
            width="100%",
            align="start",
        ),

        #Nota y básico comparten fila: son los dos campos opcionales y así el
        #formulario cabe de una vez en la pantalla en vez de pedir scroll
        rx.flex(
            field(
                "NOTA (OPCIONAL)",
                note_input(MealFormState.ing_note, MealFormState.set_ing_note),
                "200px",
            ),
            field(
                "BÁSICO DE DESPENSA",
                staple_switch(MealFormState.ing_staple, MealFormState.set_ing_staple),
                "190px",
            ),
            wrap="wrap",
            gap="12px",
            width="100%",
            align="start",
        ),

        rx.flex(
            rx.text(
                "Al elegir el producto se traen su unidad, sección y súper; cámbialos aquí "
                "solo para esta receta.",
                size="1",
                color=theme.DIM,
                flex="1 1 200px",
                min_width="180px",
            ),
            rx.hstack(
                rx.button(
                    "Cancelar",
                    on_click=MealFormState.cancel_ingredient_edit,
                    variant="soft",
                    color_scheme="gray",
                    size="2",
                    type="button",
                    cursor="pointer",
                ),
                rx.button(
                    rx.icon(
                        rx.cond(MealFormState.is_editing_ingredient, "check", "plus"),
                        size=15,
                    ),
                    rx.text(
                        rx.cond(MealFormState.is_editing_ingredient, "Guardar cambios", "Añadir"),
                        size="2",
                    ),
                    on_click=MealFormState.save_ingredient,
                    color_scheme=rx.cond(MealFormState.is_editing_ingredient, "blue", "green"),
                    size="2",
                    type="button",
                    cursor="pointer",
                ),
                spacing="2",
                align="center",
                justify="end",
                flex="1 1 auto",
                wrap="wrap",
            ),
            wrap="wrap",
            gap="12px",
            width="100%",
            align="end",
        ),

        width="100%",
        spacing="2",
        align="start",
        padding="12px",
        border_radius=theme.RADIUS_SM,
        background=rx.cond(
            MealFormState.is_editing_ingredient,
            theme.alpha(theme.ACCENT, 0.07),
            theme.BG_SUNKEN,
        ),
        border=rx.cond(
            MealFormState.is_editing_ingredient,
            f"1px solid {theme.alpha(theme.ACCENT, 0.35)}",
            f"1px solid {theme.BORDER}",
        ),
    )


def _ingredients_section() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            _label("INGREDIENTES"),
            rx.cond(
                MealFormState.has_ingredients,
                pill(MealFormState.ingredient_count.to_string(), theme.MEAL, "carrot"),
            ),
            rx.spacer(),
            width="100%",
            align="center",
            spacing="2",
        ),
        rx.text(
            "Cantidades para 2 personas. El menú semanal las multiplica según los comensales.",
            size="1",
            color=theme.DIM,
        ),
        #Plegado se ve solo el botón; desplegado, el formulario entero
        rx.cond(
            MealFormState.show_ing_form,
            _ingredient_form(),
            _add_ingredient_button(),
        ),
        rx.cond(
            MealFormState.has_ingredients,
            rx.vstack(
                rx.foreach(MealFormState.ingredients, _ingredient_row),
                width="100%",
                max_width="100%",
                spacing="1",
                #Con el formulario plegado cabe más lista a la vista
                max_height=rx.cond(MealFormState.show_ing_form, "200px", "320px"),
                overflow_y="auto",
                overflow_x="hidden",
            ),
            rx.box(
                rx.text(
                    "Sin ingredientes: esta comida no aportará nada a la lista de la compra.",
                    size="1",
                    color=theme.WARNING,
                ),
                padding="10px",
                border_radius=theme.RADIUS_SM,
                background=theme.alpha(theme.WARNING, 0.08),
                border=f"1px solid {theme.alpha(theme.WARNING, 0.2)}",
                width="100%",
            ),
        ),
        width="100%",
        spacing="2",
        align="start",
    )


def meal_form_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("chef-hat", theme.MEAL, size=20, box="44px"),
                    rx.vstack(
                        rx.dialog.title(
                            MealFormState.dialog_title, margin="0", size="4", weight="bold",
                        ),
                        rx.text(
                            "Los ingredientes alimentan la lista de la compra",
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
                        on_click=MealFormState.close,
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),

                rx.vstack(
                    _label("NOMBRE"),
                    rx.input(
                        placeholder="Ej: Arroz con pollo",
                        value=MealFormState.name,
                        on_change=MealFormState.set_name,
                        size="2",
                        width="100%",
                        max_length=40,
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),

                rx.hstack(
                    rx.vstack(
                        _label("CATEGORÍA"),
                        _category_select(),
                        spacing="1",
                        width="100%",
                        align="start",
                    ),
                    rx.vstack(
                        _label("MINUTOS"),
                        rx.input(
                            value=MealFormState.prep_minutes,
                            on_change=MealFormState.set_prep_minutes,
                            type="number",
                            size="2",
                            width="100%",
                        ),
                        spacing="1",
                        width="110px",
                        align="start",
                    ),
                    width="100%",
                    spacing="3",
                    align="end",
                ),

                rx.vstack(
                    _label("CÓMO SE HACE"),
                    rx.text_area(
                        placeholder="En dos líneas: lo justo para acordarte.",
                        value=MealFormState.description,
                        on_change=MealFormState.set_description,
                        width="100%",
                        min_height="70px",
                        max_length=300,
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),

                rx.box(height="1px", width="100%", background=theme.BORDER),
                _ingredients_section(),

                rx.hstack(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        type="button",
                        size="2",
                        on_click=MealFormState.close,
                    ),
                    rx.button(
                        rx.icon("check", size=15),
                        rx.text("Guardar", size="2"),
                        color_scheme="green",
                        size="2",
                        type="button",
                        loading=MealFormState.saving,
                        on_click=MealFormState.save,
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                    padding_top="2",
                ),
                spacing="3",
                width="100%",
            ),
            style={
                "max_width": "520px",
                "max_height": "88vh",
                "overflow_y": "auto",
                #Nada debe desbordar a lo ancho: el diálogo solo hace scroll vertical
                "overflow_x": "hidden",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=MealFormState.show,
    )
