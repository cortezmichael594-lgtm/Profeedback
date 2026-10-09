# Paleta Nocturne — referencia de color para complementos de Anki

> Documento de contexto. Nocturne es el complemento de color **principal**: define
> los colores por defecto de la interfaz de Anki en **modo día** y **modo noche**.
> Cualquier complemento futuro debería tomar estos valores como referencia para que
> su apariencia **combine** con Anki en ambos modos, en lugar de introducir colores
> sueltos. Todos los valores están en formato hexadecimal; los de 8 dígitos incluyen
> transparencia (`#RRGGBBAA`).

## Identidad

Azul sereno de acción sobre una base de grises ligeramente azulados. El modo día es
luminoso y limpio; el modo noche es profundo pero no negro puro, para reducir el
deslumbramiento. El contraste de todos los textos sobre su fondo cumple el nivel AA
de accesibilidad (salvo el texto deshabilitado, atenuado a propósito).

## Cómo usar esta paleta en un complemento futuro

Hay dos vías, según dónde pinte el complemento:

**1. Interfaz nativa (ventanas y widgets Qt).** Cuando Nocturne está activo, ya ha
reescrito los tokens de Anki, así que basta con leer el color del tema activo:

```python
from aqt import colors
from aqt.theme import theme_manager

# Devuelve el valor correcto según el modo (día/noche) en curso:
color = theme_manager.var(colors.CANVAS)          # fondo base
texto = theme_manager.var(colors.FG)              # texto principal
acento = theme_manager.var(colors.BUTTON_PRIMARY_BG)  # azul de acción
```

**2. Contenido web (repaso, editor, vistas propias en webview).** Usa las variables
CSS que Nocturne inyecta, siempre con un valor de reserva por si el complemento se
usa sin Nocturne:

```css
.mi-addon-boton {
  background: var(--button-primary-bg, #3B6FE0);
  color: var(--highlight-fg, #FFFFFF);
  border: 1px solid var(--border, #DCE0E6);
  border-radius: 6px;
}
/* Para adaptarse al modo noche sin JS, apóyate en la clase de Anki: */
body.night_mode .mi-addon-boton {
  background: var(--button-primary-bg, #4066E6);
}
```

No fijes colores a mano si existe un token equivalente: úsalo, y así el complemento
seguirá encajando aunque la paleta se ajuste en el futuro.

## Tabla de colores (modo día y modo noche)

### Lienzos y fondos

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`CANVAS`|`--canvas`|`#F7F8FA`|`#12161F`|
|`CANVAS_ELEVATED`|`--canvas-elevated`|`#FFFFFF`|`#212836`|
|`CANVAS_OVERLAY`|`--canvas-overlay`|`#FFFFFF`|`#191E2A`|
|`CANVAS_INSET`|`--canvas-inset`|`#EEF0F4`|`#0F131B`|
|`CANVAS_CODE`|`--canvas-code`|`#F1F3F7`|`#141924`|
|`CANVAS_GLASS`|`--canvas-glass`|`#FFFFFFCC`|`#212836CC`|

### Texto

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`FG`|`--fg`|`#1B2430`|`#E9EDF4`|
|`FG_SUBTLE`|`--fg-subtle`|`#5C6675`|`#9FABBB`|
|`FG_FAINT`|`--fg-faint`|`#626D7B`|`#8894A6`|
|`FG_DISABLED`|`--fg-disabled`|`#A9B1BD`|`#5B6676`|
|`FG_LINK`|`--fg-link`|`#2F63D8`|`#8DB2FF`|

### Bordes

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`BORDER`|`--border`|`#DCE0E6`|`#2C3545`|
|`BORDER_SUBTLE`|`--border-subtle`|`#E9ECF0`|`#202836`|
|`BORDER_STRONG`|`--border-strong`|`#C2C9D2`|`#3D485C`|
|`BORDER_FOCUS`|`--border-focus`|`#3B6FE0`|`#6390FF`|

### Selección y resaltado

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`HIGHLIGHT_BG`|`--highlight-bg`|`#3B6FE0`|`#4066E6`|
|`HIGHLIGHT_FG`|`--highlight-fg`|`#FFFFFF`|`#FFFFFF`|
|`SELECTED_BG`|`--selected-bg`|`#3B6FE022`|`#6390FF2E`|
|`SELECTED_FG`|`--selected-fg`|`#1B2430`|`#E9EDF4`|

### Botones

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`BUTTON_BG`|`--button-bg`|`#FFFFFF`|`#212836`|
|`BUTTON_HOVER`|`--button-gradient-start`|`#F0F2F6`|`#2A3342`|
|`BUTTON_HOVER_BORDER`|`--button-hover-border`|`#C2C9D2`|`#3D485C`|
|`BUTTON_DISABLED`|`--button-disabled`|`#FFFFFF80`|`#21283680`|
|`BUTTON_PRIMARY_BG`|`--button-primary-bg`|`#3B6FE0`|`#4066E6`|
|`BUTTON_PRIMARY_GRADIENT_START`|`--button-primary-gradient-start`|`#4A7CEA`|`#5480FF`|
|`BUTTON_PRIMARY_GRADIENT_END`|`--button-primary-gradient-end`|`#2F5BC7`|`#3452C8`|
|`BUTTON_PRIMARY_DISABLED`|`--button-primary-disabled`|`#3B6FE059`|`#4066E659`|

### Acentos

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`ACCENT_CARD`|`--accent-card`|`#1971C2`|`#74C0FC`|
|`ACCENT_NOTE`|`--accent-note`|`#2F9E44`|`#57D06B`|
|`ACCENT_DANGER`|`--accent-danger`|`#E03131`|`#FF6B6B`|

### Estados de tarjeta

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`STATE_NEW`|`--state-new`|`#1971C2`|`#74C0FC`|
|`STATE_LEARN`|`--state-learn`|`#E8590C`|`#FFA94D`|
|`STATE_REVIEW`|`--state-review`|`#2F9E44`|`#57D06B`|
|`STATE_BURIED`|`--state-buried`|`#9A7B3F`|`#B08D57`|
|`STATE_SUSPENDED`|`--state-suspended`|`#868E96`|`#8A94A3`|
|`STATE_MARKED`|`--state-marked`|`#7048E8`|`#B197FC`|

### Barras de desplazamiento

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`SCROLLBAR_BG`|`--scrollbar-bg`|`#D6DBE2`|`#273040`|
|`SCROLLBAR_BG_HOVER`|`--scrollbar-bg-hover`|`#C2C9D2`|`#313C4E`|
|`SCROLLBAR_BG_ACTIVE`|`--scrollbar-bg-active`|`#AAB3C0`|`#3D485C`|

### Sombras

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`SHADOW`|`--shadow`|`#1B243026`|`#05080F66`|
|`SHADOW_SUBTLE`|`--shadow-subtle`|`#1B243012`|`#05080F33`|
|`SHADOW_INSET`|`--shadow-inset`|`#1B24301A`|`#05080F4D`|
|`SHADOW_FOCUS`|`--shadow-focus`|`#3B6FE040`|`#6390FF4D`|

### Banderas (flags)

|Token|Variable CSS|LIGHT (día)|DARK (noche)|
|-|-|-|-|
|`FLAG_1`|`--flag-1`|`#E03131`|`#FF6B6B`|
|`FLAG_2`|`--flag-2`|`#E8590C`|`#FFA94D`|
|`FLAG_3`|`--flag-3`|`#2F9E44`|`#69DB7C`|
|`FLAG_4`|`--flag-4`|`#1971C2`|`#74C0FC`|
|`FLAG_5`|`--flag-5`|`#C2255C`|`#E599F7`|
|`FLAG_6`|`--flag-6`|`#099268`|`#63E6BE`|
|`FLAG_7`|`--flag-7`|`#7048E8`|`#B197FC`|

## Bloque para pegar como contexto

Mismo contenido en JSON, cómodo para incluir como referencia rápida:

```json
{
  "ACCENT_CARD": {
    "css": "--accent-card",
    "light": "#1971C2",
    "dark": "#74C0FC"
  },
  "ACCENT_DANGER": {
    "css": "--accent-danger",
    "light": "#E03131",
    "dark": "#FF6B6B"
  },
  "ACCENT_NOTE": {
    "css": "--accent-note",
    "light": "#2F9E44",
    "dark": "#57D06B"
  },
  "BORDER": {
    "css": "--border",
    "light": "#DCE0E6",
    "dark": "#2C3545"
  },
  "BORDER_FOCUS": {
    "css": "--border-focus",
    "light": "#3B6FE0",
    "dark": "#6390FF"
  },
  "BORDER_STRONG": {
    "css": "--border-strong",
    "light": "#C2C9D2",
    "dark": "#3D485C"
  },
  "BORDER_SUBTLE": {
    "css": "--border-subtle",
    "light": "#E9ECF0",
    "dark": "#202836"
  },
  "BUTTON_BG": {
    "css": "--button-bg",
    "light": "#FFFFFF",
    "dark": "#212836"
  },
  "BUTTON_DISABLED": {
    "css": "--button-disabled",
    "light": "#FFFFFF80",
    "dark": "#21283680"
  },
  "BUTTON_HOVER": {
    "css": "--button-gradient-start",
    "light": "#F0F2F6",
    "dark": "#2A3342"
  },
  "BUTTON_HOVER_BORDER": {
    "css": "--button-hover-border",
    "light": "#C2C9D2",
    "dark": "#3D485C"
  },
  "BUTTON_PRIMARY_BG": {
    "css": "--button-primary-bg",
    "light": "#3B6FE0",
    "dark": "#4066E6"
  },
  "BUTTON_PRIMARY_DISABLED": {
    "css": "--button-primary-disabled",
    "light": "#3B6FE059",
    "dark": "#4066E659"
  },
  "BUTTON_PRIMARY_GRADIENT_END": {
    "css": "--button-primary-gradient-end",
    "light": "#2F5BC7",
    "dark": "#3452C8"
  },
  "BUTTON_PRIMARY_GRADIENT_START": {
    "css": "--button-primary-gradient-start",
    "light": "#4A7CEA",
    "dark": "#5480FF"
  },
  "CANVAS": {
    "css": "--canvas",
    "light": "#F7F8FA",
    "dark": "#12161F"
  },
  "CANVAS_CODE": {
    "css": "--canvas-code",
    "light": "#F1F3F7",
    "dark": "#141924"
  },
  "CANVAS_ELEVATED": {
    "css": "--canvas-elevated",
    "light": "#FFFFFF",
    "dark": "#212836"
  },
  "CANVAS_GLASS": {
    "css": "--canvas-glass",
    "light": "#FFFFFFCC",
    "dark": "#212836CC"
  },
  "CANVAS_INSET": {
    "css": "--canvas-inset",
    "light": "#EEF0F4",
    "dark": "#0F131B"
  },
  "CANVAS_OVERLAY": {
    "css": "--canvas-overlay",
    "light": "#FFFFFF",
    "dark": "#191E2A"
  },
  "FG": {
    "css": "--fg",
    "light": "#1B2430",
    "dark": "#E9EDF4"
  },
  "FG_DISABLED": {
    "css": "--fg-disabled",
    "light": "#A9B1BD",
    "dark": "#5B6676"
  },
  "FG_FAINT": {
    "css": "--fg-faint",
    "light": "#626D7B",
    "dark": "#8894A6"
  },
  "FG_LINK": {
    "css": "--fg-link",
    "light": "#2F63D8",
    "dark": "#8DB2FF"
  },
  "FG_SUBTLE": {
    "css": "--fg-subtle",
    "light": "#5C6675",
    "dark": "#9FABBB"
  },
  "FLAG_1": {
    "css": "--flag-1",
    "light": "#E03131",
    "dark": "#FF6B6B"
  },
  "FLAG_2": {
    "css": "--flag-2",
    "light": "#E8590C",
    "dark": "#FFA94D"
  },
  "FLAG_3": {
    "css": "--flag-3",
    "light": "#2F9E44",
    "dark": "#69DB7C"
  },
  "FLAG_4": {
    "css": "--flag-4",
    "light": "#1971C2",
    "dark": "#74C0FC"
  },
  "FLAG_5": {
    "css": "--flag-5",
    "light": "#C2255C",
    "dark": "#E599F7"
  },
  "FLAG_6": {
    "css": "--flag-6",
    "light": "#099268",
    "dark": "#63E6BE"
  },
  "FLAG_7": {
    "css": "--flag-7",
    "light": "#7048E8",
    "dark": "#B197FC"
  },
  "HIGHLIGHT_BG": {
    "css": "--highlight-bg",
    "light": "#3B6FE0",
    "dark": "#4066E6"
  },
  "HIGHLIGHT_FG": {
    "css": "--highlight-fg",
    "light": "#FFFFFF",
    "dark": "#FFFFFF"
  },
  "SCROLLBAR_BG": {
    "css": "--scrollbar-bg",
    "light": "#D6DBE2",
    "dark": "#273040"
  },
  "SCROLLBAR_BG_ACTIVE": {
    "css": "--scrollbar-bg-active",
    "light": "#AAB3C0",
    "dark": "#3D485C"
  },
  "SCROLLBAR_BG_HOVER": {
    "css": "--scrollbar-bg-hover",
    "light": "#C2C9D2",
    "dark": "#313C4E"
  },
  "SELECTED_BG": {
    "css": "--selected-bg",
    "light": "#3B6FE022",
    "dark": "#6390FF2E"
  },
  "SELECTED_FG": {
    "css": "--selected-fg",
    "light": "#1B2430",
    "dark": "#E9EDF4"
  },
  "SHADOW": {
    "css": "--shadow",
    "light": "#1B243026",
    "dark": "#05080F66"
  },
  "SHADOW_FOCUS": {
    "css": "--shadow-focus",
    "light": "#3B6FE040",
    "dark": "#6390FF4D"
  },
  "SHADOW_INSET": {
    "css": "--shadow-inset",
    "light": "#1B24301A",
    "dark": "#05080F4D"
  },
  "SHADOW_SUBTLE": {
    "css": "--shadow-subtle",
    "light": "#1B243012",
    "dark": "#05080F33"
  },
  "STATE_BURIED": {
    "css": "--state-buried",
    "light": "#9A7B3F",
    "dark": "#B08D57"
  },
  "STATE_LEARN": {
    "css": "--state-learn",
    "light": "#E8590C",
    "dark": "#FFA94D"
  },
  "STATE_MARKED": {
    "css": "--state-marked",
    "light": "#7048E8",
    "dark": "#B197FC"
  },
  "STATE_NEW": {
    "css": "--state-new",
    "light": "#1971C2",
    "dark": "#74C0FC"
  },
  "STATE_REVIEW": {
    "css": "--state-review",
    "light": "#2F9E44",
    "dark": "#57D06B"
  },
  "STATE_SUSPENDED": {
    "css": "--state-suspended",
    "light": "#868E96",
    "dark": "#8A94A3"
  }
}
```

## Reglas de coherencia

* **Haz** que cada elemento nuevo derive su color de un token de esta tabla.
* **Haz** que el color de acción (botones/enlaces destacados) use el azul
`BUTTON_PRIMARY_BG` / `HIGHLIGHT_BG`; es el azul de acción del sistema.
* **Haz** que el texto sobre un fondo de acción use `HIGHLIGHT_FG` (blanco).
* **Haz** que cualquier color que definas a mano tenga su pareja día **y** noche.
* **Evita** el negro puro (`#000`) y el blanco puro como fondos: usa `CANVAS` y
`CANVAS_ELEVATED`.
* **Evita** introducir un segundo azul de acción distinto; reutiliza el existente.
* **Evita** rojos o verdes fuera de los ya definidos (`ACCENT_DANGER`,
`ACCENT_NOTE`, `FLAG_*`), para no romper el código de color de Anki.
