from flask import current_app

from app.servicios.cliente_http import solicitar_json

URL_NOMINATIM = "https://nominatim.openstreetmap.org/search"
URL_NOMINATIM_REVERSO = "https://nominatim.openstreetmap.org/reverse"

_MAPA_TILDES = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")


def _quitar_tildes(texto):
    """Quita solo las tildes de las vocales, sin tocar la eñe.

    Necesario porque Safari filtra las opciones del datalist comparando
    letra por letra contra lo escrito, sin reconocer que "a" y "á" son la
    misma letra: si el nombre real lleva tilde y la persona escribe sin
    tilde (como es normal al escribir rápido), la sugerencia queda oculta
    aunque el servidor sí la haya encontrado.
    """
    return texto.translate(_MAPA_TILDES)


class ErrorUbicacionNoEncontrada(Exception):
    """No es un error de red: la ciudad, lugar o coordenada simplemente no se encontró."""


def geocodificar(consulta):
    datos = solicitar_json(
        URL_NOMINATIM,
        parametros={"format": "json", "q": consulta, "limit": 1},
        headers={"User-Agent": current_app.config["CONTACTO_USER_AGENT"]},
    )
    if not datos:
        raise ErrorUbicacionNoEncontrada(
            "No se encontró esa ciudad o lugar. Verifica la ortografía o intenta con otro nombre de lugar."
        )
    resultado = datos[0]
    return float(resultado["lat"]), float(resultado["lon"]), resultado["display_name"]


def buscar_sugerencias(consulta, limite=8):
    headers = {"User-Agent": current_app.config["CONTACTO_USER_AGENT"]}

    # Dos consultas: una acotada a Chile (para que "Santiago" o "Los Ángeles"
    # prioricen el lugar chileno) y otra sin restricción de país, para no
    # perder lugares fuera de Chile. Se hacen una después de otra, no en
    # simultáneo, para respetar el límite de una solicitud por segundo de
    # la política de uso de Nominatim.
    datos_chile = solicitar_json(
        URL_NOMINATIM,
        parametros={"format": "json", "q": consulta, "limit": limite, "countrycodes": "cl"},
        headers=headers,
    ) or []
    datos_generales = solicitar_json(
        URL_NOMINATIM,
        parametros={"format": "json", "q": consulta, "limit": limite},
        headers=headers,
    ) or []

    sugerencias = []
    nombres_vistos = set()
    for resultado in datos_chile + datos_generales:
        nombre = _quitar_tildes(resultado["display_name"])
        if nombre in nombres_vistos:
            continue
        nombres_vistos.add(nombre)
        sugerencias.append(nombre)
        if len(sugerencias) >= limite:
            break
    return sugerencias


def geocodificar_inverso(lat, lon):
    datos = solicitar_json(
        URL_NOMINATIM_REVERSO,
        parametros={"format": "jsonv2", "lat": lat, "lon": lon},
        headers={"User-Agent": current_app.config["CONTACTO_USER_AGENT"]},
    )
    if not datos or "display_name" not in datos:
        raise ErrorUbicacionNoEncontrada(
            "No se pudo determinar un nombre de lugar para esas coordenadas."
        )
    return datos["display_name"]
