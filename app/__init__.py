from flask import Flask

from config import Config


def crear_aplicacion():
    aplicacion = Flask(__name__, instance_relative_config=True)
    aplicacion.config.from_object(Config)

    @aplicacion.context_processor
    def inyectar_modulos():
        from app.registro_modulos import MODULOS

        modulos_registrados = [
            modulo for modulo in MODULOS
            if modulo["endpoint"] in aplicacion.view_functions
        ]
        return {"modulos_disponibles": modulos_registrados}

    from app.blueprints.principal.rutas import blueprint_principal
    from app.blueprints.sismos.rutas import blueprint_sismos
    from app.blueprints.indicadores.rutas import blueprint_indicadores
    from app.blueprints.contacto.rutas import blueprint_contacto

    aplicacion.register_blueprint(blueprint_principal)
    aplicacion.register_blueprint(blueprint_sismos, url_prefix="/sismos")
    aplicacion.register_blueprint(blueprint_indicadores, url_prefix="/indicadores")
    aplicacion.register_blueprint(blueprint_contacto, url_prefix="/contacto")

    return aplicacion
