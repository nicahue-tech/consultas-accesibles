document.addEventListener("DOMContentLoaded", function () {
  var avisoGeolocalizacion = document.getElementById("aviso-geolocalizacion");
  var avisoUbicacionDetectada = document.getElementById("aviso-ubicacion-detectada");
  var campoCiudad = document.getElementById("ciudad");
  var listaSugerenciasUbicacion = document.getElementById("sugerencias-ubicacion");
  var campoLat = document.getElementById("lat");
  var campoLon = document.getElementById("lon");
  var formulario = document.getElementById("formulario-sismos");
  var ubicacionModificadaPorUsuario = false;
  var temporizadorSugerencias = null;
  var MAPA_TILDES = { "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
                       "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U" };

  function quitarTildes(texto) {
    return texto.replace(/[áéíóúÁÉÍÓÚ]/g, function (letra) {
      return MAPA_TILDES[letra];
    });
  }

  // Autocompletado con el elemento nativo datalist: mientras el usuario
  // escribe, se piden sugerencias de nombres de lugar a Nominatim (a través
  // del propio servidor) para reducir errores de ortografía. Es una mejora
  // progresiva: si el navegador o el lector de pantalla no muestra bien las
  // sugerencias, el campo de texto sigue funcionando igual que siempre.
  //
  // Las sugerencias siempre se guardan sin tilde (ver servicio_geocodificacion.py)
  // porque Safari filtra las opciones del datalist comparando letra por letra
  // contra lo escrito, sin reconocer que "a" y "á" son la misma letra. Para que
  // esa comparación coincida sin importar cómo se escriba, este campo también
  // quita automáticamente cualquier tilde apenas se escribe, sin mover el
  // cursor (quitar una tilde no cambia el largo del texto).
  if (campoCiudad && listaSugerenciasUbicacion) {
    campoCiudad.addEventListener("input", function () {
      var inicioSeleccion = campoCiudad.selectionStart;
      var finSeleccion = campoCiudad.selectionEnd;
      var valorSinTildes = quitarTildes(campoCiudad.value);
      if (valorSinTildes !== campoCiudad.value) {
        campoCiudad.value = valorSinTildes;
        campoCiudad.setSelectionRange(inicioSeleccion, finSeleccion);
      }

      ubicacionModificadaPorUsuario = true;
      var consulta = campoCiudad.value.trim();

      clearTimeout(temporizadorSugerencias);
      if (consulta.length < 3) {
        listaSugerenciasUbicacion.innerHTML = "";
        return;
      }

      temporizadorSugerencias = setTimeout(function () {
        fetch("/sismos/sugerencias-ubicacion?q=" + encodeURIComponent(consulta))
          .then(function (respuesta) {
            return respuesta.json();
          })
          .then(function (datos) {
            listaSugerenciasUbicacion.innerHTML = "";
            (datos.sugerencias || []).forEach(function (sugerencia) {
              var opcion = document.createElement("option");
              opcion.value = sugerencia;
              listaSugerenciasUbicacion.appendChild(opcion);
            });
          })
          .catch(function () {
            listaSugerenciasUbicacion.innerHTML = "";
          });
      }, 600);
    });
  }
  var estadoBusqueda = document.getElementById("estado-busqueda-sismos");
  var contenedorResultados = document.getElementById("resultados-sismos");
  var confirmacionSeleccion = document.getElementById("confirmacion-seleccion");
  var campoMagnitud = document.getElementById("magnitud_min");
  var campoRadio = document.getElementById("radio_km");
  var campoPeriodo = document.getElementById("rango_tiempo");

  // Refuerzo de confirmación por voz, independiente del anuncio nativo del
  // select: Safari con VoiceOver tiene un bug documentado (visto antes en
  // Blindmachine) donde a veces sigue anunciando el valor anterior aunque
  // el valor real guardado en el formulario ya sea el correcto.
  function confirmarSeleccion(texto) {
    confirmacionSeleccion.textContent = texto;
  }

  if (campoMagnitud) {
    campoMagnitud.addEventListener("change", function () {
      var opcion = campoMagnitud.options[campoMagnitud.selectedIndex];
      if (campoMagnitud.value === "todas") {
        confirmarSeleccion("Magnitud: se mostrarán sismos de todas las magnitudes.");
      } else {
        confirmarSeleccion("Magnitud mayor a " + opcion.textContent + " seleccionada.");
      }
    });
  }

  if (campoRadio) {
    campoRadio.addEventListener("change", function () {
      var opcion = campoRadio.options[campoRadio.selectedIndex];
      confirmarSeleccion("Radio " + opcion.textContent + " seleccionado.");
    });
  }

  if (campoPeriodo) {
    campoPeriodo.addEventListener("change", function () {
      var opcion = campoPeriodo.options[campoPeriodo.selectedIndex];
      confirmarSeleccion("Periodo seleccionado: " + opcion.textContent + ".");
    });
  }

  function mostrarAvisoGeolocalizacion(texto) {
    avisoGeolocalizacion.textContent = texto;
    avisoGeolocalizacion.hidden = false;
  }

  function anunciarUbicacionDetectada(lat, lon) {
    var parametros = new URLSearchParams({ lat: lat, lon: lon });
    fetch("/sismos/ubicacion-legible?" + parametros.toString())
      .then(function (respuesta) {
        return respuesta.json();
      })
      .then(function (datos) {
        if (datos.estado === "ok" && datos.ubicacion_legible) {
          avisoUbicacionDetectada.textContent = "Ubicación detectada: " + datos.ubicacion_legible + ".";
          if (!ubicacionModificadaPorUsuario) {
            campoCiudad.value = datos.ubicacion_legible;
            if (formulario) {
              ejecutarBusqueda(construirParametrosBusqueda());
            }
          }
        } else {
          avisoUbicacionDetectada.textContent =
            "Se detectó tu ubicación, pero no se pudo obtener el nombre del lugar. Puedes escribir una ciudad o lugar manualmente.";
        }
      })
      .catch(function () {
        avisoUbicacionDetectada.textContent =
          "Se detectó tu ubicación, pero no se pudo obtener el nombre del lugar. Puedes escribir una ciudad o lugar manualmente.";
      });
  }

  // Geolocalización: guarda la latitud y longitud en campos ocultos (nunca
  // se muestran en pantalla) y, solo si se logra anunciar el nombre del
  // lugar detectado, completa el campo visible de ubicación y dispara una
  // primera búsqueda automática con los valores por defecto del formulario.
  // Si la geolocalización falla o se deniega, no se dispara ninguna
  // búsqueda: el formulario manual queda disponible esperando al usuario.
  if (!("geolocation" in navigator)) {
    mostrarAvisoGeolocalizacion(
      "Este navegador no permite detectar tu ubicación automáticamente. Puedes buscar por ciudad o ingresar las coordenadas manualmente."
    );
  } else {
    navigator.geolocation.getCurrentPosition(
      function (posicion) {
        var lat = posicion.coords.latitude.toFixed(4);
        var lon = posicion.coords.longitude.toFixed(4);
        campoLat.value = lat;
        campoLon.value = lon;
        anunciarUbicacionDetectada(lat, lon);
      },
      function () {
        mostrarAvisoGeolocalizacion(
          "No se pudo obtener tu ubicación. Puedes buscar por ciudad o ingresar las coordenadas manualmente."
        );
      }
    );
  }

  function crearElementoResultados(datos) {
    if (datos.resultados.length === 0) {
      var vacio = document.createElement("p");
      vacio.textContent = "No se encontraron sismos con estos criterios.";
      return vacio;
    }
    var lista = document.createElement("ul");
    datos.resultados.forEach(function (sismo) {
      var item = document.createElement("li");

      var parrafoLugar = document.createElement("p");
      parrafoLugar.textContent = sismo.lugar + ", " + sismo.fecha_hora_legible + ".";
      item.appendChild(parrafoLugar);

      var parrafoProfundidad = document.createElement("p");
      parrafoProfundidad.textContent =
        "Profundidad: " + sismo.profundidad_km + " kilómetros (" + sismo.profundidad_descripcion + ").";
      item.appendChild(parrafoProfundidad);

      var parrafoMagnitud = document.createElement("p");
      parrafoMagnitud.textContent =
        "Magnitud: " + sismo.magnitud + " (" + sismo.magnitud_descripcion + ").";
      item.appendChild(parrafoMagnitud);

      var parrafoEnlace = document.createElement("p");
      var enlace = document.createElement("a");
      enlace.href = sismo.url_detalle;
      enlace.textContent = "Más información sobre el sismo en " + sismo.lugar + ", en el sitio del USGS";
      parrafoEnlace.appendChild(enlace);
      item.appendChild(parrafoEnlace);

      lista.appendChild(item);
    });
    return lista;
  }

  function mostrarErrorFetch() {
    var alerta = document.createElement("div");
    alerta.setAttribute("role", "alert");
    alerta.setAttribute("tabindex", "-1");
    alerta.textContent =
      "No se pudo completar la búsqueda por un problema de conexión. Intenta de nuevo.";
    contenedorResultados.innerHTML = "";
    contenedorResultados.appendChild(alerta);
    alerta.focus();
  }

  // Mientras el usuario no haya editado el campo de ubicación, se usan las
  // coordenadas detectadas (respaldo técnico, oculto) en vez de re-geocodificar
  // el texto del lugar detectado. Apenas el usuario escribe su propia ciudad,
  // esta función deja de enviar las coordenadas y prioriza el texto escrito.
  function construirParametrosBusqueda() {
    var parametros = new URLSearchParams(new FormData(formulario));
    if (!ubicacionModificadaPorUsuario) {
      parametros.delete("ciudad");
    }
    return parametros;
  }

  function ejecutarBusqueda(parametros) {
    parametros.set("formato", "json");

    estadoBusqueda.textContent = "Buscando sismos…";

    fetch(formulario.action + "?" + parametros.toString())
      .then(function (respuesta) {
        return respuesta.json();
      })
      .then(function (datos) {
        if (datos.estado === "error") {
          estadoBusqueda.textContent = "";
          mostrarErrorFetch();
          var alertaMensaje = contenedorResultados.querySelector('[role="alert"]');
          if (alertaMensaje) {
            alertaMensaje.textContent = datos.mensaje;
          }
          return;
        }
        contenedorResultados.innerHTML = "";
        contenedorResultados.appendChild(crearElementoResultados(datos));
        estadoBusqueda.textContent =
          datos.total === 1
            ? "Se encontró 1 resultado."
            : "Se encontraron " + datos.total + " resultados.";
      })
      .catch(function () {
        estadoBusqueda.textContent = "";
        mostrarErrorFetch();
      });
  }

  if (formulario) {
    formulario.addEventListener("submit", function (evento) {
      evento.preventDefault();
      ejecutarBusqueda(construirParametrosBusqueda());
    });
  }
});
