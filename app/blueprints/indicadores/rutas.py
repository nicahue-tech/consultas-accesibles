from datetime import date, datetime

from flask import Blueprint, flash, jsonify, render_template, request

from app.blueprints.indicadores.servicio_mindicador import obtener_indicadores
from app.blueprints.indicadores.utilidades import (
    construir_frase_resultado,
    convertir_moneda,
    formatear_fecha_legible,
    formatear_indicadores_para_mostrar,
)
from app.servicios.errores import ErrorConsultaExterna

blueprint_indicadores = Blueprint("indicadores", __name__)

UNIDADES_VALIDAS = {"clp", "uf", "utm", "dolar"}


@blueprint_indicadores.route("/")
def index():
    try:
        indicadores = obtener_indicadores()
        mensaje_error = None
    except ErrorConsultaExterna as error:
        indicadores = {"uf": None, "utm": None, "dolar": None}
        mensaje_error = error.mensaje_usuario

    if mensaje_error:
        flash(mensaje_error, "error")

    return render_template(
        "indicadores/index.html",
        indicadores=formatear_indicadores_para_mostrar(indicadores),
        fecha_legible=None,
        es_hoy=True,
        valores_formulario={},
        resultado_conversion=None,
    )


@blueprint_indicadores.route("/consultar")
def consultar():
    fecha_texto = request.args.get("fecha", "").strip()
    monto_texto = request.args.get("monto", "").strip()
    desde = request.args.get("desde", "")
    hacia = request.args.get("hacia", "")
    formato = request.args.get("formato")

    fecha = None
    es_hoy = True
    mensaje_error = None
    indicadores = None
    resultado_conversion = None
    error_conversion = None

    if fecha_texto:
        try:
            fecha = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        except ValueError:
            mensaje_error = "La fecha ingresada no es válida."
        else:
            es_hoy = fecha == date.today()

    if mensaje_error is None:
        try:
            indicadores = obtener_indicadores(fecha)
        except ErrorConsultaExterna as error:
            mensaje_error = error.mensaje_usuario

    if mensaje_error is None and monto_texto and desde in UNIDADES_VALIDAS and hacia in UNIDADES_VALIDAS:
        try:
            monto = float(monto_texto)
            resultado = convertir_moneda(monto, desde, hacia, indicadores)
            fecha_legible = formatear_fecha_legible(fecha) if fecha else None
            resultado_conversion = construir_frase_resultado(
                monto, desde, hacia, resultado, es_hoy, fecha_legible, indicadores
            )
        except ValueError as error:
            error_conversion = str(error)

    if formato == "json":
        if mensaje_error:
            return jsonify(estado="error", mensaje=mensaje_error), 502
        return jsonify(
            estado="ok",
            indicadores=formatear_indicadores_para_mostrar(indicadores),
            fecha_legible=formatear_fecha_legible(fecha) if fecha else None,
            es_hoy=es_hoy,
            resultado_conversion=resultado_conversion,
            error_conversion=error_conversion,
        )

    if mensaje_error:
        flash(mensaje_error, "error")
        indicadores = {"uf": None, "utm": None, "dolar": None}
    elif error_conversion:
        flash(error_conversion, "error")

    return render_template(
        "indicadores/index.html",
        indicadores=formatear_indicadores_para_mostrar(indicadores),
        fecha_legible=formatear_fecha_legible(fecha) if fecha else None,
        es_hoy=es_hoy,
        valores_formulario=request.args,
        resultado_conversion=resultado_conversion,
    )
