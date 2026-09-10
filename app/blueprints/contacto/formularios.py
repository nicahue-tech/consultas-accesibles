from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional


class FormularioContacto(FlaskForm):
    nombre = StringField(
        "Nombre (obligatorio)",
        validators=[DataRequired(message="El nombre es obligatorio")],
    )
    correo = StringField(
        "Correo electrónico (obligatorio)",
        validators=[
            DataRequired(message="El correo electrónico es obligatorio"),
            Email(message="Ese correo no parece válido"),
        ],
    )
    telefono = StringField("Teléfono (campo opcional)", validators=[Optional()])
    mensaje = TextAreaField(
        "Mensaje (obligatorio)",
        validators=[DataRequired(message="El mensaje es obligatorio")],
    )
    enviar = SubmitField("Enviar mensaje")
