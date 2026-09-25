# mcp-server-ci · Sesión 11: CI/CD y monitorización

[![CI](https://github.com/ignaciothepower/mcp-server-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/ignaciothepower/mcp-server-ci/actions/workflows/ci.yml)

**Repositorio:** https://github.com/ignaciothepower/mcp-server-ci
**Ejecuciones de la CI:** https://github.com/ignaciothepower/mcp-server-ci/actions

El servidor MCP de la tienda de la Sesión 10 (`convertir_precio`, `consultar_pedido` y el resource `tienda://politica-devoluciones`), llevado a producción: tests, linting, CI en GitHub Actions, secretos fuera del código, logging estructurado y monitorización con LangFuse.

## Instalar y probar en local

```bash
git clone https://github.com/ignaciothepower/mcp-server-ci.git
cd mcp-server-ci
python -m venv .venv
.venv\Scripts\activate          # en Mac/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt

ruff check .                    # linting: errores y malas prácticas (incluida seguridad, reglas S)
ruff format --check .           # formato
pytest -v                       # 8 tests: sin internet y sin LLM
```

## Cómo corren los tests

| Fichero | Qué prueba | Por qué así |
|---|---|---|
| `tests/test_pedidos.py` | `consultar_pedido`: caso feliz, limpieza de `#`, formato inválido, pedido inexistente | Lógica pura: rápidos y los que más protegen |
| `tests/test_precio.py` | `convertir_precio` con la API **simulada** (`httpx.MockTransport`) | La CI no puede depender de que una API externa responda |
| `tests/test_servidor.py` | Conecta por MCP **en memoria** y comprueba tools y resource | Es lo que ve un host como Claude Code |

## Qué hace el workflow de CI (`.github/workflows/ci.yml`)

En **cada push y cada pull request a `main`**, GitHub arranca máquinas limpias (Ubuntu) y ejecuta:

1. **Job `calidad`**, dos veces (matriz de Python 3.10 y 3.12): checkout → Python con caché de pip → `pip install` → `ruff check` → `ruff format --check` → `pytest`.
2. **Job `secretos`** (solo si `calidad` pasa): comprueba con `scripts/check_langfuse.py` que las claves llegan desde GitHub Secrets y que LangFuse las acepta.

Si un paso falla, el check sale en rojo ✗ y GitHub lo avisa en el commit (y por email). Con `fail-fast` (el valor por defecto), si una versión de la matriz falla se cancela la otra.

## Cómo se gestionan los secretos

- **Nunca** hay claves en el código. `config.py` las lee del entorno.
- **En local:** copia `.env.example` como `.env` y pon tus claves. `.env` está en `.gitignore`: compruébalo con `git check-ignore -v .env`.
- **En la CI:** *Settings → Secrets and variables → Actions*. Pestaña **Secrets** (datos sensibles, cifrados y enmascarados `***` en los logs): `LANGFUSE_PUBLIC_KEY` y `LANGFUSE_SECRET_KEY`. Pestaña **Variables** (configuración no sensible, en claro): `LANGFUSE_HOST`. El workflow los inyecta como variables de entorno.
- `ruff` (regla **S105**) avisa si alguien escribe una clave en el código.
- **Regla de oro:** si una clave llega a Git, está comprometida → **rótala** (genera una nueva y borra la vieja). Borrar el commit no basta.

## Cómo se monitoriza

- **Logs estructurados** (`logs.py`): una línea JSON por evento a **stderr** (stdout es del protocolo MCP), con `ts`, `nivel`, `evento`, `tool` y `ms`.
- **Trazas con LangFuse** (`host_ollama.py`): cada pregunta es una traza con una *generation* por llamada al LLM (tokens y latencia) y un *tool* por cada tool MCP.
  ```bash
  python host_ollama.py "¿Cuándo llega mi pedido 1234?"   # necesita Ollama con llama3.1 y tu .env
  ```
  En la clase, la traza tardó 56,5 s en total: 56,3 s del modelo y 0,01 s de la tool; 582 tokens; coste 0 $ porque el modelo es local.

## Checklist: listo para producción

- [x] Tests que pasan en verde (`pytest`, 8 tests, sin red)
- [x] Linting y formato automáticos (`ruff check` + `ruff format --check`)
- [x] CI en cada push y PR (GitHub Actions, matriz 3.10/3.12)
- [x] Secretos fuera del código (`.env` en `.gitignore` + GitHub Secrets)
- [x] Logging estructurado a stderr (JSON)
- [x] Monitorización del LLM: trazas, tokens, latencia y coste (LangFuse)
- [ ] Despliegue automático (CD) → Sesión 12

## Estructura

```
server.py                 Servidor MCP (Sesión 10) con logging JSON
logs.py                   Formato JSON para los logs
config.py                 Lee las claves del entorno (.env / Secrets)
host_ollama.py            Host MCP con llama3.1 + trazas en LangFuse
scripts/check_langfuse.py Smoke test de secretos (lo usa la CI)
tests/                    pytest
.github/workflows/ci.yml  El workflow de CI
.env.example              Plantilla de secretos (sin claves reales)
soluciones/               Ejercicios de la Sesión 10
```

## Sesión 12 · Desplegar en la nube (AWS)

El mismo servidor, ahora por **HTTP** dentro de un contenedor Docker en una máquina EC2. En local sigue siendo STDIO; en la nube, `MCP_TRANSPORT=http` (ya viene en el `Dockerfile`).

```bash
docker build -t mcp-server .                 # imagen de ~198 MB
docker run -d -p 8000:8000 mcp-server        # servidor MCP en http://localhost:8000/mcp
curl http://localhost:8000/salud             # {"estado":"ok",...}
python cliente_http.py http://IP-DE-LA-EC2:8000
```

**En AWS** (desde **AWS CloudShell**, sin crear access keys): `aws/desplegar.sh` hace todo lo de la clase y `aws/apagar.sh` lo borra y comprueba que el gasto queda a cero.

| Pieza | En este proyecto |
|---|---|
| **IAM** | Usuario administrador para el día a día; la cuenta *root* solo para facturación (y con MFA) |
| **Budget** | Alerta de 5 USD/mes: email al 80 % real y al 100 % previsto |
| **VPC / security group** | Nada de `0.0.0.0/0`: el puerto 22 solo desde CloudShell y el 8000 solo desde tu IP |
| **EC2** | `t3.micro` (Free Tier) con Amazon Linux 2023 e IMDSv2 obligatorio |
| **S3** | Bucket privado (bloqueo de acceso público por defecto) y un enlace firmado de 5 minutos para compartir un fichero |

### Checklist: apaga todo

- [ ] `aws ec2 terminate-instances` y esperar a `terminated` (el disco se borra con ella)
- [ ] Borrar el security group y el par de claves
- [ ] `aws s3 rb s3://BUCKET --force`
- [ ] Comprobar a 0: instancias, discos EBS, IPs elásticas, snapshots y buckets (`bash aws/apagar.sh` lo hace)
- [ ] Revisar *Billing* al día siguiente (los costes tardan unas horas en aparecer)

En la clase: la t3.micro estuvo encendida unos 30 minutos (**menos de 1 céntimo**) y todo quedó a cero.

### Alternativa sin tarjeta: Render o Railway

No ejecutado en clase. Los dos leen el `Dockerfile` del repositorio:

1. Crea una cuenta gratuita con tu GitHub y elige *New Web Service* (Render) o *New Project → Deploy from GitHub repo* (Railway).
2. Selecciona este repositorio; detectan el `Dockerfile` solos.
3. Variables: `MCP_TRANSPORT=http` (ya está en el Dockerfile) y el puerto que te indique la plataforma en `PORT`.
4. Te dan una URL pública con HTTPS: `curl https://TU-APP/salud`.

Ojo: en el plan gratuito el servicio se duerme tras un rato sin uso y tarda unos segundos en despertar.
