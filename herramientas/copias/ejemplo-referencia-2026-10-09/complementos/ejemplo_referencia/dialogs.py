"""Diálogos Qt.

Se construyen solo con controles estándar de Qt (casillas, campos, botones
Aceptar/Cancelar). Así toman solos el aspecto y los colores del tema activo,
también los de Nocturne, y no hay que fijar ningún color a mano.
"""

from __future__ import annotations

from typing import Any

from aqt import mw
from aqt.qt import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QWidget,
    qconnect,
)
from aqt.utils import disable_help_button, restoreGeom, saveGeom

from . import strings

_GEOMETRY_KEY = "ejemplo_referencia_options"


def _can_remember_geometry() -> bool:
    # Fuera de Anki (pruebas) no hay perfil abierto; dentro de Anki siempre lo hay.
    return mw is not None and mw.pm.profile is not None


class OptionsDialog(QDialog):
    def __init__(self, parent: QWidget | None, values: dict[str, Any]) -> None:
        super().__init__(parent)
        disable_help_button(self)
        self.setWindowTitle(strings.OPTIONS_TITLE)

        self.show_badge = QCheckBox(strings.OPTION_SHOW_BADGE, self)
        self.show_badge.setChecked(bool(values["show_badge"]))
        self.default_tag = QLineEdit(str(values["default_tag"]), self)

        form = QFormLayout(self)
        form.addRow(self.show_badge)
        form.addRow(strings.OPTION_DEFAULT_TAG, self.default_tag)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        qconnect(buttons.accepted, self.accept)
        qconnect(buttons.rejected, self.reject)
        form.addRow(buttons)

        if _can_remember_geometry():
            restoreGeom(self, _GEOMETRY_KEY)

    def done(self, a0: int) -> None:
        if _can_remember_geometry():
            saveGeom(self, _GEOMETRY_KEY)
        super().done(a0)

    def values(self) -> dict[str, Any]:
        return {
            "show_badge": self.show_badge.isChecked(),
            "default_tag": self.default_tag.text().strip(),
        }
