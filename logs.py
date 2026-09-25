"""Logging estructurado: una linea JSON por evento, siempre a stderr (stdout es del protocolo MCP).

Un log en JSON lo puede filtrar y agregar una maquina (Grafana, Datadog, CloudWatch...):
"dame todos los WARNING de consultar_pedido de hoy" o "latencia media de convertir_precio".
"""

import json
import logging
import sys
from datetime import datetime, timezone


class FormatoJSON(logging.Formatter):
    def format(self, registro: logging.LogRecord) -> str:
        evento = {
            "ts": datetime.fromtimestamp(registro.created, tz=timezone.utc).isoformat(timespec="milliseconds"),
            "nivel": registro.levelname,
            "servicio": registro.name,
            "evento": registro.getMessage(),
        }
        evento.update(getattr(registro, "campos", {}))  # campos extra: tool, ms, error...
        return json.dumps(evento, ensure_ascii=False)


def configurar(nombre: str, nivel: int = logging.INFO) -> logging.Logger:
    manejador = logging.StreamHandler(sys.stderr)
    manejador.setFormatter(FormatoJSON())
    raiz = logging.getLogger()
    raiz.handlers[:] = [manejador]
    raiz.setLevel(nivel)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # sin el ruido de cada peticion HTTP
    return logging.getLogger(nombre)
