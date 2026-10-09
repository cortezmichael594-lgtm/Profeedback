#!/usr/bin/env python3
"""Comprueba y empaqueta un complemento de Anki. Solo usa la biblioteca estándar.

Uso, desde la carpeta del proyecto y con el intérprete del .venv:

    python herramientas/empaquetar.py [complemento] [opciones]

    complemento           carpeta dentro de complementos/ (opcional si solo hay una)
    --solo-comprobar      comprueba, pero no genera el .ankiaddon
    --sin-mypy            omite la comprobación de nombres y firmas con mypy
    --sin-importar        omite la importación de prueba fuera de Anki
    --sin-pruebas         omite las pruebas de pruebas/<complemento>/
    --olvidar-fix FIX-003 da por retirada, a propósito, una nota de corrección
    --autoprueba          comprueba que esta herramienta y el entorno funcionan

Qué comprueba, por este orden:
  1. manifest.json y config.json válidos.
  2. Cada .py compila; sin PyQt directo, sin colores fijos, sin errores típicos.
  3. Los archivos web (css/js/html): sin colores fijos ni recursos de internet.
  4. Las notas de corrección (FIX-NNN): índice y bloques coherentes, y ninguna
     perdida respecto a la última entrega (se guardan en herramientas/registro-fix/).
  5. mypy contra la versión de Anki instalada en el .venv: detecta hooks, funciones
     y métodos inventados y firmas incorrectas.
  6. Importación del paquete fuera de Anki y pruebas de pruebas/<complemento>/.
  7. Construcción del .ankiaddon en paquetes/ y verificación del zip resultante.

Códigos de salida: 0 correcto (puede haber avisos), 1 hay errores, 2 uso incorrecto.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

PACKAGE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
MANIFEST_KEYS = {
    "package": str,
    "name": str,
    "mod": (int, float),
    "conflicts": list,
    "min_point_version": (int, float),
    "max_point_version": (int, float),
    "branch_index": (int, float),
    "human_version": str,
    "homepage": str,
}
EXCLUDED_DIRS = {"__pycache__", ".git", ".mypy_cache", ".pytest_cache"}
EXCLUDED_NAMES = {"meta.json", ".DS_Store", "Thumbs.db"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".ankiaddon", ".tmp"}
USER_FILES_ALLOWED = {"README.txt", "LEEME.txt"}
TEXT_SUFFIXES = {".py", ".js", ".css", ".html", ".htm"}
WEB_SUFFIXES = {".js", ".css", ".html", ".htm"}
FORBIDDEN_QT = {"PyQt6", "PyQt5", "PySide6", "PySide2"}
# Marca que permite un color fijo en una línea concreta (por ejemplo, un valor de reserva).
COLOR_OK_MARK = "colores-ok"
COLOR_HINT = f" Si es un valor de reserva legítimo, añada «{COLOR_OK_MARK}: motivo» en esa línea."

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
COLOR_FUNC_RE = re.compile(r"\b(?:rgba?|hsla?|hwb|oklch|oklab|lab|lch)\(", re.IGNORECASE)
COLOR_WORD_RE = re.compile(r"color|background|border|fill|stroke|shadow", re.IGNORECASE)
VAR_RE = re.compile(r"var\((?:[^()]|\([^()]*\))*\)")
URL_RE = re.compile(r"url\([^)]*\)")

FIX_ID = r"FIX-\d{3}"
COMMENT_START = r"^\s*(?:#|//|/\*+|\*)\s*"
FIX_BLOCK_RE = re.compile(COMMENT_START + r"---\s*(" + FIX_ID + r")\b")
FIX_INDEX_RE = re.compile(COMMENT_START + r"(" + FIX_ID + r")\s*\(")


# ---------------------------------------------------------------------------
# Estructuras
# ---------------------------------------------------------------------------


@dataclass
class Project:
    root: Path

    @property
    def addons(self) -> Path:
        return self.root / "complementos"

    @property
    def tests(self) -> Path:
        return self.root / "pruebas"

    @property
    def packages(self) -> Path:
        return self.root / "paquetes"

    @property
    def fix_registry(self) -> Path:
        return self.root / "herramientas" / "registro-fix"

    @property
    def anki_version_file(self) -> Path:
        return self.root / "herramientas" / "version-anki.txt"


@dataclass
class Options:
    only_check: bool = False
    skip_mypy: bool = False
    skip_import: bool = False
    skip_tests: bool = False
    forget_fix: list[str] = field(default_factory=list)


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    done: list[str] = field(default_factory=list)

    def error(self, text: str) -> None:
        self.errors.append(text)

    def warn(self, text: str) -> None:
        self.warnings.append(text)

    def ok(self, text: str) -> None:
        self.done.append(text)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def child_env(project: Project) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(project.addons)] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])
    )
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run(cmd: list[str], project: Project, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=child_env(project),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=900,
    )


def tail(text: str, lines: int = 15) -> str:
    """Últimas líneas útiles de una salida (sin el ruido interno de importlib)."""
    chunk = [
        line
        for line in text.strip().splitlines()
        if line.strip() and "<frozen importlib" not in line and not re.fullmatch(r"\s*[~^]+\s*", line)
    ]
    return "\n    ".join(chunk[-lines:])


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.strip().split(".") if part.isdigit())


# ---------------------------------------------------------------------------
# Selección de archivos
# ---------------------------------------------------------------------------


def pick_addon(project: Project, name: str | None, report: Report) -> Path | None:
    if name:
        direct = Path(name)
        for candidate in (direct, project.addons / name):
            if candidate.is_dir():
                return candidate.resolve()
        report.error(f"No existe la carpeta del complemento «{name}» (se busca en complementos/).")
        return None
    candidates = []
    if project.addons.is_dir():
        candidates = sorted(
            p
            for p in project.addons.iterdir()
            if p.is_dir()
            and not p.name.startswith(".")
            and ((p / "__init__.py").exists() or (p / "manifest.json").exists())
        )
    if len(candidates) == 1:
        return candidates[0].resolve()
    if not candidates:
        report.error("No hay ningún complemento en complementos/.")
    else:
        names = ", ".join(p.name for p in candidates)
        report.error(f"Hay varios complementos ({names}): indique cuál empaquetar.")
    return None


def package_files(folder: Path, report: Report) -> list[Path]:
    """Archivos que viajan en el paquete, en orden estable."""
    included: list[Path] = []
    skipped_user_files = False
    for path in sorted(folder.rglob("*"), key=lambda p: p.relative_to(folder).as_posix()):
        if path.is_dir():
            continue
        relative = path.relative_to(folder)
        parts = relative.parts
        if any(part in EXCLUDED_DIRS for part in parts[:-1]):
            continue
        if path.name in EXCLUDED_NAMES or path.suffix in EXCLUDED_SUFFIXES:
            continue
        if parts[0] == "user_files" and path.name not in USER_FILES_ALLOWED:
            skipped_user_files = True
            continue
        included.append(path)
    if skipped_user_files:
        report.warn(
            "user_files/ contiene archivos de prueba que NO se incluyen en el paquete "
            "(solo viaja un README.txt o LEEME.txt)."
        )
    return included


# ---------------------------------------------------------------------------
# 1. manifest.json y config.json
# ---------------------------------------------------------------------------


def check_manifest(folder: Path, report: Report) -> dict[str, object] | None:
    path = folder / "manifest.json"
    if not path.exists():
        report.error("Falta manifest.json (debe declarar al menos «package» y «name»).")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        report.error(f"manifest.json no es un JSON válido: {exc}")
        return None
    if not isinstance(data, dict):
        report.error("manifest.json debe ser un objeto JSON.")
        return None
    problems = 0
    for key in ("package", "name"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            report.error(f"manifest.json: falta «{key}» o no es un texto.")
            problems += 1
    package = data.get("package")
    if isinstance(package, str) and not PACKAGE_RE.match(package):
        report.error(
            f"manifest.json: «package» ({package!r}) debe ser un nombre de módulo: "
            "minúsculas, cifras y guiones bajos, sin espacios ni guiones, y sin empezar por cifra."
        )
        problems += 1
    for key, value in data.items():
        expected = MANIFEST_KEYS.get(key)
        if expected is None:
            report.warn(f"manifest.json: clave desconocida «{key}» (Anki la ignora).")
        elif not isinstance(value, expected):
            report.error(f"manifest.json: «{key}» tiene un tipo incorrecto.")
            problems += 1
    if isinstance(package, str) and package != folder.name:
        report.warn(
            f"El «package» del manifiesto ({package}) no coincide con el nombre de la carpeta "
            f"({folder.name}). Conviene que sean iguales."
        )
    if problems:
        return None
    report.ok(f"manifest.json válido (paquete «{package}», nombre «{data['name']}»).")
    return data


def check_json_files(folder: Path, files: list[Path], report: Report) -> None:
    count = 0
    for path in files:
        if path.suffix != ".json":
            continue
        relative = path.relative_to(folder).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            report.error(f"{relative}: JSON no válido: {exc}")
            continue
        count += 1
        if relative == "config.json":
            if not isinstance(data, dict):
                report.error("config.json debe ser un objeto JSON.")
            else:
                for key in data:
                    if str(key).startswith("_"):
                        report.error(
                            f"config.json: la clave «{key}» empieza por guion bajo "
                            "(Anki se reserva esas claves)."
                        )
    if count:
        report.ok(f"{count} archivo(s) JSON válidos.")


# ---------------------------------------------------------------------------
# 2. Python
# ---------------------------------------------------------------------------


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


def strip_var_and_url(text: str) -> str:
    return VAR_RE.sub("", URL_RE.sub("", text))


def looks_like_fixed_color(text: str) -> bool:
    stripped = text.strip()
    if re.fullmatch(HEX_RE.pattern, stripped):
        return True
    if COLOR_WORD_RE.search(stripped):
        cleaned = strip_var_and_url(stripped)
        return bool(HEX_RE.search(cleaned) or COLOR_FUNC_RE.search(cleaned))
    return False


class PythonReviewer(ast.NodeVisitor):
    def __init__(self, label: str, report: Report, lines: list[str]) -> None:
        self.label = label
        self.report = report
        self.lines = lines
        self.function_depth = 0

    def color_allowed(self, node: ast.AST) -> bool:
        number = getattr(node, "lineno", 0)
        return 0 < number <= len(self.lines) and COLOR_OK_MARK in self.lines[number - 1]

    def error(self, node: ast.AST, text: str) -> None:
        self.report.error(f"{self.label}:{getattr(node, 'lineno', '?')}: {text}")

    def warn(self, node: ast.AST, text: str) -> None:
        self.report.warn(f"{self.label}:{getattr(node, 'lineno', '?')}: {text}")

    def _enter_function(self, node: ast.AST) -> None:
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    visit_FunctionDef = _enter_function
    visit_AsyncFunctionDef = _enter_function
    visit_Lambda = _enter_function

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return  # docstring o texto suelto: no es código
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name.split(".")[0] in FORBIDDEN_QT:
                self.error(node, "importe Qt desde aqt.qt, nunca directamente (use la versión que trae Anki).")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module.split(".")[0] in FORBIDDEN_QT:
            self.error(node, "importe Qt desde aqt.qt, nunca directamente (use la versión que trae Anki).")
        if module in ("aqt.colors", "_aqt.colors") and not self.color_allowed(node):
            self.error(
                node,
                "no importe los colores como nombres sueltos: lea colors.X en el momento de usarlos, "
                "porque Nocturne puede redefinirlos después de cargar este complemento." + COLOR_HINT,
            )

    def visit_Assert(self, node: ast.Assert) -> None:
        self.warn(node, "assert no se evalúa en algunas compilaciones de Anki: use if y avise a la persona.")

    def visit_Call(self, node: ast.Call) -> None:
        name = dotted_name(node.func)
        if name == "time.sleep":
            self.warn(node, "time.sleep congela Anki si corre en el hilo principal.")
        elif name.endswith(".processEvents"):
            self.warn(node, "processEvents provoca parpadeos y reentradas: use QueryOp o CollectionOp.")
        elif name.endswith(".setStyleSheet"):
            self.warn(node, "setStyleSheet: preferir controles nativos sin estilo; si es imprescindible, solo con colores del tema.")
        elif name == "print":
            self.warn(node, "print: use AddonManager.get_logger(__name__); lo que va a stderr abre un aviso de error en Anki.")
        elif name in ("sys.stderr.write", "traceback.print_exc") or name.endswith("print_exception"):
            self.warn(node, "escribir en stderr abre una ventana de error en Anki: use el registro del complemento.")
        elif re.search(r"\.db\.(execute|all|first|scalar|list)$", name):
            self.warn(node, "SQL directo contra la colección: use las funciones de la colección (no se sincroniza ni sobrevive a cambios).")
        elif name.endswith("theme_manager.var") or name.endswith("theme_manager.qcolor"):
            if self.function_depth == 0 and not self.color_allowed(node):
                self.error(
                    node,
                    "color del tema leído al cargar el módulo: léalo dentro de la función que lo pinta "
                    "(y repinte con gui_hooks.theme_did_change)." + COLOR_HINT,
                )
        elif name.split(".")[-1] == "QColor":
            first = node.args[0] if node.args else None
            if (
                len(node.args) >= 3 or (isinstance(first, ast.Constant) and isinstance(first.value, str))
            ) and not self.color_allowed(node):
                self.error(node, "QColor con valor fijo: use theme_manager.qcolor(colors.X)." + COLOR_HINT)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if (
            isinstance(node.value, str)
            and looks_like_fixed_color(node.value)
            and not self.color_allowed(node)
        ):
            self.error(
                node,
                f"color fijo ({node.value.strip()[:40]!r}): use un color del tema o var(--token, reserva)." + COLOR_HINT,
            )


def check_python(folder: Path, files: list[Path], report: Report) -> None:
    count = 0
    for path in files:
        if path.suffix != ".py":
            continue
        relative = path.relative_to(folder).as_posix()
        source = read_text(path)
        if source is None:
            report.error(f"{relative}: no se puede leer como UTF-8.")
            continue
        try:
            tree = ast.parse(source, filename=relative)
            compile(tree, relative, "exec")
        except SyntaxError as exc:
            report.error(f"{relative}:{exc.lineno}: error de sintaxis: {exc.msg}")
            continue
        count += 1
        PythonReviewer(relative, report, source.splitlines()).visit(tree)
    if count:
        report.ok(f"{count} archivo(s) .py compilan.")
    uses_get_config = any(
        "getConfig(" in (read_text(p) or "") for p in files if p.suffix == ".py"
    )
    if uses_get_config and not (folder / "config.json").exists():
        report.error("El código usa getConfig pero falta config.json: getConfig devolvería None.")


# ---------------------------------------------------------------------------
# 3. Web
# ---------------------------------------------------------------------------


def blank_block_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group().count("\n"), text, flags=re.S)


def css_declaration_lines(text: str) -> list[tuple[int, str]]:
    """Líneas (con su número) que están dentro de un bloque { ... }, sin selectores."""
    result: list[tuple[int, str]] = []
    depth = 0
    for number, line in enumerate(blank_block_comments(text).splitlines(), start=1):
        part = line
        if depth == 0 and "{" in line:
            part = line.split("{", 1)[1]
        if depth > 0 or "{" in line:
            result.append((number, part))
        depth += line.count("{") - line.count("}")
        depth = max(depth, 0)
    return result


def check_web(folder: Path, files: list[Path], report: Report) -> None:
    count = 0
    for path in files:
        if path.suffix not in WEB_SUFFIXES:
            continue
        relative = path.relative_to(folder).as_posix()
        text = read_text(path)
        if text is None:
            report.error(f"{relative}: no se puede leer como UTF-8.")
            continue
        count += 1
        flagged = 0
        original = text.splitlines()

        def flag(number: int, text_: str) -> None:
            nonlocal flagged
            if 0 < number <= len(original) and COLOR_OK_MARK in original[number - 1]:
                return
            flagged += 1
            if flagged <= 6:
                report.error(
                    f"{relative}:{number}: color fijo ({text_.strip()[:50]!r}): use var(--token, reserva) "
                    "y su pareja de modo noche." + COLOR_HINT
                )

        if path.suffix == ".css":
            for number, line in css_declaration_lines(text):
                cleaned = strip_var_and_url(line)
                if HEX_RE.search(cleaned) or COLOR_FUNC_RE.search(cleaned):
                    flag(number, line)
        elif path.suffix in (".js",):
            no_comments = re.sub(r"(?m)(^|\s)//.*$", r"\1", blank_block_comments(text))
            for number, line in enumerate(no_comments.splitlines(), start=1):
                cleaned = strip_var_and_url(line)
                if COLOR_WORD_RE.search(cleaned) and (HEX_RE.search(cleaned) or COLOR_FUNC_RE.search(cleaned)):
                    flag(number, line)
        else:  # html
            for number, line in enumerate(text.splitlines(), start=1):
                for style in re.findall(r"style\s*=\s*\"([^\"]*)\"", line):
                    cleaned = strip_var_and_url(style)
                    if HEX_RE.search(cleaned) or COLOR_FUNC_RE.search(cleaned):
                        flag(number, style)
        if flagged > 6:
            report.error(f"{relative}: y {flagged - 6} color(es) fijo(s) más.")

        body = blank_block_comments(text)
        if path.suffix == ".js":
            body = re.sub(r"(?m)(^|\s)//.*$", r"\1", body)
        for number, line in enumerate(body.splitlines(), start=1):
            for url in re.findall(r"https?://[^\s\"')]+", line):
                if "www.w3.org" in url:
                    continue
                report.warn(f"{relative}:{number}: recurso de internet ({url[:60]}): el complemento debe funcionar sin conexión, sin CDNs.")
            if path.suffix == ".js" and re.search(r"(?<![\w.])(?:window\.)?(?:alert|confirm|prompt)\s*\(", line):
                report.warn(f"{relative}:{number}: alert/confirm/prompt bloquean la ventana: use un aviso de Qt desde Python.")
    if count:
        report.ok(f"{count} archivo(s) web revisados (colores fijos y recursos externos).")


# ---------------------------------------------------------------------------
# 4. Notas de corrección (FIX)
# ---------------------------------------------------------------------------


def check_fix_notes(
    project: Project,
    folder: Path,
    package: str,
    files: list[Path],
    options: Options,
    report: Report,
) -> dict[str, list[str]] | None:
    """Devuelve {FIX-NNN: [archivos]} si todo es coherente; None si hay errores."""
    found: dict[str, list[str]] = {}
    problems = 0
    for path in files:
        if path.suffix not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(folder).as_posix()
        text = read_text(path)
        if text is None:
            continue
        lines = text.splitlines()
        blocks: set[str] = set()
        index: set[str] = set()
        for number, line in enumerate(lines):
            block = FIX_BLOCK_RE.match(line)
            if block:
                blocks.add(block.group(1))
                window = "\n".join(lines[number : number + 12])
                for label in ("Síntoma", "Causa", "Regla"):
                    if not re.search(label.replace("í", "[ií]") + r"\s*:", window):
                        report.warn(f"{relative}:{number + 1}: la nota {block.group(1)} no tiene la línea «{label}:».")
                continue
            entry = FIX_INDEX_RE.match(line)
            if entry:
                index.add(entry.group(1))
        for fix in sorted(index - blocks):
            report.error(f"{relative}: {fix} está en el índice del archivo, pero falta su bloque en el código.")
            problems += 1
        for fix in sorted(blocks - index):
            report.error(f"{relative}: {fix} tiene bloque, pero falta su línea en el índice «Historial de correcciones».")
            problems += 1
        for fix in blocks:
            found.setdefault(fix, []).append(relative)

    registry_path = project.fix_registry / f"{package}.json"
    previous: dict[str, list[str]] = {}
    if registry_path.exists():
        try:
            previous = json.loads(registry_path.read_text(encoding="utf-8")).get("fix", {})
        except (OSError, ValueError):
            report.warn(f"No se pudo leer {registry_path.name}; se creará de nuevo.")
    forgotten = {fix.upper() for fix in options.forget_fix}
    lost = sorted(set(previous) - set(found) - forgotten)
    for fix in lost:
        where = ", ".join(previous[fix]) or "archivo desconocido"
        report.error(
            f"Se ha perdido la nota {fix} (estaba en {where}). Vuelva a ponerla en su sitio; "
            f"si la retiró a propósito, repita con --olvidar-fix {fix}."
        )
        problems += 1

    numbers = sorted(int(fix.split("-")[1]) for fix in found)
    if numbers:
        gaps = sorted(set(range(1, numbers[-1] + 1)) - set(numbers))
        if gaps:
            report.warn("La numeración de FIX tiene huecos: " + ", ".join(f"FIX-{n:03d}" for n in gaps) + ".")
    if problems:
        return None
    if found:
        report.ok(f"Notas de corrección coherentes y conservadas: {len(found)}.")
    return found


def save_fix_registry(project: Project, package: str, found: dict[str, list[str]], options: Options) -> None:
    if not found and not options.forget_fix:
        return
    project.fix_registry.mkdir(parents=True, exist_ok=True)
    path = project.fix_registry / f"{package}.json"
    previous: dict[str, list[str]] = {}
    if path.exists():
        try:
            previous = json.loads(path.read_text(encoding="utf-8")).get("fix", {})
        except (OSError, ValueError):
            previous = {}
    forgotten = {fix.upper() for fix in options.forget_fix}
    merged = {fix: files for fix, files in previous.items() if fix not in forgotten}
    merged.update(found)
    ordered = {fix: sorted(merged[fix]) for fix in sorted(merged)}
    path.write_text(
        json.dumps({"complemento": package, "fix": ordered}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# 5. Entorno, mypy, importación y pruebas
# ---------------------------------------------------------------------------


def check_environment(project: Project, report: Report) -> bool:
    if sys.prefix == sys.base_prefix:
        report.warn("Esta herramienta no se está ejecutando con el intérprete del .venv.")
    result = run(
        [sys.executable, "-c", "from anki.buildinfo import version; print(version)"],
        project,
        project.root,
    )
    if result.returncode != 0:
        report.error(
            "El entorno no está preparado: no se puede importar anki/aqt. "
            "Ejecute primero la preparación del entorno (.venv con aqt instalado)."
        )
        return False
    real = result.stdout.strip()
    expected_text = read_text(project.anki_version_file)
    if expected_text and version_tuple(real) != version_tuple(expected_text):
        report.warn(
            f"El .venv tiene Anki {real}, pero el cliente usa {expected_text.strip()}. "
            "Reinstale aqt con la versión del cliente."
        )
    else:
        report.ok(f"Entorno con Anki {real}.")
    return True


def check_mypy(project: Project, folder: Path, report: Report) -> None:
    if importlib.util.find_spec("mypy") is None:
        report.warn("mypy no está instalado: NO se han comprobado nombres ni firmas de la API de Anki.")
        return
    cmd = [
        sys.executable,
        "-m",
        "mypy",
        "--check-untyped-defs",
        f"--cache-dir={project.root / '.mypy_cache'}",
        folder.name,
    ]
    result = run(cmd, project, folder.parent)
    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        report.ok("mypy: todos los nombres, hooks y firmas de la API existen en esta versión de Anki.")
    else:
        report.error("mypy encontró problemas con la API de Anki o con los tipos:\n    " + tail(output, 30))


def check_import(project: Project, folder: Path, report: Report) -> None:
    code = "import importlib, sys; importlib.import_module(sys.argv[1])"
    result = run([sys.executable, "-c", code, folder.name], project, project.root)
    if result.returncode == 0:
        report.ok("El paquete se importa sin errores fuera de Anki.")
    else:
        report.error(
            "El paquete falla al importarse fuera de Anki (si el fallo es por «mw», proteja el "
            "registro con «if mw is None: return»):\n    " + tail(result.stderr, 12)
        )


def check_tests(project: Project, folder: Path, report: Report) -> None:
    tests = project.tests / folder.name
    if not tests.is_dir() or not list(tests.glob("test*.py")):
        report.warn(f"No hay pruebas de la lógica en pruebas/{folder.name}/.")
        return
    result = run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(tests), "-p", "test*.py"],
        project,
        project.root,
    )
    output = result.stdout + result.stderr
    if result.returncode == 0:
        ran = re.search(r"Ran (\d+) tests?", output)
        report.ok(f"Pruebas: {ran.group(1) if ran else '?'} correctas (colección temporal, nunca la real).")
    else:
        report.error("Fallan las pruebas:\n    " + tail(output, 30))


# ---------------------------------------------------------------------------
# 6. Paquete
# ---------------------------------------------------------------------------


def build_package(
    project: Project, folder: Path, manifest: dict[str, object], files: list[Path], report: Report
) -> Path | None:
    project.packages.mkdir(parents=True, exist_ok=True)
    package = str(manifest["package"])
    version = manifest.get("human_version")
    suffix = "-" + re.sub(r"[^A-Za-z0-9._-]+", "_", str(version)) if version else ""
    target = project.packages / f"{package}{suffix}.ankiaddon"
    partial = target.with_suffix(".tmp")
    try:
        with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.relative_to(folder).as_posix())
        problems = verify_zip(partial, folder, manifest, files)
        if problems:
            for problem in problems:
                report.error("Paquete incorrecto: " + problem)
            return None
        os.replace(partial, target)
    finally:
        if partial.exists():
            partial.unlink()
    report.ok("Paquete verificado: manifest.json en la raíz, sin __pycache__ ni meta.json.")
    return target


def verify_zip(path: Path, folder: Path, manifest: dict[str, object], files: list[Path]) -> list[str]:
    problems: list[str] = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            problems.append(f"entrada dañada: {bad}")
        names = archive.namelist()
        if "manifest.json" not in names:
            problems.append("manifest.json no está en la raíz del zip")
        if "__init__.py" not in names:
            problems.append("__init__.py no está en la raíz del zip")
        for name in names:
            parts = name.split("/")
            if "__pycache__" in parts or name.endswith((".pyc", ".pyo")):
                problems.append(f"contiene {name}")
            if parts[-1] == "meta.json":
                problems.append(f"contiene {name}: lo genera Anki en cada equipo")
            if name.startswith("/") or ".." in parts:
                problems.append(f"ruta peligrosa: {name}")
        expected = {p.relative_to(folder).as_posix() for p in files}
        if expected != set(names):
            problems.append("la lista de archivos del zip no coincide con la de la carpeta")
        if "manifest.json" in names and json.loads(archive.read("manifest.json")) != json.loads(
            (folder / "manifest.json").read_text(encoding="utf-8")
        ):
            problems.append("el manifest.json del zip difiere del de la carpeta")
    return problems


# ---------------------------------------------------------------------------
# Orquestación
# ---------------------------------------------------------------------------


def execute(project: Project, name: str | None, options: Options) -> tuple[Report, Path | None]:
    report = Report()
    folder = pick_addon(project, name, report)
    if folder is None:
        return report, None

    manifest = check_manifest(folder, report)
    files = package_files(folder, report)
    check_json_files(folder, files, report)
    check_python(folder, files, report)
    check_web(folder, files, report)

    package = str(manifest["package"]) if manifest else folder.name
    found = check_fix_notes(project, folder, package, files, options, report)

    if check_environment(project, report):
        if not options.skip_mypy:
            check_mypy(project, folder, report)
        if not options.skip_import:
            check_import(project, folder, report)
        if not options.skip_tests:
            check_tests(project, folder, report)

    if report.errors or manifest is None or found is None:
        return report, None
    if options.only_check:
        save_fix_registry(project, package, found, options)
        return report, None
    built = build_package(project, folder, manifest, files, report)
    if built is not None and not report.errors:
        save_fix_registry(project, package, found, options)
    return report, built


def print_report(report: Report, built: Path | None, only_check: bool, show_path: bool = True) -> None:
    if report.done:
        print("COMPROBADO")
        for line in report.done:
            print(f"  - {line}")
    if report.warnings:
        print("AVISOS (revíselos uno a uno: corríjalos o explíquelos en la entrega)")
        for line in report.warnings:
            print(f"  - {line}")
    if report.errors:
        print("ERRORES")
        for line in report.errors:
            print(f"  - {line}")
        print(f"\nRESULTADO: HAY {len(report.errors)} ERROR(ES). No se ha generado ningún paquete.")
        return
    if built is not None:
        with zipfile.ZipFile(built) as archive:
            print("\nCONTENIDO DEL PAQUETE")
            for info in archive.infolist():
                print(f"  {info.file_size:>8}  {info.filename}")
        print(f"\nRESULTADO: CORRECTO ({len(report.warnings)} aviso(s)).")
        if show_path:
            print(f"PAQUETE: {built}")
    else:
        print(f"\nRESULTADO: CORRECTO ({len(report.warnings)} aviso(s)){' (solo comprobación)' if only_check else ''}.")


def self_test() -> int:
    """Crea un proyecto temporal con un complemento mínimo, otro roto, y comprueba la herramienta."""
    good_init = (
        '"""Complemento mínimo de autoprueba."""\n\nfrom __future__ import annotations\n\n'
        "from aqt import mw\n\n\ndef _register() -> None:\n    if mw is None:\n        return\n\n\n_register()\n"
    )
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        project = Project(Path(tmp))
        good = project.addons / "autoprueba_ok"
        good.mkdir(parents=True)
        (good / "__init__.py").write_text(good_init, encoding="utf-8")
        (good / "manifest.json").write_text(
            json.dumps({"package": "autoprueba_ok", "name": "Autoprueba", "human_version": "0.0.1"}), encoding="utf-8"
        )
        (good / "__pycache__").mkdir()
        (good / "__pycache__" / "x.pyc").write_bytes(b"x")
        (good / "meta.json").write_text("{}", encoding="utf-8")
        options = Options(skip_tests=True)
        report, built = execute(project, "autoprueba_ok", options)
        print_report(report, built, False, show_path=False)
        if report.errors or built is None:
            print("\nAUTOPRUEBA: FALLA con un complemento correcto. No se fíe de esta herramienta hasta arreglarlo.")
            return 1
        with zipfile.ZipFile(built) as archive:
            names = set(archive.namelist())
        if names != {"__init__.py", "manifest.json"}:
            print(f"\nAUTOPRUEBA: el paquete contiene {sorted(names)} en lugar de __init__.py y manifest.json.")
            return 1

        bad = project.addons / "autoprueba_mal"
        bad.mkdir()
        (bad / "__init__.py").write_text("def roto(:\n    pass\n", encoding="utf-8")
        (bad / "manifest.json").write_text(json.dumps({"package": "Mal Nombre", "name": ""}), encoding="utf-8")
        bad_report, bad_built = execute(project, "autoprueba_mal", Options(skip_mypy=True, skip_import=True, skip_tests=True))
        if bad_built is not None or len(bad_report.errors) < 2:
            print("\nAUTOPRUEBA: no detecta errores conocidos (sintaxis y manifiesto). No se fíe de esta herramienta.")
            return 1
    print("\nAUTOPRUEBA: CORRECTA. La herramienta y el entorno funcionan.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Comprueba y empaqueta un complemento de Anki.")
    parser.add_argument("complemento", nargs="?", help="carpeta dentro de complementos/")
    parser.add_argument("--solo-comprobar", action="store_true")
    parser.add_argument("--sin-mypy", action="store_true")
    parser.add_argument("--sin-importar", action="store_true")
    parser.add_argument("--sin-pruebas", action="store_true")
    parser.add_argument("--olvidar-fix", action="append", default=[], metavar="FIX-NNN")
    parser.add_argument("--autoprueba", action="store_true")
    args = parser.parse_args(argv)

    if args.autoprueba:
        return self_test()

    project = Project(Path(__file__).resolve().parent.parent)
    options = Options(
        only_check=args.solo_comprobar,
        skip_mypy=args.sin_mypy,
        skip_import=args.sin_importar,
        skip_tests=args.sin_pruebas,
        forget_fix=args.olvidar_fix,
    )
    report, built = execute(project, args.complemento, options)
    print_report(report, built, options.only_check)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
