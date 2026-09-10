from flask import Blueprint, flash, jsonify, render_template, request

from app.blueprints.sismos.servicio_geocodificacion import (
    ErrorUbicacionNoEncontrada,
    buscar_sugerencias,
    geocodificar,
    geocodificar_inverso,
)
from app.blueprints.sismos.servicio_usgs import buscar_sismos
from app.servicios.errores import ErrorConsultaExterna

blueprint_sismos = Blueprint("sismos", __name__)


@blueprint_sismos.route("/")
def index():
    return render_template("sismos/index.html", resultados=None, ubicacion_legible=None,
                            valores_formulario={})


@blueprint_sismos.route("/buscar")
def buscar():
    ciudad = request.args.get("ciudad", "").strip()
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    radio_km = request.args.get("radio_km", default=200, type=int)
    magnitud_min_raw = request.args.get("magnitud_min", default="4")
    rango_tiempo = request.args.get("rango_tiempo", default="dia")
    formato = request.args.get("formato")

    magnitud_min = None if magnitud_min_raw == "todas" else float(magnitud_min_raw)

    ubicacion_legible = None
    resultados = None
    mensaje_error = None

    try:
        if ciudad:
            lat, lon, ubicacion_legible = geocodificar(ciudad)
        elif lat is None or lon is None:
            raise ValueError("Debes indicar una ciudad o lugar, o ingresar latitud y longitud.")

        resultados = buscar_sismos(lat, lon, radio_km, magnitud_min, rango_tiempo)
    except ErrorUbicacionNoEncontrada as error:
        mensaje_error = str(error)
    except ErrorConsultaExterna as error:
        mensaje_error = error.mensaje_usuario
    except ValueError as error:
        mensaje_error = str(error)

    if formato == "json":
        return jsonify(
            estado="error" if mensaje_error else "ok",
            mensaje=mensaje_error,
            ubicacion_legible=ubicacion_legible,
            resultados=resultados or [],
            total=len(resultados) if resultados else 0,
        ), (502 if mensaje_error else 200)

    if mensaje_error:
        flash(mensaje_error, "error")

    return render_template(
        "sismos/index.html",
        resultados=resultados,
        ubicacion_legible=ubicacion_legible,
        valores_formulario=request.args,
    )


@blueprint_sismos.route("/sugerencias-ubicacion")
def sugerencias_ubicacion():
    consulta = request.args.get("q", "").strip()
    if len(consulta) < 3:
        return jsonify(sugerencias=[])

    try:
        sugerencias = buscar_sugerencias(consulta)
    except ErrorConsultaExterna:
        sugerencias = []

    return jsonify(sugerencias=sugerencias)


@blueprint_sismos.route("/ubicacion-legible")
def ubicacion_legible():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if lat is None or lon is None:
        return jsonify(estado="error", mensaje="Debes indicar latitud y longitud."), 400

    try:
        lugar = geocodificar_inverso(lat, lon)
        return jsonify(estado="ok", ubicacion_legible=lugar)
    except ErrorUbicacionNoEncontrada as error:
        return jsonify(estado="error", mensaje=str(error))
    except ErrorConsultaExterna as error:
        return jsonify(estado="error", mensaje=error.mensaje_usuario), 502
