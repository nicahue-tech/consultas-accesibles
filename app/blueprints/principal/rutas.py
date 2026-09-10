from flask import Blueprint, render_template

blueprint_principal = Blueprint("principal", __name__)


@blueprint_principal.route("/")
def inicio():
    return render_template("principal/inicio.html")
