document.addEventListener("DOMContentLoaded", function () {
  var formularioFecha = document.getElementById("formulario-fecha");
  var formularioConversion = document.getElementById("formulario-conversion");
  var campoFechaVisible = document.getElementById("fecha");
  var campoFechaOculto = formularioConversion ? formularioConversion.querySelector('input[name="fecha"]') : null;
  var estadoFecha = document.getElementById("estado-fecha");
  var contenedorTabla = document.getElementById("tabla-indicadores");
  var resultadoConversion = document.getElementById("resultado-conversion");

  var NOMBRES_FILA = { uf: "UF", utm: "UTM", dolar: "Dólar observado" };

  function crearTabla(datos) {
    var tabla = document.createElement("table");

    var caption = document.createElement("caption");
    caption.textContent =
      "Valor de la UF, la UTM y el dólar observado " +
      (datos.es_hoy ? "de hoy" : "del " + datos.fecha_legible) +
      ", en pesos chilenos.";
    tabla.appendChild(caption);

    var encabezado = document.createElement("thead");
    var filaEncabezado = document.createElement("tr");
    ["Indicador", "Valor en pesos chilenos"].forEach(function (texto) {
      var celda = document.createElement("th");
      celda.setAttribute("scope", "col");
      celda.textContent = texto;
      filaEncabezado.appendChild(celda);
    });
    encabezado.appendChild(filaEncabezado);
    tabla.appendChild(encabezado);

    var cuerpo = document.createElement("tbody");
    ["uf", "utm", "dolar"].forEach(function (clave) {
      var fila = document.createElement("tr");

      var celdaNombre = document.createElement("th");
      celdaNombre.setAttribute("scope", "row");
      celdaNombre.textContent = NOMBRES_FILA[clave];
      fila.appendChild(celdaNombre);

      var celdaValor = document.createElement("td");
      celdaValor.textContent = datos.indicadores[clave]
        ? "$" + datos.indicadores[clave]
        : (datos.mensajes_sin_dato && datos.mensajes_sin_dato[clave]) || "No disponible";
      fila.appendChild(celdaValor);

      cuerpo.appendChild(fila);
    });
    tabla.appendChild(cuerpo);

    return tabla;
  }

  function mostrarErrorFetch() {
    var alerta = document.createElement("div");
    alerta.setAttribute("role", "alert");
    alerta.setAttribute("tabindex", "-1");
    alerta.textContent =
      "No se pudo completar la consulta por un problema de conexión. Intenta de nuevo.";
    contenedorTabla.innerHTML = "";
    contenedorTabla.appendChild(alerta);
    alerta.focus();
  }

  function construirParametros(formulario) {
    var parametros = new URLSearchParams(new FormData(formulario));
    if (campoFechaVisible) {
      parametros.set("fecha", campoFechaVisible.value);
    }
    if (formularioConversion) {
      var monto = formularioConversion.querySelector("#monto");
      var desde = formularioConversion.querySelector("#desde");
      var hacia = formularioConversion.querySelector("#hacia");
      if (monto && monto.value) {
        parametros.set("monto", monto.value);
        parametros.set("desde", desde.value);
        parametros.set("hacia", hacia.value);
      }
    }
    return parametros;
  }

  function ejecutarConsulta(parametros) {
    parametros.set("formato", "json");

    fetch("/indicadores/consultar?" + parametros.toString())
      .then(function (respuesta) {
        return respuesta.json();
      })
      .then(function (datos) {
        if (datos.estado === "error") {
          mostrarErrorFetch();
          var alertaMensaje = contenedorTabla.querySelector('[role="alert"]');
          if (alertaMensaje) {
            alertaMensaje.textContent = datos.mensaje;
          }
          return;
        }

        contenedorTabla.innerHTML = "";
        contenedorTabla.appendChild(crearTabla(datos));

        if (campoFechaOculto) {
          campoFechaOculto.value = campoFechaVisible ? campoFechaVisible.value : "";
        }

        estadoFecha.textContent = datos.es_hoy
          ? "Mostrando valores de hoy."
          : "Mostrando valores del " + datos.fecha_legible + ".";

        resultadoConversion.textContent = datos.resultado_conversion || datos.error_conversion || "";
      })
      .catch(function () {
        mostrarErrorFetch();
      });
  }

  if (formularioFecha) {
    formularioFecha.addEventListener("submit", function (evento) {
      evento.preventDefault();
      ejecutarConsulta(construirParametros(formularioFecha));
    });
  }

  if (formularioConversion) {
    formularioConversion.addEventListener("submit", function (evento) {
      evento.preventDefault();
      ejecutarConsulta(construirParametros(formularioConversion));
    });
  }
});
