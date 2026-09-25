"""Host MCP minimo (Sesion 10) + MONITORIZACION con LangFuse (Sesion 11).

Cada pregunta = una TRAZA en LangFuse, con dentro:
  - una GENERATION por cada llamada al LLM (modelo, entrada, salida, tokens y latencia)
  - un TOOL por cada tool MCP ejecutada (argumentos, resultado y si fue error)
Las claves de LangFuse se leen del entorno (.env en local, Secrets en la CI): ver config.py.
Uso: python host_ollama.py "pregunta"
"""

import asyncio
import json
import sys
import time

import httpx
from langfuse import get_client, propagate_attributes
from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

import config  # noqa: F401  (carga el .env)

MODELO = "llama3.1"
OLLAMA = "http://localhost:11434/api/chat"
SERVIDOR = "server.py"  # o extras/server_tarea.py (variacion de la Sesion 10)
SYSTEM = "Eres el asistente de una tienda online. Responde en espanol, breve. Usa las herramientas cuando haga falta."

langfuse = get_client()


async def main(pregunta: str) -> None:
    servidor = StdioServerParameters(command=sys.executable, args=[SERVIDOR])
    async with Client(servidor) as mcp:
        tools = (await mcp.list_tools()).tools
        print(f"[host] servidor conectado: {len(tools)} tools -> {[t.name for t in tools]}")
        herramientas = [
            {
                "type": "function",
                "function": {"name": t.name, "description": t.description, "parameters": t.input_schema},
            }
            for t in tools
        ]
        mensajes = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": pregunta}]
        print(f"Tu: {pregunta}")

        # TRAZA: la peticion completa del usuario
        with langfuse.start_as_current_observation(as_type="span", name="atender-cliente", input=pregunta) as traza:
            with propagate_attributes(user_id="alumno-demo", session_id="s11-demo", tags=["s11", "mcp", MODELO]):
                respuesta = await bucle(mcp, herramientas, mensajes)
            traza.update(output=respuesta)
            langfuse.set_current_trace_as_public()  # demo de clase: la traza se puede ver sin login
            print(f"[langfuse] traza: {langfuse.get_trace_url()}")
    langfuse.flush()  # enviar todo antes de salir


async def bucle(mcp, herramientas, mensajes) -> str:
    async with httpx.AsyncClient(timeout=300) as http:
        for vuelta in range(4):  # tope de vueltas: nunca un bucle infinito
            # GENERATION: una llamada al modelo, con sus tokens y su latencia
            with langfuse.start_as_current_observation(
                as_type="generation", name=f"llm-vuelta-{vuelta + 1}", model=MODELO, input=mensajes[1:]
            ) as gen:
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
                datos = r.json()
                msg = datos["message"]
                tokens = {"input": datos.get("prompt_eval_count", 0), "output": datos.get("eval_count", 0)}
                gen.update(output=msg, usage_details=tokens, cost_details={"total": 0.0})  # local: coste 0
            print(f"[llm] vuelta {vuelta + 1} ({time.time() - t0:.0f} s, tokens {tokens['input']}+{tokens['output']})")
            mensajes.append(msg)
            if not msg.get("tool_calls"):
                print(f"Asistente: {msg['content']}")
                return msg["content"]
            for llamada in msg["tool_calls"]:
                nombre, args = llamada["function"]["name"], llamada["function"]["arguments"]
                print(f"  [host] tools/call -> {nombre}({json.dumps(args, ensure_ascii=False)})")
                # TOOL: la ejecucion de una tool en el servidor MCP
                with langfuse.start_as_current_observation(as_type="tool", name=nombre, input=args) as span:
                    res = await mcp.call_tool(nombre, args)
                    texto = "\n".join(c.text for c in res.content if getattr(c, "text", None))
                    span.update(output=texto, level="ERROR" if res.is_error else "DEFAULT")
                print(f"  [servidor] <- {texto}")
                mensajes.append({"role": "tool", "content": texto, "tool_name": nombre})
    return "(sin respuesta: se alcanzo el tope de vueltas)"


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "Cuando llega mi pedido 1234?"))
