import os

import requests

from app.servicios.errores import (
    ErrorConexion,
    ErrorRespuestaInvalida,
    ErrorTiempoAgotado,
)

TIMEOUT_RELAY_CORREO = 10


def leer_credenciales_relay():
    url = os.environ.get("RELAY_CORREO_URL")
    clave = os.environ.get("RELAY_CORREO_CLAVE")
    if not url or not clave:
        raise RuntimeError(
            "Faltan las variables de entorno RELAY_CORREO_URL y/o RELAY_CORREO_CLAVE"
        )
    return {"url": url, "clave": clave}


def enviar_correo_contacto(nombre_remitente, correo_remitente, telefono, mensaje):
    # El envío real ya no lo hace este proyecto: se le pide a Blindmachine,
    # que sí puede usar SMTP directo porque está en un plan de pago, a
    # través de su endpoint interno de relay de correo.
    credenciales = leer_credenciales_relay()

    cuerpo = {
        "origen": "Consultas Accesibles",
        "nombre": nombre_remitente,
        "correo": correo_remitente,
        "telefono": telefono,
        "mensaje": mensaje,
    }

    try:
        respuesta = requests.post(
            credenciales["url"],
            json=cuerpo,
            headers={"X-Relay-Key": credenciales["clave"]},
            timeout=TIMEOUT_RELAY_CORREO,
        )
    except requests.exceptions.Timeout:
        raise ErrorTiempoAgotado(
            "El servicio de envío de correo tardó demasiado en responder. Intenta de nuevo en unos minutos."
        )
    except requests.exceptions.ConnectionError:
        raise ErrorConexion(
            "No se pudo conectar con el servicio de envío de correo. Revisa tu conexión a internet."
        )

    if respuesta.status_code != 200:
        raise ErrorRespuestaInvalida(
            f"El servicio de envío de correo respondió con un error (código {respuesta.status_code})."
        )
