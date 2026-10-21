# Calendario (CalendPy)

Reflex 0.8.28. Menus semanales, tareas y lista de la compra. Datos en **Supabase**.

Servicio `calendpy-panel` (front :3001, back :8001) → https://calendpy.noxuscmmd.uk
Repo `ispamer98/Calendario` — **PUBLICO**.

Desde el 2026-09-26 lo publica el VPS `noxus-vps` (TLS + reenvío a casa por Tailscale), no
Cloudflare. Una ruta HTTP propia nueva puede exigir tocar el router del VPS: skill
`migracion-hostinger`.

## Estructura

```
Calendario/
  Calendario.py   punto de entrada
  pages/          paginas
  components/     UI reutilizable
  state/          estado
  database/       acceso a Supabase
  model/          modelos
```

## Comandos

```bash
.venv/bin/python -m pyflakes Calendario/
journalctl -u calendpy-panel -n 50 --no-pager
sudo systemctl restart calendpy-panel        # avisa antes
```

## Reglas

- `rxconfig.py` lleva **`state_auto_setters=False` a proposito**: sin el, Reflex
  crea un evento `set_<var>` por cada var publica del estado, invocable por
  cualquier cliente. **No lo quites** y no anadas setters que no hagan falta.
- Las claves de Supabase van en `.env`, nunca en el codigo. Repo publico.
- Los cambios de esquema en Supabase no los gestiona este repo: comprueba que el
  modelo y la tabla real coinciden antes de dar algo por hecho.
- `.web/` es generado: ni leer ni editar.

Detalles de Reflex → skill `reflex`. Despliegue → skill `despliegue`.
