"""
Migración única: importa suscriptores.json a la tabla push_subscriptions.

Uso (una sola vez, después de ejecutar 001_push_subscriptions.sql en Supabase):

    python -m Calendario.database.migrations.migrate_suscriptores_json

Requiere red hacia Supabase y las variables de entorno del .env cargadas.
Busca cada "nombre_usuario" del json contra la tabla user (case-insensitive).
Los que no encuentren coincidencia se listan al final para revisarlos a mano.
"""

import json
import os

from Calendario.database.database import SupabaseAPI

ARCHIVO = "suscriptores.json"


def main():
    if not os.path.exists(ARCHIVO):
        print(f"No existe {ARCHIVO}, nada que migrar.")
        return

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        subs = json.load(f)

    db = SupabaseAPI()
    migrados, sin_usuario = 0, []

    for sub in subs:
        username = (sub.get("nombre_usuario") or "").strip()
        user = db.get_user_by_username(username) if username else None
        if not user:
            sin_usuario.append(sub)
            continue

        keys = sub.get("keys", {})
        ok = db.upsert_push_subscription(
            user_id=user["id"],
            endpoint=sub.get("endpoint", ""),
            p256dh=keys.get("p256dh", ""),
            auth=keys.get("auth", ""),
            alias=sub.get("alias", "Dispositivo"),
        )
        if ok:
            migrados += 1
        else:
            sin_usuario.append(sub)

    print(f"Migrados: {migrados}/{len(subs)}")
    if sin_usuario:
        print("No se pudieron migrar (revisar usuario o error de red):")
        for s in sin_usuario:
            print(f"  - alias={s.get('alias')!r} nombre_usuario={s.get('nombre_usuario')!r}")


if __name__ == "__main__":
    main()
