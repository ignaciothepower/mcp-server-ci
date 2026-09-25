# Imagen del servidor MCP de la tienda (Sesion 12). Pequena: Python 3.12 "slim" + solo lo necesario.
FROM python:3.12-slim

WORKDIR /app

# 1) Primero las dependencias: si no cambian, Docker reutiliza esta capa y el build tarda segundos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Despues el codigo
COPY server.py logs.py config.py ./
COPY datos/ datos/

# En la nube el servidor habla HTTP (en local, STDIO)
ENV MCP_TRANSPORT=http PORT=8000
EXPOSE 8000

# Nunca como root dentro del contenedor
RUN useradd --create-home app
USER app

CMD ["python", "server.py"]
