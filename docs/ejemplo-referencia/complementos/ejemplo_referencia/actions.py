"""Lo que ocurre cuando la persona pulsa algo: pregunta, confirma, lanza la operación y avisa.

Reparto de trabajo: la interfaz Qt solo se toca desde el hilo principal; lo que
puede tardar (leer o escribir en la colección) va en segundo plano con QueryOp
(lecturas) o CollectionOp (escrituras, que entran en Editar → Deshacer).
"""

from __future__ import annotations

from collections.abc import Sequence

from anki.collection import OpChangesWithCount
from anki.notes import NoteId
from aqt import mw
from aqt.operations import CollectionOp, QueryOp
from aqt.utils import askUser, getText, showWarning, tooltip

from . import config, dialogs, logic, strings
from .errors import guarded


@guarded
def open_options() -> None:
    """Abre las opciones del complemento.

    Se registra con setConfigAction y debe devolver None: si devolviera False, Anki
    abriría en su lugar el editor de JSON, que para esta persona también es código.
    """
    if mw is None:
        return
    dialog = dialogs.OptionsDialog(mw, config.load())
    if dialog.exec():
        config.save(dialog.values())
        tooltip(strings.OPTIONS_SAVED, parent=mw)


@guarded
def tag_notes() -> None:
    """Pregunta qué notas, cuenta cuántas son, confirma con la cifra exacta y etiqueta."""
    if mw is None:
        return
    search, accepted = getText(strings.ASK_SEARCH, parent=mw)
    if not accepted or not search.strip():
        return
    tag = logic.clean_tag(str(config.load()["default_tag"]))
    if tag is None:
        showWarning(strings.NO_TAG, parent=mw)
        return

    # Todo lo que haga falta de la interfaz se recoge ANTES de pasar al segundo plano.
    QueryOp(
        parent=mw,
        op=lambda col: logic.find_notes(col, search),
        success=lambda note_ids: _confirm_and_tag(note_ids, tag),
    ).failure(_on_search_failed).with_progress(strings.SEARCHING).run_in_background()


@guarded
def _on_search_failed(error: Exception) -> None:
    showWarning(strings.SEARCH_FAILED.format(reason=str(error)), parent=mw)


@guarded
def _confirm_and_tag(note_ids: Sequence[NoteId], tag: str) -> None:
    if mw is None:
        return
    if not note_ids:
        tooltip(strings.NOTHING_FOUND, parent=mw)
        return
    question = strings.CONFIRM_TAG.format(count=strings.format_count(len(note_ids)), tag=tag)
    # defaultno=True: ante una operación masiva, un Intro de más no debe confirmarla.
    if not askUser(question, parent=mw, defaultno=True):
        return
    CollectionOp(
        parent=mw, op=lambda col: logic.add_tag(col, note_ids, tag)
    ).success(_on_tagged).run_in_background()


@guarded
def _on_tagged(changes: OpChangesWithCount) -> None:
    tooltip(strings.TAGGED.format(count=strings.format_count(changes.count)), parent=mw)
