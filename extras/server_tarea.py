"""Variacion: disena la tool para la TAREA del usuario, no para cada endpoint.

Mismo servidor + una tool que resuelve 'importe de mi pedido en otra moneda' en una sola llamada.
Asi el LLM no tiene que encadenar dos tools (llama3.1 las pidio en paralelo y fallo).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import consultar_pedido, convertir_precio, log, mcp  # noqa: E402


@mcp.tool()
async def importe_pedido_en(numero: str, moneda: str) -> str:
    """Dice el importe de un pedido convertido a otra moneda (USD, GBP, JPY, CHF, MXN o BRL).

    Args:
        numero: numero de pedido de 4 cifras, por ejemplo "1234"
        moneda: codigo ISO de la moneda destino, por ejemplo "USD"
    """
    pedido = consultar_pedido(numero)
    if "error" in pedido:
        return pedido["error"]
    log.info("importe_pedido_en(%s, %s)", numero, moneda)
    return await convertir_precio(pedido["importe_eur"], moneda)


if __name__ == "__main__":
    mcp.run()
