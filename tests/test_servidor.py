"""Test de integracion: hablamos con el servidor por MCP (en memoria, sin subprocesos) como lo haria un host."""

import asyncio

from mcp.client import Client

from server import mcp


async def descubrir():
    async with Client(mcp) as cliente:  # conexion en proceso: initialize + list, igual que Claude Code
        tools = [t.name for t in (await cliente.list_tools()).tools]
        politica = await cliente.read_resource("tienda://politica-devoluciones")
        return tools, politica.contents[0].text


def test_el_servidor_expone_sus_tools_y_su_resource():
    tools, politica = asyncio.run(descubrir())
    assert sorted(tools) == ["consultar_pedido", "convertir_precio"]
    assert "30 dias" in politica
