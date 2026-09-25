"""Servidor MCP de la tienda (Sesion 10) con logging estructurado en JSON a stderr (Sesion 11)."""

import os
import time

import httpx

# mcp 2.x: la clase se llama MCPServer (en la 1.x era FastMCP, from mcp.server.fastmcp)
from mcp.server.mcpserver import MCPServer
from starlette.requests import Request
from starlette.responses import JSONResponse

import logs

# REGLA DE ORO en STDIO: stdout es el canal JSON-RPC. Todo lo demas, a stderr (en JSON, ver logs.py).
log = logs.configurar("mi-servidor")

# La instancia del servidor: el nombre es lo que vera el host (Claude Code, VS Code...)
mcp = MCPServer("mi-servidor")

# Base de datos de juguete: los mismos pedidos del agente de soporte de la Sesion 2
PEDIDOS = {
    "1234": {"estado": "enviado", "transportista": "SEUR", "llegada": "jueves", "importe_eur": 49.90},
    "5678": {"estado": "en preparacion", "transportista": "-", "llegada": "la semana que viene", "importe_eur": 120.00},
}
MONEDAS = {"USD", "GBP", "JPY", "CHF", "MXN", "BRL"}


# ---- Paso 2 · primera tool: una API publica sin clave (Frankfurter, tipos del BCE) ----
@mcp.tool()
async def convertir_precio(importe_eur: float, moneda: str) -> str:
    """Convierte un importe en euros a otra moneda con el tipo de cambio oficial del BCE de hoy.

    Args:
        importe_eur: cantidad en euros, por ejemplo 49.90
        moneda: codigo ISO de la moneda destino: USD, GBP, JPY, CHF, MXN o BRL
    """
    moneda = moneda.strip().upper()
    if moneda not in MONEDAS:
        return f"Error: moneda '{moneda}' no soportada. Usa una de: {', '.join(sorted(MONEDAS))}"
    if importe_eur <= 0:
        return "Error: el importe debe ser mayor que cero"
    t0 = time.perf_counter()
    url = f"https://api.frankfurter.dev/v1/latest?from=EUR&to={moneda}"
    async with httpx.AsyncClient(timeout=10) as cliente:
        r = await cliente.get(url)
        r.raise_for_status()
        datos = r.json()
    tipo = datos["rates"][moneda]
    ms = round((time.perf_counter() - t0) * 1000)
    log.info("tool_ok", extra={"campos": {"tool": "convertir_precio", "moneda": moneda, "ms": ms}})
    return f"{importe_eur:.2f} EUR = {importe_eur * tipo:.2f} {moneda} (tipo {tipo}, BCE {datos['date']})"


# ---- Paso 4 · segunda tool con validacion (reutiliza consulta_pedido de la S2) ----
@mcp.tool()
def consultar_pedido(numero: str) -> dict:
    """Devuelve el estado, el transportista, el dia de llegada y el importe en euros de un pedido.

    Args:
        numero: numero de pedido de 4 cifras, por ejemplo "1234"
    """
    numero = numero.strip().lstrip("#")
    if not (numero.isdigit() and len(numero) == 4):
        log.warning("entrada_invalida", extra={"campos": {"tool": "consultar_pedido", "numero": numero}})
        return {"error": "El numero de pedido debe tener 4 cifras, por ejemplo 1234"}
    log.info("tool_ok", extra={"campos": {"tool": "consultar_pedido", "numero": numero}})
    return PEDIDOS.get(numero, {"error": f"No existe el pedido {numero}"})


# ---- Paso 4 · resource de solo lectura, identificado por una URI ----
@mcp.resource("tienda://politica-devoluciones")
def politica_devoluciones() -> str:
    """Politica de devoluciones de la tienda (texto plano, solo lectura)."""
    log.info("resource_leido", extra={"campos": {"uri": "tienda://politica-devoluciones"}})
    with open(__file__.replace("server.py", "datos/politica_devoluciones.txt"), encoding="utf-8") as f:
        return f.read()


# ---- Sesion 12 · en la nube: una ruta HTTP normal para comprobar que el servidor esta vivo ----
@mcp.custom_route("/salud", methods=["GET"])
async def salud(request: Request) -> JSONResponse:
    """Health check: lo que mira un balanceador (o tu navegador) para saber si el servidor responde."""
    return JSONResponse({"estado": "ok", "servidor": "mi-servidor", "tools": ["convertir_precio", "consultar_pedido"]})


if __name__ == "__main__":
    # En local (Claude Code, tests): STDIO. En la nube (Docker, EC2): HTTP, porque el cliente esta en otra maquina.
    transporte = os.environ.get("MCP_TRANSPORT", "stdio")
    log.info("arranque", extra={"campos": {"transporte": transporte}})
    if transporte == "http":
        # 0.0.0.0 = escuchar en todas las interfaces: obligatorio dentro de un contenedor.
        # Quien decide quien entra NO es el codigo, es el security group de AWS (el cortafuegos).
        mcp.run("streamable-http", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))  # noqa: S104
    else:
        mcp.run()  # transporte por defecto: stdio
