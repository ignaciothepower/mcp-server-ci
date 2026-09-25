"""Tests de consultar_pedido: logica pura, sin red. Son los mas rapidos y los que mas protegen."""

from server import consultar_pedido


def test_pedido_existente_devuelve_su_estado():
    # El caso feliz: el pedido 1234 de la Sesion 2 esta enviado con SEUR
    pedido = consultar_pedido("1234")
    assert pedido["estado"] == "enviado"
    assert pedido["transportista"] == "SEUR"


def test_limpia_la_almohadilla_y_los_espacios():
    # Los usuarios (y los modelos) escriben "#5678": la tool debe entenderlo igual
    assert consultar_pedido("  #5678 ")["estado"] == "en preparacion"


def test_formato_invalido_devuelve_error_util():
    # '12a' no son 4 cifras: esperamos un mensaje que explique COMO arreglarlo, no una excepcion
    assert "4 cifras" in consultar_pedido("12a")["error"]


def test_pedido_inexistente():
    assert consultar_pedido("9999") == {"error": "No existe el pedido 9999"}
