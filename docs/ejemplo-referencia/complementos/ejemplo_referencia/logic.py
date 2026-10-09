"""Lógica que lee y escribe en la colección.

Este módulo importa solo `anki` (nunca `aqt`) y recibe la colección como parámetro:
así se puede probar con una colección temporal, sin abrir Anki y sin tocar jamás la
colección real de la persona.
"""

from __future__ import annotations

from collections.abc import Sequence

from anki.collection import Collection, OpChangesWithCount
from anki.notes import NoteId


def clean_tag(raw: str) -> str | None:
    """Devuelve la etiqueta lista para usar, o None si no queda nada.

    Las etiquetas de Anki no admiten espacios (separan etiquetas distintas), así que
    se sustituyen por guiones bajos. Es validación en la frontera: lo que escribe la
    persona no entra sin revisar.
    """
    tag = "_".join(raw.split())
    return tag or None


def find_notes(col: Collection, search: str) -> Sequence[NoteId]:
    """Busca con una sola consulta del motor, tenga la colección diez notas o cien mil."""
    return col.find_notes(search)


def add_tag(col: Collection, note_ids: Sequence[NoteId], tag: str) -> OpChangesWithCount:
    """Añade la etiqueta a todas las notas de una vez (una sola operación deshacible)."""
    return col.tags.bulk_add(note_ids, tag)
