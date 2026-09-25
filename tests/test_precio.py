"""Tests de convertir_precio SIN internet: sustituimos la API real por una respuesta falsa (mock).

En la CI no queremos depender de que Frankfurter este caido o de que el tipo de cambio cambie cada dia.
"""

import asyncio

import httpx

import server


def respuesta_falsa(peticion: httpx.Request) -> httpx.Response:
    # Simula a Frankfurter: siempre 1 EUR = 1.10 USD
    return httpx.Response(200, json={"date": "2026-01-01", "rates": {"USD": 1.10}})


def test_convierte_con_el_tipo_de_la_api(monkeypatch):
    transporte = httpx.MockTransport(respuesta_falsa)
    cliente_original = httpx.AsyncClient
    monkeypatch.setattr(server.httpx, "AsyncClient", lambda **kw: cliente_original(transport=transporte, **kw))
    resultado = asyncio.run(server.convertir_precio(10, "usd"))
    assert resultado == "10.00 EUR = 11.00 USD (tipo 1.1, BCE 2026-01-01)"


def test_moneda_no_soportada_no_llama_a_la_api():
    # La validacion va ANTES de la peticion: 'bitcoin' se rechaza sin tocar la red
    assert "no soportada" in asyncio.run(server.convertir_precio(10, "bitcoin"))


def test_importe_negativo():
    assert "mayor que cero" in asyncio.run(server.convertir_precio(-5, "USD"))
