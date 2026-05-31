import reflex as rx

config = rx.Config(
    app_name="Calendario",
    api_url="https://calendpy.noxuscmmd.uk",
    deploy_url="https://calendpy.noxuscmmd.uk",
    # Añade esto si no está, para forzar el puerto de escucha
    backend_port=8001, 
    frontend_port=3001,
    admin_dash=False,  # Opcional: quita el panel de admin si no lo usas
    overlay_component=None,  # <--- ESTA ES LA CLAVE para quitar el logo
    app_styles={
        ".reflex-overlay": rx.Style(display="none"),
    },
    show_built_with_reflex=False,
    show_reflex_badge=False,
    telemetry_enabled=False,
)
