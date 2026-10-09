"""Protección de errores.

Un error sin capturar le planta a la persona un volcado técnico y puede dejar el
complemento inservible hasta reiniciar. Todo lo que Anki llama por nuestra cuenta
(menús, botones, hooks) va envuelto con uno de estos dos decoradores: el detalle
técnico va al registro del complemento y la persona ve, como mucho, un aviso breve.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar, cast

from aqt import mw
from aqt.addons import AddonManager
from aqt.utils import tooltip

from . import strings

F = TypeVar("F", bound=Callable[..., Any])

# Un solo aviso por función y sesión: si el fallo se repite en cada tarjeta,
# no se debe llenar la pantalla de avisos.
_already_warned: set[str] = set()


def _report(name: str) -> None:
    AddonManager.get_logger(__name__).exception("Fallo en %s", name)
    if mw is None or name in _already_warned:
        return
    _already_warned.add(name)
    tooltip(strings.ERROR_GENERIC, period=5000)


def guarded(func: F) -> F:
    """Para funciones de menús, botones y hooks que no devuelven nada."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception:
            _report(func.__name__)
            return None

    return cast(F, wrapper)


def guarded_filter(func: F) -> F:
    """Para filtros (por ejemplo card_will_show o webview_did_receive_js_message).

    Un filtro debe devolver siempre su primer argumento, modificado o no. Si fallara
    y devolviera None, se rompería el resto de la cadena de Anki; por eso, ante un
    error, se devuelve el primer argumento tal cual.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception:
            _report(func.__name__)
            return args[0] if args else None

    return cast(F, wrapper)
