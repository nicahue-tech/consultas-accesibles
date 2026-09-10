from app.servicios.cliente_http import solicitar_json

URL_BASE_MINDICADOR = "https://mindicador.cl/api"

CLAVES_INDICADORES = ("uf", "utm", "dolar")


def obtener_indicadores(fecha=None):
    """Consulta UF, UTM y dólar observado.

    Si fecha es None, un único llamado a /api trae el valor de hoy de los
    tres indicadores. Si se pasa un objeto date, mindicador.cl no ofrece un
    endpoint combinado por fecha: hay que consultar cada indicador por
    separado en /api/{indicador}/{dd-mm-yyyy}, cuya respuesta trae una
    "serie" vacía cuando no hay dato para ese día exacto (por ejemplo el
    dólar observado los fines de semana). Ese caso se traduce a None, que la
    plantilla muestra como "No disponible".
    """
    if fecha is None:
        datos = solicitar_json(URL_BASE_MINDICADOR)
        indicadores = {}
        for clave in CLAVES_INDICADORES:
            indicador = datos.get(clave)
            if indicador is None or indicador.get("valor") is None:
                indicadores[clave] = None
            else:
                indicadores[clave] = {
                    "valor": indicador["valor"],
                    "fecha": indicador.get("fecha"),
                }
        return indicadores

    fecha_texto = fecha.strftime("%d-%m-%Y")
    indicadores = {}
    for clave in CLAVES_INDICADORES:
        datos = solicitar_json(f"{URL_BASE_MINDICADOR}/{clave}/{fecha_texto}")
        serie = datos.get("serie") or []
        if not serie or serie[0].get("valor") is None:
            indicadores[clave] = None
        else:
            indicadores[clave] = {
                "valor": serie[0]["valor"],
                "fecha": serie[0].get("fecha"),
            }
    return indicadores
