import requests
from flask import current_app

from app.servicios.errores import (
    ErrorConexion,
    ErrorRespuestaInvalida,
    ErrorTiempoAgotado,
)


def solicitar_json(
    url,
    parametros=None,
    headers=None,
    timeout=None,
    metodo="GET",
    json_cuerpo=None,
    codigos_aceptados=(),
):
    """Único punto del proyecto que hace llamadas HTTP salientes.

    Centraliza el timeout y la traducción de errores de red a mensajes en
    español, para que ningún servicio (USGS, Nominatim, mindicador.cl,
    Blindmachine) tenga que repetir el mismo manejo de excepciones.

    codigos_aceptados permite tratar ciertos códigos de error HTTP (por
    ejemplo 404) como respuestas válidas: en ese caso se devuelve el JSON
    del cuerpo en vez de lanzar ErrorRespuestaInvalida.
    """
    timeout = timeout or current_app.config["TIMEOUT_APIS_EXTERNAS"]
    try:
        respuesta = requests.request(
            metodo,
            url,
            params=parametros,
            headers=headers,
            json=json_cuerpo,
            timeout=timeout,
        )
        if respuesta.status_code not in codigos_aceptados:
            respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.Timeout as error:
        current_app.logger.warning(f"Timeout consultando {url}: {error!r}")
        raise ErrorTiempoAgotado(
            "El servicio externo tardó demasiado en responder. Intenta de nuevo en unos minutos."
        )
    except requests.exceptions.ConnectionError as error:
        current_app.logger.warning(f"ConnectionError consultando {url}: {error!r}")
        raise ErrorConexion(
            "No se pudo conectar con el servicio externo. Revisa tu conexión a internet."
        )
    except requests.exceptions.HTTPError as error:
        codigo = error.response.status_code if error.response is not None else "desconocido"
        current_app.logger.warning(f"HTTPError consultando {url}: {error!r}")
        raise ErrorRespuestaInvalida(
            f"El servicio externo respondió con un error (código {codigo})."
        )
    except ValueError as error:
        current_app.logger.warning(f"ValueError consultando {url}: {error!r}")
        raise ErrorRespuestaInvalida(
            "El servicio externo devolvió una respuesta que no se pudo interpretar."
        )
