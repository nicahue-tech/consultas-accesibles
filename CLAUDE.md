# Convenciones del proyecto

## Leyenda de transparencia sobre APIs externas

Todo módulo que consulte una API externa (como Sismos consultando USGS, o
Indicadores consultando mindicador.cl) debe incluir, cerca del final de su
página, una sección `<h2>Sobre estos datos</h2>` seguida de un párrafo que:

- indique la fuente real de los datos (el nombre del servicio o entidad que
  los provee), y
- aclare si esa fuente es oficial o de un tercero independiente, y
- advierta explícitamente que, al ser un servicio de terceros, la consulta
  puede fallar o demorar por razones fuera de nuestro control.

Este texto es estático e informativo, no dinámico: no necesita
`aria-live`, solo texto plano legible dentro del flujo normal de la página.

Ver `app/templates/sismos/index.html` y `app/templates/indicadores/index.html`
como referencia del formato exacto a seguir.

## Obligatoriedad de campos en formularios

El texto que indica si un campo es obligatorio u opcional (por ejemplo
"(obligatorio)" o "(campo opcional)") siempre debe ir dentro del propio
texto de la etiqueta `<label>` del campo, nunca como texto suelto entre el
cierre de `</label>` y el `<input>` (u otro control). Si queda fuera del
`label`, VoiceOver lo anuncia como una parada aparte al navegar linealmente,
antes de llegar al campo editable.

En los formularios construidos con Flask-WTF, esto se logra incluyendo el
texto directamente en la definición del campo (el primer argumento del
`StringField`, `TextAreaField`, etc. en el archivo `formularios.py` del
blueprint correspondiente), nunca agregándolo en la plantilla junto a
`{{ formulario.campo.label }}`.

Ver `app/blueprints/contacto/formularios.py` como referencia.
