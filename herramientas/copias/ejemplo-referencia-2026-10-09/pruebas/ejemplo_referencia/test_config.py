"""Pruebas de la capa de configuración (sin Anki en marcha)."""

from __future__ import annotations

import unittest

from ejemplo_referencia import config

DEFAULTS = {"show_badge": True, "default_tag": "ejemplo"}


class MergeWithDefaultsTest(unittest.TestCase):
    def test_first_run_without_stored_config(self) -> None:
        self.assertEqual(config.merge_with_defaults(None, DEFAULTS), DEFAULTS)

    def test_option_missing_in_older_version_gets_default(self) -> None:
        merged = config.merge_with_defaults({"show_badge": False}, DEFAULTS)
        self.assertEqual(merged, {"show_badge": False, "default_tag": "ejemplo"})

    def test_wrong_type_falls_back_to_default(self) -> None:
        merged = config.merge_with_defaults({"show_badge": "sí", "default_tag": 5}, DEFAULTS)
        self.assertEqual(merged, DEFAULTS)

    def test_unknown_keys_are_dropped(self) -> None:
        merged = config.merge_with_defaults({"otra": 1}, DEFAULTS)
        self.assertEqual(merged, DEFAULTS)

    def test_defaults_are_not_mutated(self) -> None:
        defaults = dict(DEFAULTS)
        config.merge_with_defaults({"show_badge": False}, defaults)
        self.assertEqual(defaults, DEFAULTS)

    def test_shipped_defaults_match_config_json(self) -> None:
        import json
        from pathlib import Path

        shipped = json.loads((Path(config.__file__).parent / "config.json").read_text("utf-8"))
        self.assertEqual(shipped, config.DEFAULTS)


if __name__ == "__main__":
    unittest.main()
