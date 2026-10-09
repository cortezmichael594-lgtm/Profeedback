# Errores de «Ejemplo de referencia»

Registro en lenguaje llano de los fallos de este complemento. Lo mantiene Claude Code: cada corrección
del código (FIX-NNN) tiene aquí su línea con el mismo número, y el comprobador vigila que no falte
ninguna.

## Pendientes

Fallos detectados que esperan su decisión. Cada uno: fecha, versión, qué pasa y propuesta.

- 2026-10-09 · versión 1.0.0 · Qué pasa: con una sola nota, la pregunta y el aviso final dicen
  «1 notas» («Se etiquetarán 1 notas con «ejemplo». ¿Continuar?» y «Se etiquetaron 1 notas…»).
  Propuesta: escribir «nota» o «notas» según la cifra, como «1 nota» y «2 notas».

## Corregidos

Cada corrección: número, fecha, versión, qué pasaba, por qué pasaba y la regla que evita que vuelva.

(Ninguna todavía.)

## Así a propósito

Lo que parece un fallo pero se decidió así, y quién lo decidió. No se «arregla» sin preguntar.

- 1.0.0 · Etiquetar notas no hace copia de seguridad antes de cambiar nada. Lo decide el criterio del
  taller: la copia previa se reserva para borrar o cambiar lo que ya existe, y añadir una etiqueta no
  es ninguna de las dos cosas. Sí hay confirmación con la cifra exacta y se puede deshacer.
