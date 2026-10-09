# Preparar el entorno de trabajo

Se hace una sola vez, y de nuevo si Anki cambia de versión. Todo queda dentro de esta carpeta (en `.venv/`), salvo `uv` si hiciera falta instalarlo. Avise al cliente, en una frase, de que tarda unos minutos y descarga unos 300 MB. Los comandos están escritos con barra normal (`/`) para que valgan en PowerShell y en Git Bash.

## 1. Buscar un Python válido

Pruebe por este orden y quédese con el primero que dé una versión 3.10 o superior (mejor 3.13):

1. `uv --version`. Con uv no hace falta tener Python: si falta, uv lo descarga.
2. `py -3.13 --version`.
3. `python --version`. Si abre la Tienda de Microsoft o no imprime nada, es el falso `python` de Windows: cuente que no hay Python.

Si no hay ninguno, explique al cliente que `uv` es un instalador de Python de código abierto (de Astral) y pida permiso antes de instalarlo, porque se instala fuera de esta carpeta:

```
winget install --id=astral-sh.uv -e
```

Si después `uv` no se reconoce, llámelo por su ruta completa (`%LOCALAPPDATA%\Microsoft\WinGet\Links\uv.exe`) o pida al cliente que cierre y vuelva a abrir Claude Code.

## 2. Crear el entorno

- Con uv: `uv venv .venv --python 3.13`
- Sin uv: `py -3.13 -m venv .venv` (o `python -m venv .venv`)

## 3. Instalar lo mismo que usa Anki

La versión de `aqt` debe coincidir con la de Anki del cliente, porque con ella se comprueban los nombres de la API. PyPI escribe `26.9.3` donde Anki dice `26.09.3`. Se instala también `mypy`, que detecta nombres inventados.

- Con uv: `uv pip install --python .venv/Scripts/python.exe "aqt[qt]==26.9.3" mypy`
- Sin uv: `.venv/Scripts/python -m pip install "aqt[qt]==26.9.3" mypy`

## 4. Comprobar

`.venv/Scripts/python herramientas/empaquetar.py --autoprueba` debe terminar en «AUTOPRUEBA: CORRECTA». Esa prueba crea un complemento mínimo en una carpeta temporal y recorre todo el proceso (mypy, importación y empaquetado), así que confirma que el entorno y la herramienta funcionan.

## 5. Control de versiones (opcional)

Si git está instalado y no hay repositorio: `git init`. No instale git.

## 6. Resumen al cliente

En cuatro líneas como máximo: qué ha quedado preparado y qué falta, si falta algo.

## Anki ha cambiado de versión

Cuando el cliente diga que ha actualizado Anki a la versión X.Y.Z (Ayuda > Acerca de Anki):

1. Cambie `herramientas/version-anki.txt` y los datos de `<entorno>` de `CLAUDE.md`. Es un cambio de las reglas pedido por el cliente: guarde antes la copia en `herramientas/copias/` y regístrelo en «Cambios aprobados» de `docs/automejora.md` con la huella nueva (véase `<automejora>`).
2. Reinstale en el entorno: `uv pip install --python .venv/Scripts/python.exe "aqt[qt]==X.Y.Z" mypy` (sin cero a la izquierda en el mes: 26.09.3 se escribe 26.9.3). Si PyPI aún no publica esa versión, dígaselo al cliente y espere.
3. Lea las notas de esa versión en https://github.com/ankitects/anki/releases (desde la 23.12 están ahí y no en el manual) y apunte lo que afecte a los complementos.
4. Ejecute `empaquetar.py` sobre cada complemento de `complementos/`. Resuma al cliente qué falla y arréglelo; cada arreglo lleva su nota FIX.
5. Ejecute `empaquetar.py --revision`: señala los aprendizajes comprobados con la versión anterior. Vuelva a comprobar cada uno en el código nuevo y, según el caso, actualice su versión, corríjalo o retírelo con su motivo.
