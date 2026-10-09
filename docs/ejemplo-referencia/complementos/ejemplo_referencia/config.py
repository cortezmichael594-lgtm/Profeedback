"""Única capa sobre la configuración del complemento.

El resto del código lee y guarda opciones solo a través de este módulo. Así una
opción que falte (primer arranque, o una versión anterior que no la tenía) nunca
rompe nada: se usa el valor por defecto.

Ojo: si se cambia un valor de config.json en una versión nueva, quien ya había
personalizado las opciones seguirá viendo el valor antiguo. Una opción nueva sí
llega, porque aquí se completa con los valores por defecto.
"""

from __future__ import annotations

from typing import Any

from aqt import mw

# Debe coincidir con config.json. Las claves no pueden empezar por guion bajo
# (Anki se las reserva).
DEFAULTS: dict[str, Any] = {
    "show_badge": True,
    "default_tag": "ejemplo",
}


def merge_with_defaults(stored: object, defaults: dict[str, Any]) -> dict[str, Any]:
    """Completa lo guardado con los valores por defecto.

    Se descarta cualquier valor guardado cuyo tipo no coincida con el del valor por
    defecto (por ejemplo, si alguien editó el JSON a mano) y toda clave desconocida.
    """
    merged = dict(defaults)
    if isinstance(stored, dict):
        for key, default in defaults.items():
            value = stored.get(key, default)
            if isinstance(value, type(default)):
                merged[key] = value
    return merged


def load() -> dict[str, Any]:
    stored = mw.addonManager.getConfig(__name__) if mw is not None else None
    return merge_with_defaults(stored, DEFAULTS)


def save(values: dict[str, Any]) -> None:
    if mw is None:
        return
    mw.addonManager.writeConfig(__name__, merge_with_defaults(values, DEFAULTS))
