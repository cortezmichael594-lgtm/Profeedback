# Qué hace «Ejemplo de referencia»

Versión 1.0.0 · 2026-10-09

Complemento de muestra del taller: no está pensado para instalarse, sino para copiar su forma de
trabajar. Añade dos entradas al menú Herramientas y, si se activa, un botón pequeño en la pantalla de
repaso. Solo cambia algo de su colección en un caso: cuando usted le pide etiquetar notas y lo
confirma, y eso se puede deshacer. Lo único que guarda por su cuenta son sus dos opciones.

## 1. Dónde aparece

- En el menú Herramientas, dos entradas: «Ejemplo de referencia: opciones…» y «Ejemplo de referencia:
  etiquetar notas…».
- En Herramientas > Complementos, al seleccionarlo y pulsar «Configuración», se abre su ventana de
  opciones, no el editor de texto que Anki muestra con otros complementos.
- En la pantalla de repaso, una insignia «Ejemplo» en la esquina superior derecha, si esa opción está
  activada.
- No aparece en la lista de mazos, en la pantalla de un mazo, en Explorar, en el editor ni en las
  estadísticas.

## 2. La insignia del repaso

- Es un botón pequeño y redondeado con el texto «Ejemplo». Queda fijo arriba a la derecha, por encima
  de la tarjeta: no ocupa sitio ni la desplaza.
- Usa los colores del tema de Anki (el azul de acción, con su versión para el modo noche) y se
  oscurece un poco al pasar el ratón.
- Aparece con un fundido muy breve, de algo más de una décima de segundo. Si el sistema tiene activada
  la opción de reducir las animaciones, aparece sin fundido.
- Al pasar el ratón muestra el globo «Abrir las opciones del complemento de ejemplo». Al pulsarla, se
  abre la ventana de opciones.
- Se puede alcanzar con el tabulador; entonces un recuadro indica que está seleccionada. Con el ratón
  no sale ese recuadro.
- Se coloca al entrar a repasar. Si la desactiva en las opciones mientras repasa, sigue visible hasta
  que salga del repaso y vuelva a entrar. Al activarla, aparece la próxima vez que entre a repasar.

## 3. Ventana de opciones

- Título: «Ejemplo de referencia». No tiene botón de ayuda.
- Casilla «Mostrar la insignia durante el repaso»: marcada por defecto.
- Campo «Etiqueta que se añadirá:»: por defecto, «ejemplo». Se guarda sin los espacios del principio
  y del final.
- Botones Aceptar y Cancelar. Aceptar guarda y muestra un aviso breve, «Opciones guardadas.»;
  Cancelar cierra sin guardar nada.
- La ventana recuerda su tamaño y su posición.

## 4. Etiquetar notas

1. Pregunta, en una ventana pequeña titulada «Anki»: «¿Qué notas quiere etiquetar? Escriba una
   búsqueda, igual que en el navegador de tarjetas.»
2. Si cancela o deja la búsqueda vacía (o solo con espacios), no hace nada.
3. Toma la etiqueta de las opciones y cambia sus espacios por guiones bajos: «mi etiqueta» se
   convierte en «mi_etiqueta». Si queda vacía, avisa «La etiqueta está vacía. Escriba una en las
   opciones del complemento.» y no sigue.
4. Busca las notas sin congelar Anki; si tarda, aparece la ventana de progreso «Buscando notas…».
5. Si la búsqueda está mal escrita, avisa «No se pudo hacer la búsqueda:» seguido del motivo que da
   Anki.
6. Si no encuentra nada, muestra el aviso breve «No hay ninguna nota que coincida con esa búsqueda.»
7. Si encuentra notas, pregunta con la cifra exacta y punto de millar: «Se etiquetarán 1.240 notas con
   «ejemplo». ¿Continuar?». El botón marcado de antemano es «No», para que un Intro de más no lo
   confirme.
8. Si acepta, etiqueta todas de una vez, sin congelar Anki, y avisa «Se etiquetaron 1.240 notas. Puede
   deshacerlo desde Editar → Deshacer.». Esa cifra cuenta solo las notas que han cambiado: las que ya
   tenían la etiqueta no suman, así que puede ser menor que la de la pregunta.
9. Editar > Deshacer quita la etiqueta de todas esas notas de una sola vez.

No hace copia de seguridad antes de etiquetar: añadir una etiqueta no borra ni cambia nada de lo que
ya había, y se puede deshacer.

## 5. Qué guarda y dónde

- Sus dos opciones, en la configuración de complementos de Anki de ese ordenador: valen para todos los
  perfiles y no viajan con la sincronización.
- Si falta una opción o tiene un valor que no sirve (por ejemplo, porque viene de una versión anterior
  del complemento), usa el valor por defecto.
- La etiqueta queda en las notas, como cualquier otra, y viaja con la sincronización.

## 6. Idiomas

Sus textos están solo en español, sea cual sea el idioma de Anki. Los botones estándar (Aceptar,
Cancelar, Sí, No) salen en el idioma de Anki.

## 7. Si algo falla

- Nunca abre la ventana de error de Anki. En su lugar muestra durante 5 segundos el aviso «El
  complemento de ejemplo tuvo un problema. Anki sigue funcionando; el detalle quedó en su registro.»,
  una sola vez por cada función y sesión, para no llenar la pantalla si el fallo se repite.
- El detalle técnico queda anotado en el registro del complemento.

## 8. Qué no hace

- No se conecta a internet.
- No cambia nada de su colección salvo añadir la etiqueta que usted confirma.
- No quita etiquetas: para eso están Editar > Deshacer o Explorar.
- No aparece fuera de los sitios del apartado 1.
