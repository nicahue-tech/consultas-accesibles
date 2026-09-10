import os
import smtplib
from email.message import EmailMessage


def leer_credenciales_correo():
    remitente = os.environ.get("CORREO_REMITENTE")
    clave_app = os.environ.get("CORREO_CLAVE_APP")
    if not remitente or not clave_app:
        raise RuntimeError(
            "Faltan las variables de entorno CORREO_REMITENTE y/o CORREO_CLAVE_APP"
        )
    return {"remitente": remitente, "clave_app": clave_app}


def enviar_correo_contacto(nombre_remitente, correo_remitente, telefono, mensaje):
    # Mismo mecanismo que usa Blindmachine: credenciales de una cuenta Gmail
    # con clave de aplicación, destino fijo (la casilla de contacto) y el
    # remitente del formulario en Reply-To, para poder responderle directo.
    credenciales = leer_credenciales_correo()

    mensaje_correo = EmailMessage()
    mensaje_correo["Subject"] = "Nuevo mensaje de contacto - Consultas Accesibles"
    mensaje_correo["From"] = credenciales["remitente"]
    mensaje_correo["To"] = "contacto@blindmachine.cl"
    mensaje_correo["Reply-To"] = correo_remitente

    cuerpo = (
        f"Nombre: {nombre_remitente}\n"
        f"Correo: {correo_remitente}\n"
        f"Teléfono: {telefono if telefono else 'No proporcionado'}\n\n"
        f"Mensaje:\n{mensaje}\n"
    )
    mensaje_correo.set_content(cuerpo)

    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
        servidor.starttls()
        servidor.login(credenciales["remitente"], credenciales["clave_app"])
        servidor.send_message(mensaje_correo)
