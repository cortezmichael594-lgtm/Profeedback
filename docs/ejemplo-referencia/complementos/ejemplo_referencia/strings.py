"""Todos los textos que ve la persona, en español y en un solo sitio.

Así se corrigen o traducen sin tocar la lógica. Los identificadores del código
van en inglés; lo que se lee en pantalla, aquí.
"""

from __future__ import annotations

# Menú Herramientas
MENU_OPTIONS = "Ejemplo de referencia: opciones…"
MENU_TAG_NOTES = "Ejemplo de referencia: etiquetar notas…"

# Opciones
OPTIONS_TITLE = "Ejemplo de referencia"
OPTION_SHOW_BADGE = "Mostrar la insignia durante el repaso"
OPTION_DEFAULT_TAG = "Etiqueta que se añadirá:"
OPTIONS_SAVED = "Opciones guardadas."

# Etiquetar notas
ASK_SEARCH = "¿Qué notas quiere etiquetar? Escriba una búsqueda, igual que en el navegador de tarjetas."
SEARCHING = "Buscando notas…"
NOTHING_FOUND = "No hay ninguna nota que coincida con esa búsqueda."
CONFIRM_TAG = "Se etiquetarán {count} notas con «{tag}». ¿Continuar?"
TAGGED = "Se etiquetaron {count} notas. Puede deshacerlo desde Editar → Deshacer."
NO_TAG = "La etiqueta está vacía. Escriba una en las opciones del complemento."
SEARCH_FAILED = "No se pudo hacer la búsqueda:\n{reason}"

# Insignia del repaso
BADGE_LABEL = "Ejemplo"
BADGE_TIP = "Abrir las opciones del complemento de ejemplo"

# Avisos generales
ERROR_GENERIC = "El complemento de ejemplo tuvo un problema. Anki sigue funcionando; el detalle quedó en su registro."


def format_count(number: int) -> str:
    """Escribe un número con punto de millares, como se lee en España: 1240 -> 1.240."""
    return f"{number:,}".replace(",", ".")
