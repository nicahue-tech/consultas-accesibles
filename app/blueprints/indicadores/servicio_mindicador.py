import os
from datetime import date

from flask import current_app

from app.servicios.cliente_http import solicitar_json
from app.servicios.errores import ErrorRelayInvalido

URL_BASE_MINDICADOR = "https://mindicador.cl/api"

CLAVES_INDICADORES = ("uf", "utm", "dolar")

FUENTE_MINDICADOR = "mindicador.cl"


def _configuracion_relay():
    url = os.environ.get("RELAY_INDICADORES_URL")
    clave = os.environ.get("RELAY_INDICADORES_CLAVE")
    if not url or not clave:
        current_app.logger.error("Faltan RELAY_INDICADORES_URL o RELAY_INDICADORES_CLAVE")
        raise ErrorRelayInvalido("El servicio de historial de indicadores no está configurado.")
    return url.rstrip("/"), {"X-Relay-Key": clave}


def consultar_en_relay(codigo, fecha):
    """Pregunta a Blindmachine si ya hay un valor guardado.

    Devuelve {"valor", "fecha", "fuente"} si existe, o None si no existe
    (404 con {"existe": false}).
    """
    url, headers = _configuracion_relay()
    datos = solicitar_json(
        f"{url}/consultar",
        parametros={"codigo": codigo, "fecha": fecha.isoformat()},
        headers=headers,
        codigos_aceptados=(404,),
    )
    if datos.get("existe") is True and datos.get("valor") is not None:
        return {"valor": datos["valor"], "fecha": datos.get("fecha"), "fuente": datos.get("fuente")}
    if datos.get("existe") is False:
        return None
    raise ErrorRelayInvalido("El servicio de historial de indicadores respondió en un formato inesperado.")


def guardar_en_relay(codigo, fecha, valor, fuente):
    url, headers = _configuracion_relay()
    datos = solicitar_json(
        f"{url}/guardar",
        headers=headers,
        metodo="POST",
        json_cuerpo={
            "codigo": codigo,
            "fecha": fecha.isoformat(),
            "valor": valor,
            "fuente": fuente,
        },
    )
    if datos.get("ok") is not True:
        raise ErrorRelayInvalido("El servicio de historial de indicadores no confirmó el guardado.")


def obtener_valor_desde_fuente_externa(codigo, fecha):
    """Punto único de integración con la fuente real de los datos.

    Devuelve (valor, fuente), o None si la fuente no tiene dato para esa
    fecha exacta (por ejemplo el dólar observado un fin de semana).

    Hoy la fuente es mindicador.cl, que no ofrece un endpoint combinado por
    fecha: se consulta /api/{indicador}/{dd-mm-yyyy}, cuya "serie" viene
    vacía cuando no hay dato. Para migrar al Banco Central basta con
    reemplazar el cuerpo de esta función, manteniendo la misma firma y el
    mismo formato de retorno; el resto del flujo no cambia.
    """
    fecha_texto = fecha.strftime("%d-%m-%Y")
    datos = solicitar_json(f"{URL_BASE_MINDICADOR}/{codigo}/{fecha_texto}")
    serie = datos.get("serie") or []
    if not serie or serie[0].get("valor") is None:
        return None
    return serie[0]["valor"], FUENTE_MINDICADOR


def obtener_indicador(codigo, fecha):
    """Flujo completo para un indicador y fecha: relay, fuente externa, guardado.

    Devuelve {"valor", "fecha"} o None si no hay dato para ese día.
    """
    guardado = consultar_en_relay(codigo, fecha)
    if guardado is not None:
        return {"valor": guardado["valor"], "fecha": guardado["fecha"]}

    resultado = obtener_valor_desde_fuente_externa(codigo, fecha)
    if resultado is None:
        return None
    valor, fuente = resultado

    guardar_en_relay(codigo, fecha, valor, fuente)
    return {"valor": valor, "fecha": fecha.isoformat()}


def obtener_indicadores(fecha=None):
    """Consulta UF, UTM y dólar observado para una fecha (hoy si es None).

    Un indicador sin dato para ese día se devuelve como None, que la
    plantilla muestra como "No disponible".
    """
    fecha = fecha or date.today()
    return {clave: obtener_indicador(clave, fecha) for clave in CLAVES_INDICADORES}
