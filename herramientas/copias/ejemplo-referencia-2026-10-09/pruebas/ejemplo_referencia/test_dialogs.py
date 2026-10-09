"""Prueba de humo de los diálogos: se construyen sin errores y devuelven lo que se les dio.

Usa la plataforma gráfica «offscreen» de Qt, así que no abre ninguna ventana real.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import unittest  # noqa: E402

from aqt.qt import QApplication  # noqa: E402
from ejemplo_referencia import dialogs  # noqa: E402


class OptionsDialogTest(unittest.TestCase):
    app: QApplication

    @classmethod
    def setUpClass(cls) -> None:
        existing = QApplication.instance()
        cls.app = existing if isinstance(existing, QApplication) else QApplication([])

    def test_values_round_trip(self) -> None:
        dialog = dialogs.OptionsDialog(None, {"show_badge": False, "default_tag": "mi_etiqueta"})
        self.assertEqual(dialog.values(), {"show_badge": False, "default_tag": "mi_etiqueta"})

    def test_values_follow_the_controls(self) -> None:
        dialog = dialogs.OptionsDialog(None, {"show_badge": True, "default_tag": "a"})
        dialog.show_badge.setChecked(False)
        dialog.default_tag.setText("  b  ")
        self.assertEqual(dialog.values(), {"show_badge": False, "default_tag": "b"})


if __name__ == "__main__":
    unittest.main()
