"""Ejercicio 2 (reto) · Solucion: 2 tools + 1 resource + validacion + logging a stderr.

Un 'cuaderno de notas' que el asistente puede escribir, buscar y leer. Se guarda en notas.json.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from mcp.server.mcpserver import MCPServer

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="[notas] %(levelname)s %(message)s")
log = logging.getLogger("notas")
mcp = MCPServer("notas")
FICHERO = Path(__file__).with_name("notas.json")


def _cargar() -> list[dict]:
    return json.loads(FICHERO.read_text(encoding="utf-8")) if FICHERO.exists() else []


@mcp.tool()
def guardar_nota(titulo: str, texto: str) -> str:
    """Guarda una nota nueva en el cuaderno. Tiene EFECTOS: escribe en disco.

    Args:
        titulo: titulo corto de la nota (maximo 60 caracteres)
        texto: contenido de la nota (maximo 1000 caracteres)
    """
    titulo, texto = titulo.strip(), texto.strip()
    if not titulo or len(titulo) > 60:
        return "Error: el titulo es obligatorio y debe tener como maximo 60 caracteres"
    if not texto or len(texto) > 1000:
        return "Error: el texto es obligatorio y debe tener como maximo 1000 caracteres"
    notas = _cargar()
    notas.append({"titulo": titulo, "texto": texto, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")})
    FICHERO.write_text(json.dumps(notas, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("guardar_nota(%r) -> %d notas", titulo, len(notas))
    return f"Nota '{titulo}' guardada. Ahora hay {len(notas)} notas."


@mcp.tool()
def buscar_notas(palabra: str) -> list[dict]:
    """Busca notas cuyo titulo o texto contengan una palabra (sin distinguir mayusculas).

    Args:
        palabra: palabra a buscar, minimo 3 letras
    """
    palabra = palabra.strip().lower()
    if len(palabra) < 3:
        return [{"error": "La palabra debe tener al menos 3 letras"}]
    encontradas = [n for n in _cargar() if palabra in (n["titulo"] + " " + n["texto"]).lower()]
    log.info("buscar_notas(%r) -> %d", palabra, len(encontradas))
    return encontradas


@mcp.resource("notas://todas")
def todas_las_notas() -> str:
    """Todas las notas del cuaderno en JSON (solo lectura)."""
    return json.dumps(_cargar(), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
