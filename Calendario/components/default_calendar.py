import reflex as rx
from datetime import datetime
import calendar

def default_calendar() -> rx.Component:
    # Obtener fecha actual
    current_date = datetime.now()
    current_day = current_date.day
    
    # Obtener el calendario del mes actual
    cal = calendar.monthcalendar(current_date.year, current_date.month)
    
    def render_day(day):
        return rx.table.cell(
            rx.cond(
                (day == 0),
                "",
                str(day)
            ),
            background_color=rx.cond(
                (day == current_day),
                "rgba(79, 70, 229, 0.1)",
                "transparent"
            ),
            border_radius=rx.cond(
                (day == current_day),
                "8px",
                "0px"
            ),
            font_weight=rx.cond(
                (day == current_day),
                "bold",
                "normal"
            )
        )

    def render_week(week):
        return rx.table.row(
            rx.foreach(
                week,
                render_day
            )
        )

    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Lun"),
                rx.table.column_header_cell("Mar"),
                rx.table.column_header_cell("Mié"),
                rx.table.column_header_cell("Jue"),
                rx.table.column_header_cell("Vie"),
                rx.table.column_header_cell("Sáb"),
                rx.table.column_header_cell("Dom"),
            )
        ),
        rx.table.body(
            rx.foreach(
                cal,
                render_week
            )
        ),
        width="100%",
        text_align="center",
        border="1px solid #eee",
        border_radius="8px",
        padding="1em"
    )