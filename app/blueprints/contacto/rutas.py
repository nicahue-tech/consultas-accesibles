from flask import Blueprint, flash, redirect, render_template, url_for

from app.blueprints.contacto.formularios import FormularioContacto
from app.servicios.correo import enviar_correo_contacto

blueprint_contacto = Blueprint("contacto", __name__)


@blueprint_contacto.route("/", methods=["GET", "POST"])
def index():
    formulario = FormularioContacto()

    if formulario.validate_on_submit():
        try:
            enviar_correo_contacto(
                formulario.nombre.data.strip(),
                formulario.correo.data.strip(),
                formulario.telefono.data.strip() if formulario.telefono.data else "",
                formulario.mensaje.data.strip(),
            )
        except Exception as error:
            print(
                f"Error al enviar correo de contacto de {formulario.nombre.data.strip()} "
                f"({formulario.correo.data.strip()}): {error}"
            )
            flash(
                "No se pudo enviar el mensaje. Intenta de nuevo más tarde.",
                "error",
            )
            return render_template("contacto/index.html", formulario=formulario)

        return redirect(url_for("contacto.gracias"))

    return render_template("contacto/index.html", formulario=formulario)


@blueprint_contacto.route("/gracias")
def gracias():
    return render_template("contacto/gracias.html")
