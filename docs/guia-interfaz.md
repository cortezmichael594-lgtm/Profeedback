# Guía de interfaz: nativa, fluida y con la paleta Nocturne

Documento del proyecto, comprobado contra el código de Anki 26.09.3. Léalo entero antes
de diseñar o escribir cualquier ventana, menú, botón o página. Los nombres de aquí son
los que existen en esa versión; ante cualquier duda, confírmelos con Grep en el código
real del entorno (`.venv`, carpetas `aqt` y `_aqt`).

## 1. Nativo primero

Un elemento nativo pasa por parte de Anki: hereda el tema (también Nocturne), las
fuentes, el teclado, las traducciones y los cambios de versiones futuras sin trabajo
extra. Uno dibujado a mano hay que mantenerlo. Por eso, para cada necesidad se usa
primero la pieza que Anki ya tiene:

| Necesidad | Pieza nativa |
|---|---|
| Una acción puntual | Entrada en un menú existente: `mw.form.menuTools.addAction(QAction(texto, mw))`. Existen también `menuCol`, `menuEdit` y `menuHelp`. Varias acciones: un submenú `QMenu`. |
| Acción sobre notas o tarjetas | Menús del navegador con el hook `browser_menus_did_init(browser)` (`browser.form.menu_Notes`, `menu_Cards`, `menuEdit`) y el menú contextual con `browser_will_show_context_menu(browser, menu)`. |
| Acción durante el repaso | Menú contextual: `reviewer_will_show_context_menu(reviewer, menu)`. Botones de respuesta: `reviewer_will_init_answer_buttons`. |
| Acceso principal | Barra superior: `top_toolbar_did_init_links(links, toolbar)` con `links.append(toolbar.create_link(cmd, label, func, tip, id))`. Solo si la persona lo pide: la barra es pequeña. |
| Botón en el editor | `editor_did_init_buttons(buttons, editor)` y `editor.addButton(...)`. En 26.09 conviven `Editor` y `NewEditor`: lea el código real y pruebe ambos tipos. |
| Opciones del complemento | `QDialog` con controles estándar (`QCheckBox`, `QSpinBox`, `QComboBox`, `QLineEdit`, `QFormLayout`) y `QDialogButtonBox` con Aceptar y Cancelar, registrado con `setConfigAction`. Esa función devuelve `None`: si devolviera `False`, Anki abriría su editor de JSON. |
| Aviso breve que no estorba | `tooltip(texto)`. |
| Aviso que exige atención | `showInfo`, `showWarning`. |
| Pedir un texto o confirmar | `getText`, `askUser(..., defaultno=True)` (en operaciones masivas, para que un Intro de más no confirme). |
| Trabajo que tarda | `QueryOp(...).with_progress(texto)` o `CollectionOp`; nunca un `QProgressDialog` propio. |
| Atajo de teclado | `QAction.setShortcut(...)`; compruebe que no choca con los de Anki. |
| Icono propio | SVG monocolor: `ColoredIcon(path, color=colors.FG)` con `theme_manager.icon_from_resources(...)` en Qt; `currentColor` en web. |
| Pantalla propia con contenido web | Solo si nada nativo sirve: `AnkiWebView`, nunca un `QWebEngineView` suelto. |

En una página web (propia o inyectada), también nativo: `<button>`, `<input>`, `<select>`,
`<details>` y `<dialog>` en lugar de `<div>` con clic. Traen teclado, foco y accesibilidad.

Un control dibujado a mano, o un menú o botón con aspecto propio, solo si la persona lo
pide de forma expresa; en ese caso, avíselo en el plan.

## 2. La paleta Nocturne en la práctica

El documento `docs/paleta-nocturne.md` manda sobre estos resúmenes (tabla completa de
valores día y noche). Nocturne redefine los colores que Anki ya tiene; este proyecto no
inventa colores: los toma de ahí.

- **Qt.** `theme_manager.var(colors.CANVAS)` devuelve el texto del color y
  `theme_manager.qcolor(colors.FG)` un `QColor`, según el modo activo. Se leen en el
  momento de pintar, dentro de la función que pinta, y se repintan con
  `gui_hooks.theme_did_change`. Dos motivos: Anki carga los complementos por orden
  alfabético de carpeta, así que Nocturne puede cargarse después y redefinir los
  colores; y quien guarda el color al arrancar lo ve desfasado al cambiar de modo.
  Se accede siempre como `colors.X`: no se importan los nombres sueltos (`from aqt.colors
  import CANVAS`), porque guardarían la referencia antigua.
- **Controles estándar de Qt** (casillas, botones, listas, campos): ya toman el tema.
  No se les pone ningún color ni hoja de estilos.
- **Web.** `var(--token, reserva)`, con la reserva tomada de la columna día de la
  paleta y su pareja de modo noche en `body.night_mode`. Todas las variables de la
  paleta existen en las páginas de Anki 26.09.3.
- **Aviso de nombres.** En el documento de Nocturne, la fila `BUTTON_HOVER` corresponde,
  en Anki 26.09.3, a `BUTTON_GRADIENT_START` (CSS `--button-gradient-start`). El nombre
  `colors.BUTTON_HOVER` no existe y daría error. Anki tiene además `BUTTON_GRADIENT_END`.
  Antes de usar un token, confírmelo con Grep en `_aqt/colors.py` del `.venv`.
- **Reglas de coherencia.** Un único azul de acción (`BUTTON_PRIMARY_BG` o `HIGHLIGHT_BG`),
  con `HIGHLIGHT_FG` encima; fondos con `CANVAS` y `CANVAS_ELEVATED`, nunca negro ni blanco
  puros; rojos y verdes solo de `ACCENT_DANGER`, `ACCENT_NOTE`, `STATE_*` y `FLAG_*`; todo
  color que defina el complemento lleva su pareja de día y de noche.
- **Control automático.** `herramientas/empaquetar.py` rechaza los colores fijos. La
  única excepción es una línea con la marca `colores-ok: motivo`, para un valor de
  reserva legítimo.

## 3. Sin parpadeos: interfaz Qt

1. Cree una vez y muestre muchas. Una ventana que se abre a menudo conserva su instancia
   (en un atributo o con un padre, para que no la recoja el recolector de basura) y se
   muestra con `show()`, `raise_()` y `activateWindow()`; no se reconstruye.
2. Cambie lo que ya existe (texto, estado, datos del modelo) en lugar de destruir y
   recrear controles o disposiciones.
3. Antes de mostrar un diálogo, constrúyalo entero; tamaño y posición con
   `restoreGeom` y `saveGeom`, para que no salte al abrirse.
4. Varios cambios visuales seguidos: agrúpelos entre `setUpdatesEnabled(False)` y
   `setUpdatesEnabled(True)`.
5. Ni `setStyleSheet` repetido o en bucles, ni `QApplication.processEvents()`, ni
   `time.sleep`.
6. Todo trabajo que tarde va fuera del hilo principal (`QueryOp`, `CollectionOp`); la
   interfaz solo se toca desde el hilo principal, y para refrescar el progreso desde el
   segundo plano se usa `mw.taskman.run_on_main(...)`.
7. Listas largas: un modelo con su vista (`QStandardItemModel` con `QListView`), no un
   control por fila.
8. Reaccione al cambio de modo día o noche con `gui_hooks.theme_did_change`, una vez; no
   consulte el tema en bucle.
9. Animaciones: ninguna, salvo petición expresa. Si se piden: máximo 150 ms.

## 4. Sin parpadeos: contenido web

Anki ya cuida lo suyo (comprobado en `webview.py`): cada `AnkiWebView` fija el fondo de la
página al color `CANVAS` «para reducir el parpadeo» y lo repinta al cambiar el tema; las
pantallas con páginas propias (editor, opciones de mazo, estadísticas) permanecen ocultas
hasta que su estilo está inyectado. Para no estropearlo:

1. Use `AnkiWebView` y los hooks de Anki. Si alguna vez hace falta una vista propia:
   `page().setBackgroundColor(theme_manager.qcolor(colors.CANVAS))` antes de cargar.
2. Todo el CSS, JS y HTML propio entra por `webview_will_set_content`, antes del primer
   pintado: `web_content.css.append(...)`, `web_content.js.append(...)`,
   `web_content.body += ...`. Inyectarlo después con `eval` hace que aparezca de golpe.
3. Lo que aparece más tarde no desplaza nada: `position: fixed` o `absolute`, o su hueco
   reservado desde el principio (`min-height`, `aspect-ratio`).
4. Actualice el DOM existente (`textContent`, clases) en vez de recargar la página o
   rehacer su HTML.
5. Anime solo `opacity` y `transform`, un máximo de 150 ms, y respete
   `@media (prefers-reduced-motion: reduce)`.
6. El JavaScript es idempotente: Anki puede reinyectarlo, así que comprueba si el nodo o
   el listener ya existe antes de crearlo (véase `ejemplo.js` del ejemplo de referencia).
7. Durante el repaso: `card_will_show` para cambiar el HTML de la tarjeta;
   `onUpdateHook` (con el contenido nuevo ya colocado, antes del fundido) y
   `onShownHook` (después del fundido) para el JS que dependa del momento. Los hooks se
   reinician con cada tarjeta.
8. Sin internet: nada de CDNs ni fuentes externas; todo dentro del paquete, servido con
   `setWebExports`.
9. Chromium 140: sirve el CSS moderno (`:has()`, `color-mix()`, anidamiento, `@layer`,
   consultas de contenedor). Si duda de una función, compruébela en MDN.

## 5. Ejemplo completo

`docs/ejemplo-referencia/` contiene un complemento pequeño que sigue esta guía y supera
todas las comprobaciones: dos entradas en el menú Herramientas, diálogo de opciones
nativo, operación masiva con búsqueda, confirmación con la cifra exacta y deshacer, e
insignia en el repaso con las variables de la paleta. Es un modelo de estructura, no un
complemento para instalar; los complementos reales se crean en `complementos/`.
