"""Cliente MCP por HTTP (Sesion 12): habla con el servidor aunque este en otra maquina, por ejemplo en AWS.

Uso:  python cliente_http.py http://IP-DE-LA-EC2:8000
Hace lo mismo que Claude Code o nuestro host: initialize -> tools/list -> tools/call -> resources/read.
"""

import asyncio
import sys
import time

from mcp.client import Client


async def main(base: str) -> None:
    url = base.rstrip("/") + "/mcp"
    t0 = time.perf_counter()
    async with Client(url) as mcp:  # una URL en lugar de un comando: transporte Streamable HTTP
        print(f"conectado a {url} en {(time.perf_counter() - t0) * 1000:.0f} ms")
        tools = [t.name for t in (await mcp.list_tools()).tools]
        print(f"tools/list      -> {tools}")
        for nombre, args in [
            ("consultar_pedido", {"numero": "1234"}),
            ("convertir_precio", {"importe_eur": 49.9, "moneda": "USD"}),
        ]:
            t1 = time.perf_counter()
            res = await mcp.call_tool(nombre, args)
            texto = " ".join(c.text for c in res.content if getattr(c, "text", None)).replace("\n", " ")
            print(f"tools/call      -> {nombre}({args}) = {texto}  [{(time.perf_counter() - t1) * 1000:.0f} ms]")
        politica = await mcp.read_resource("tienda://politica-devoluciones")
        print(f"resources/read  -> {politica.contents[0].text.splitlines()[1]}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"))
