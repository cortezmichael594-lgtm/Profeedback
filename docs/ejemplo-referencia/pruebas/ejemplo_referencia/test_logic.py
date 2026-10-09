"""Pruebas de la lógica con una colección TEMPORAL (nunca la de la persona).

Se ejecutan con herramientas/empaquetar.py, que añade complementos/ al PYTHONPATH.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from anki.collection import Collection
from ejemplo_referencia import logic, strings


class CleanTagTest(unittest.TestCase):
    def test_spaces_become_underscores(self) -> None:
        self.assertEqual(logic.clean_tag("  mi etiqueta  "), "mi_etiqueta")

    def test_empty_is_none(self) -> None:
        self.assertIsNone(logic.clean_tag("   "))


class FormatCountTest(unittest.TestCase):
    def test_spanish_thousands_separator(self) -> None:
        self.assertEqual(strings.format_count(1240), "1.240")
        self.assertEqual(strings.format_count(7), "7")
        self.assertEqual(strings.format_count(1234567), "1.234.567")


class CollectionLogicTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.col = Collection(str(Path(self._tmp.name) / "prueba.anki2"))

    def tearDown(self) -> None:
        self.col.close()
        self._tmp.cleanup()

    def _add_note(self, front: str) -> None:
        notetype = self.col.models.by_name("Basic")
        assert notetype is not None  # en una prueba, assert es lo adecuado
        note = self.col.new_note(notetype)
        note["Front"] = front
        note["Back"] = "respuesta"
        self.col.add_note(note, self.col.decks.id("Default"))

    def test_search_without_results(self) -> None:
        self.assertEqual(list(logic.find_notes(self.col, "gato")), [])

    def test_tag_added_only_to_found_notes(self) -> None:
        self._add_note("gato")
        self._add_note("perro")
        ids = logic.find_notes(self.col, "gato")
        self.assertEqual(len(ids), 1)

        changes = logic.add_tag(self.col, ids, "animales")

        self.assertEqual(changes.count, 1)
        self.assertEqual(len(self.col.find_notes("tag:animales")), 1)
        self.assertEqual(len(self.col.find_notes("perro tag:animales")), 0)

    def test_tagging_can_be_undone(self) -> None:
        self._add_note("gato")
        ids = logic.find_notes(self.col, "gato")
        logic.add_tag(self.col, ids, "animales")
        self.col.undo()
        self.assertEqual(len(self.col.find_notes("tag:animales")), 0)


if __name__ == "__main__":
    unittest.main()
