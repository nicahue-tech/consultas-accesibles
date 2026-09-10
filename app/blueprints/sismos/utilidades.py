MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}


def clasificar_profundidad(km):
    """<70 km superficial, 70-300 km intermedio, >300 km profundo."""
    if km < 70:
        return "superficial"
    if km <= 300:
        return "intermedio"
    return "profundo"


def clasificar_magnitud(magnitud):
    """Rangos estándar de la escala de magnitud de momento."""
    if magnitud < 5.0:
        return "leve"
    if magnitud < 6.0:
        return "moderado"
    if magnitud < 7.0:
        return "fuerte"
    return "muy fuerte"


def formatear_fecha_legible(fecha_dt):
    """Evita depender del locale del servidor para nombres de mes en español."""
    return (
        f"{fecha_dt.day} de {MESES[fecha_dt.month]} de {fecha_dt.year}, "
        f"{fecha_dt.strftime('%H:%M')}"
    )
