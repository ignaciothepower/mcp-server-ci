"""Configuracion: TODAS las credenciales se leen del entorno, ninguna esta escrita en el codigo.

En local vienen de un fichero .env (que esta en .gitignore); en GitHub Actions, de los Secrets del repositorio.
"""

import os

from dotenv import load_dotenv

load_dotenv()  # si existe .env lo carga; si no (en la CI), no pasa nada: se usan las variables ya definidas

NECESARIAS = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST")


def faltan() -> list[str]:
    """Nombres de las variables que no estan definidas (nunca sus valores)."""
    return [n for n in NECESARIAS if not os.environ.get(n)]


def enmascarar(valor: str) -> str:
    """Para los logs: 'sk-lf-1a2b...' -> 'sk-lf-****'. Jamas se imprime una clave entera."""
    return valor[:6] + "****" if valor else "(vacia)"
