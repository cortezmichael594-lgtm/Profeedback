/* Insignia del complemento de ejemplo: conecta el botón con Python.

   Anki puede volver a inyectar este script, así que primero se comprueba si el
   botón ya está conectado: sin esa guarda se acumularían escuchas duplicadas. */
(function () {
  "use strict";
  var badge = document.getElementById("ejemplo-referencia-badge");
  if (!badge || badge.dataset.ejemploBound === "1") {
    return;
  }
  badge.dataset.ejemploBound = "1";
  badge.addEventListener("click", function () {
    pycmd("ejemplo_referencia:options");
  });
})();
