# Calendario/utils/send_not.py

import json
from pywebpush import webpush, WebPushException

VAPID_PUBLIC_KEY = "BPT7Iv41LckseHHQ4yxZ27SHlCaiDmAPCJzYmNixYWEcYPK6RkMGKXnNXG4sPls8xCkKVAxLR7olUcTvAf616_Y"
VAPID_PRIVATE_KEY = "dwZ64s6Lcipb6ob0IdvfY9NesoT09_3Vk64Ix63EW_w"

# Suscripciones en memoria
SUBSCRIPTIONS = []

def add_subscription(subscription_info: dict):
    """Añadir nueva suscripción"""
    SUBSCRIPTIONS.append(subscription_info)
    print("Suscripción añadida:", subscription_info.get('endpoint'))

def send_notification(message: str):
    """Enviar notificación a todos los suscriptores"""
    payload = json.dumps({"title": "Notificación", "body": message})
    for sub in SUBSCRIPTIONS:
        try:
            webpush(
                subscription_info=sub,
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": "mailto:ispamer98@gmail.com"},
            )
            print(f"Notificación enviada a {sub.get('endpoint')}")
        except WebPushException as ex:
            print("Error enviando push:", ex)
