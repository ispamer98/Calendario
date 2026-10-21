---
tipo: decision
fecha: 2026-08-16
proyecto: Calendario
estado: aceptada
---

# Desactivar los setters automáticos de Reflex

## Contexto

Reflex genera, por cada variable pública de una clase de estado, un evento
llamado `set_<nombre>`. Ese evento queda expuesto en el websocket y **puede
invocarlo cualquier cliente conectado**, no solo los componentes que tú has
escrito.

En una aplicación con sesiones de usuario eso es un problema directo: variables
como el usuario actual o el calendario seleccionado pasan a ser escribibles desde
la consola del navegador. Y CalendPy es una aplicación pública en internet.

En Reflex 0.8.28 el valor por defecto de `state_auto_setters` es `None`, que la
librería interpreta como **activado**, avisando de que en una versión futura
pasará a estar desactivado.

## Decisión

Poner `state_auto_setters=False` explícitamente en `rxconfig.py`. Solo existen
los setters que se definen a mano.

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| Dejar el valor por defecto | Expone un setter por cada var pública, incluida la identidad del usuario |
| Renombrar las vars sensibles con `_` | Funciona, pero hay que acertar una por una y para siempre; un descuido reabre el agujero |
| Esperar a que Reflex cambie el valor por defecto | Deja la aplicación expuesta mientras tanto |

## Consecuencias

- Cuando un componente necesite escribir en el estado hay que **definir el evento
  a mano**. Ya no aparece solo.
- Si alguna vez algo deja de responder al escribir en un campo, la primera
  sospecha es que falta ese evento explícito, no que Reflex se haya roto.
- La decisión está anotada en `rxconfig.py` junto a la línea, para que nadie la
  quite pensando que sobra.

## Cómo revertirla

Borrar la línea de `rxconfig.py`. **No se recomienda**: ver arriba.

Ver también [[setters-automaticos-siguen-activos]] — el mismo asunto en
noxuscmmd, donde la decisión aún no se ha tomado.
