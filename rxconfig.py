import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin  # ← IMPORTAR el plugin correctamente

config = rx.Config(
    app_name="Calendario",
    show_built_with_reflex=False,
    plugins=[SitemapPlugin()]  # ← Pasar una instancia del plugin
)
