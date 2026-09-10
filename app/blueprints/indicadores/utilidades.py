MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}

NOMBRES_UNIDAD = {
    "clp": "pesos chilenos",
    "uf": "UF",
    "utm": "UTM",
    "dolar": "dólares",
}

NOMBRES_TASA = {
    "uf": "el valor de la UF",
    "utm": "el valor de la UTM",
    "dolar": "el valor del dólar observado",
}


def formatear_fecha_legible(fecha_date):
    """Evita depender del locale del servidor para nombres de mes en español."""
    return f"{fecha_date.day} de {MESES[fecha_date.month]} de {fecha_date.year}"


def formatear_numero(valor):
    """Redondea a 2 decimales y recorta ceros sobrantes, sin separador de miles."""
    texto = f"{round(valor, 2):.2f}"
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto


def formatear_indicadores_para_mostrar(valores_indicadores):
    """Convierte {"uf": {"valor": ..., "fecha": ...} | None, ...} en un dict
    con el mismo número ya formateado como texto (o None si no hay dato),
    para que la plantilla lo muestre igual en las tres filas de la tabla."""
    return {
        clave: formatear_numero(indicador["valor"]) if indicador else None
        for clave, indicador in valores_indicadores.items()
    }


def _valor_en_pesos_por_unidad(unidad, valores_indicadores):
    if unidad == "clp":
        return 1

    indicador = valores_indicadores.get(unidad)
    if indicador is None:
        raise ValueError(
            f"No se puede convertir porque {NOMBRES_TASA[unidad]} no está disponible "
            "para la fecha consultada."
        )
    return indicador["valor"]


def convertir_moneda(monto, desde, hacia, valores_indicadores):
    """Convierte monto de la unidad desde a la unidad hacia, pasando por pesos
    chilenos como intermedio, salvo que ambas unidades sean la misma."""
    if desde == hacia:
        return monto

    pesos_por_desde = _valor_en_pesos_por_unidad(desde, valores_indicadores)
    pesos_por_hacia = _valor_en_pesos_por_unidad(hacia, valores_indicadores)

    monto_en_pesos = monto * pesos_por_desde
    return monto_en_pesos / pesos_por_hacia


def construir_frase_resultado(monto, desde, hacia, resultado, es_hoy, fecha_legible, valores_indicadores):
    monto_texto = formatear_numero(monto)
    resultado_texto = formatear_numero(resultado)
    nombre_desde = NOMBRES_UNIDAD[desde]
    nombre_hacia = NOMBRES_UNIDAD[hacia]

    if desde == hacia:
        return (
            f"{monto_texto} {nombre_desde} es el mismo monto que {resultado_texto} "
            f"{nombre_hacia}: no se necesita ninguna conversión."
        )

    momento = "de hoy" if es_hoy else f"del {fecha_legible}"

    unidades_con_tasa = [unidad for unidad in (desde, hacia) if unidad != "clp"]
    clausulas_tasa = []
    for unidad in unidades_con_tasa:
        valor = formatear_numero(valores_indicadores[unidad]["valor"])
        clausulas_tasa.append(f"{NOMBRES_TASA[unidad]} {momento}, ${valor}")

    return (
        f"{monto_texto} {nombre_desde} equivalen a {resultado_texto} {nombre_hacia}, "
        f"según {' y '.join(clausulas_tasa)}."
    )
