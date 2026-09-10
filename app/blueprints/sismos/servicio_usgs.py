from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.blueprints.sismos.utilidades import (
    clasificar_magnitud,
    clasificar_profundidad,
    formatear_fecha_legible,
)
from app.servicios.cliente_http import solicitar_json

URL_USGS = "https://earthquake.usgs.gov/fdsnws/event/1/query"

DURACION_RANGO = {
    "hora": timedelta(hours=1),
    "dia": timedelta(days=1),
    "semana": timedelta(days=7),
    "mes": timedelta(days=30),
}


def buscar_sismos(latitud, longitud, radio_km, magnitud_min, rango_tiempo):
    ahora = datetime.now(timezone.utc)
    delta = DURACION_RANGO.get(rango_tiempo, DURACION_RANGO["dia"])

    parametros = {
        "format": "geojson",
        "starttime": (ahora - delta).isoformat(),
        "endtime": ahora.isoformat(),
        "latitude": latitud,
        "longitude": longitud,
        "maxradiuskm": radio_km,
        "orderby": "time",
    }
    if magnitud_min is not None:
        parametros["minmagnitude"] = magnitud_min

    datos = solicitar_json(URL_USGS, parametros=parametros)

    resultados = []
    for feature in datos.get("features", []):
        propiedades = feature["properties"]
        _, _, profundidad = feature["geometry"]["coordinates"]
        fecha_dt = datetime.fromtimestamp(
            propiedades["time"] / 1000, tz=ZoneInfo("America/Santiago")
        )
        resultados.append({
            "id": feature["id"],
            "lugar": propiedades["place"],
            "magnitud": propiedades["mag"],
            "magnitud_descripcion": clasificar_magnitud(propiedades["mag"]),
            "profundidad_km": round(profundidad, 1),
            "profundidad_descripcion": clasificar_profundidad(profundidad),
            "fecha_hora_legible": formatear_fecha_legible(fecha_dt),
            "url_detalle": propiedades["url"],
        })
    return resultados
