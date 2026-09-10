class ErrorConsultaExterna(Exception):
    """Excepción base para fallas al consultar una API externa.

    El atributo mensaje_usuario ya viene redactado en español, listo para
    mostrarse directamente en un bloque de alerta accesible.
    """

    def __init__(self, mensaje_usuario):
        self.mensaje_usuario = mensaje_usuario
        super().__init__(mensaje_usuario)


class ErrorTiempoAgotado(ErrorConsultaExterna):
    pass


class ErrorConexion(ErrorConsultaExterna):
    pass


class ErrorRespuestaInvalida(ErrorConsultaExterna):
    pass
