# Calendario/utils/reminders.py
"""
El aviso de "toca comer": recordar descontar de la despensa.

Sin esto, la despensa se vacía solo si te acuerdas de entrar a vaciarla, que es
como decir que no se vacía. El servidor mira el reloj una vez por minuto y, a la
hora que cada uno haya puesto (15:00 la comida y 23:00 la cena, por defecto),
manda el aviso con lo que toca ese día.

Tres reglas que evitan que esto se vuelva ruido:

- **Solo si hay algo puesto.** Si ese día no tiene comida planificada, no se
  manda nada: un aviso vacío enseña a ignorar los avisos.
- **Solo si no está ya descontado.** Quien lo restó por la mañana desde el
  calendario no tiene por qué recibir el recordatorio a las tres.
- **Una sola vez.** El envío se reserva antes en `meal_reminders` (índice único
  por usuario, día y comida), así que aunque el servidor corra con varios
  procesos o se reinicie a esa hora, el aviso sale una vez y no tres.

El bucle se registra como tarea de ciclo de vida de la app (`Calendario.py`), así
que vive mientras viva el servidor y no depende de que nadie tenga la web
abierta.
"""

import asyncio
import logging
from datetime import datetime

import pytz

logger = logging.getLogger(__name__)

#Cada cuánto se mira el reloj. Un minuto es lo justo para no perder la hora
#exacta sin castigar la base de datos.
TICK_SECONDS = 60

ZONA = pytz.timezone("Europe/Madrid")


def _mensaje(slot: str, comida: str, calendario: str) -> tuple[str, str]:
    if slot == "meal":
        titulo = "🍽️ Hora de comer"
        cuerpo = f"Hoy toca {comida}. ¿Descontamos sus ingredientes de la despensa?"
    else:
        titulo = "🌙 Hora de cenar"
        cuerpo = f"Esta noche toca {comida}. ¿Descontamos sus ingredientes de la despensa?"
    if calendario:
        cuerpo += f"\n↳ {calendario}"
    return titulo, cuerpo


def _enviar_recordatorios(ahora: datetime) -> int:
    """Manda los avisos que tocan en este minuto. Devuelve cuántos salieron.

    Es código síncrono a propósito (`webpush` lo es, y la base de datos también
    por REST): quien lo llama lo hace en un hilo aparte.
    """
    #Import perezoso: este módulo lo carga la app al arrancar y no debe arrastrar
    #medio proyecto antes de tiempo
    from Calendario.state.notification_state import NotificationState
    from Calendario.utils.api import SUPABASE_API

    hora_actual = ahora.strftime("%H:%M")
    enviados = 0

    for usuario in SUPABASE_API.get_users_wanting_meal_reminders():
        slots = []
        if usuario["meal_notify_time"] == hora_actual:
            slots.append("meal")
        if usuario["dinner_notify_time"] == hora_actual:
            slots.append("dinner")
        if not slots:
            continue

        try:
            dias = SUPABASE_API.get_todays_meals_for_user(usuario["id"], ahora)
        except Exception as e:
            logger.warning(f"No se pudieron leer las comidas de hoy de {usuario['username']}: {e}")
            continue

        for dia in dias:
            for slot in slots:
                comida = dia["meal"] if slot == "meal" else dia["dinner"]
                #Sin plato puesto no hay nada que recordar
                if not comida:
                    continue
                #Ya descontado: el recordatorio sobra
                if dia["meal_consumed" if slot == "meal" else "dinner_consumed"]:
                    continue
                #Reserva del envío: si otro proceso llegó antes, aquí se corta
                if not SUPABASE_API.claim_meal_reminder(usuario["id"], dia["day_id"], slot):
                    continue

                calendario = ""
                try:
                    info = SUPABASE_API.supabase.from_("calendars").select("name").eq(
                        "id", dia["calendar_id"]
                    ).execute()
                    calendario = (info.data or [{}])[0].get("name", "")
                except Exception:
                    pass

                titulo, cuerpo = _mensaje(slot, comida, calendario)
                NotificationState.enviar_aviso_despensa(
                    titulo=titulo,
                    mensaje=cuerpo,
                    destino=usuario["username"],
                    #Al tocar el aviso se abre directamente lo que hay que restar
                    url=f"/despensa?dia={dia['day_id']}&slot={slot}",
                    tag=f"comida-{dia['day_id']}-{slot}",
                )
                enviados += 1
    return enviados


async def meal_reminder_loop():
    """Bucle de avisos. Se registra como tarea de ciclo de vida de la app."""
    logger.info("⏰ Recordatorios de despensa en marcha (comida y cena)")
    ultimo_minuto = ""
    while True:
        try:
            ahora = datetime.now(ZONA)
            minuto = ahora.strftime("%H:%M")
            #Un minuto se procesa una sola vez aunque el bucle despierte dos
            #veces dentro de él
            if minuto != ultimo_minuto:
                ultimo_minuto = minuto
                enviados = await asyncio.to_thread(_enviar_recordatorios, ahora)
                if enviados:
                    logger.info(f"⏰ {enviados} recordatorios de despensa enviados a las {minuto}")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            #Un fallo puntual (base de datos caída) no puede llevarse el bucle
            logger.warning(f"Fallo en el bucle de recordatorios: {e}")
        await asyncio.sleep(TICK_SECONDS)
