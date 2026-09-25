"""Ejercicio 1 (basico) · Solucion: servidor MCP con UNA tool util (Open-Meteo, API publica sin clave)."""

import logging
import sys

import httpx
from mcp.server.mcpserver import MCPServer

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="[tiempo] %(levelname)s %(message)s")
log = logging.getLogger("tiempo")
mcp = MCPServer("tiempo")

CIUDADES = {
    "madrid": (40.42, -3.70),
    "barcelona": (41.39, 2.17),
    "sevilla": (37.39, -5.99),
    "valencia": (39.47, -0.38),
    "bilbao": (43.26, -2.93),
}


@mcp.tool()
async def tiempo_actual(ciudad: str) -> str:
    """Devuelve la temperatura (C) y el viento (km/h) actuales de una ciudad espanola.

    Args:
        ciudad: Madrid, Barcelona, Sevilla, Valencia o Bilbao
    """
    clave = ciudad.strip().lower()
    if clave not in CIUDADES:
        return f"Error: ciudad no soportada. Usa una de: {', '.join(c.title() for c in CIUDADES)}"
    lat, lon = CIUDADES[clave]
    log.info("tiempo_actual(%s)", clave)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
    async with httpx.AsyncClient(timeout=10) as cliente:
        r = await cliente.get(url)
        r.raise_for_status()
        actual = r.json()["current"]
    return (
        f"{ciudad.title()}: {actual['temperature_2m']} C, viento {actual['wind_speed_10m']} km/h ({actual['time']} UTC)"
    )


if __name__ == "__main__":
    mcp.run()
