import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambiar-esta-clave-en-produccion")
    TIMEOUT_APIS_EXTERNAS = int(os.environ.get("TIMEOUT_APIS_EXTERNAS", "8"))
    CONTACTO_USER_AGENT = os.environ.get(
        "CONTACTO_USER_AGENT",
        "ConsultasAccesibles/1.0 (contacto: nicahue@gmail.com)",
    )
