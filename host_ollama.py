"""Un HOST MCP minimo: llama3.1 (Ollama, local) usando las tools de nuestro servidor.

Es lo que hace Claude Code por dentro, en ~50 lineas:
  1) arranca el servidor por STDIO y pide tools/list
  2) pasa esas definiciones (inputSchema) al LLM como herramientas
  3) si el LLM pide una tool -> tools/call al servidor -> devuelve el resultado al LLM
Uso: uv run python host_ollama.py "pregunta"
"""

import asyncio
import json
import sys
import time

import httpx
from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

MODELO = "llama3.1"
OLLAMA = "http://localhost:11434/api/chat"
SERVIDOR = "server.py"  # o extras/server_tarea.py (variacion)


async def main(pregunta: str) -> None:
    servidor = StdioServerParameters(command=sys.executable, args=[SERVIDOR])
    async with Client(servidor) as mcp:
        tools = (await mcp.list_tools()).tools
        print(f"[host] servidor conectado: {len(tools)} tools -> {[t.name for t in tools]}")
        # El inputSchema que genero el SDK ES el formato de function calling del LLM
        herramientas = [
            {
                "type": "function",
                "function": {"name": t.name, "description": t.description, "parameters": t.input_schema},
            }
            for t in tools
        ]
        mensajes = [
            {
                "role": "system",
                "content": "Eres el asistente de una tienda online. Responde en espanol, breve. "
                "Usa las herramientas cuando haga falta. "
                "Si la pregunta tiene varias partes, usa una herramienta para cada parte "
                "antes de responder (p. ej. primero el pedido y luego convertir su importe).",
            },
            {"role": "user", "content": pregunta},
        ]
        print(f"Tu: {pregunta}")
        async with httpx.AsyncClient(timeout=300) as http:
            for vuelta in range(4):  # tope de vueltas: nunca un bucle infinito
                t0 = time.time()
                r = await http.post(
                    OLLAMA,
                    json={
                        "model": MODELO,
                        "messages": mensajes,
                        "tools": herramientas,
                        "stream": False,
                        "keep_alive": 0,
                        "options": {"temperature": 0, "num_predict": 200},
                    },
                )
                msg = r.json()["message"]
                print(f"[llm] vuelta {vuelta + 1} ({time.time() - t0:.0f} s)")
                mensajes.append(msg)
                if not msg.get("tool_calls"):
                    print(f"Asistente: {msg['content']}")
                    return
                for llamada in msg["tool_calls"]:
                    nombre, args = llamada["function"]["name"], llamada["function"]["arguments"]
                    print(f"  [host] tools/call -> {nombre}({json.dumps(args, ensure_ascii=False)})")
                    res = await mcp.call_tool(nombre, args)
                    texto = "\n".join(c.text for c in res.content if getattr(c, "text", None))
                    print(f"  [servidor] <- {texto}")
                    mensajes.append({"role": "tool", "content": texto, "tool_name": nombre})


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--servidor":
        SERVIDOR = sys.argv[2]
        del sys.argv[1:3]
    asyncio.run(main(" ".join(sys.argv[1:]) or "Cuando llega mi pedido 1234 y cuanto es su importe en dolares?"))
