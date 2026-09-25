# Sesión 11 · CI/CD y monitorización en producción · Prompts para Claude Code

Estos son los prompts que usamos en la práctica, en el mismo orden que en clase. Cópialos y pégalos en Claude Code uno a uno.

**Cómo usarlos**
1. Pega el prompt del paso y deja que Claude Code proponga los cambios.
2. **Lee el código antes de aceptar** (y los comandos, como `pip install`, antes de permitirlos).
3. Ejecuta y compara con el apartado *Qué deberías ver*.
4. Si no sale lo esperado, vuelve a pedírselo con lo que has aprendido.

> Antes de empezar: el servidor MCP de la Sesión 10, Git instalado, una cuenta gratuita de [GitHub](https://github.com/signup) y tus claves de LangFuse Cloud de la Sesión 3 en un `.env` (tienes la plantilla en `.env.example`; **nunca subas tu `.env`**). Repositorio de referencia de la clase, público: https://github.com/ignaciothepower/mcp-server-ci (sus ejecuciones: https://github.com/ignaciothepower/mcp-server-ci/actions).

El resultado de referencia, con todo el código comentado, está en la carpeta `mcp-server-ci` del material de la sesión.

---

## Paso 1 · Preparar el proyecto con tests y linting

**Qué construye**

- Partimos del servidor MCP de la S10
- ruff: linting + formato en una herramienta
- pytest: 8 tests sin red ni LLM
- Todo en verde en local antes de subir nada

**Prompt**

```text
Toma el servidor MCP de la Sesion 10. Configura ruff en pyproject.toml (line-length 120 y reglas E, W, F, I, B y S de seguridad) y pasalo con ruff check y ruff format --check. Arregla lo que encuentre (ruff check --fix y ruff format) y justifica con noqa lo que decidas mantener. Luego anade una carpeta tests/ con pytest: tests de consultar_pedido (caso feliz, limpieza de '#', formato invalido, pedido inexistente), de convertir_precio SIN internet usando httpx.MockTransport, y uno de integracion que conecte con el servidor por MCP en memoria y compruebe sus tools y su resource. Ejecutalos en local y explica cada test con un comentario didactico.
```

**Qué deberías ver**

Mi propio codigo de la S10 tenia 8 avisos y 6 ficheros sin formatear. Uno era real: un import que sobraba.

### Variación en vivo: Variación · rompemos el codigo a proposito

```text
Rompe a proposito consultar_pedido quitando el .lstrip('#') y ejecuta pytest. Ensename que test falla, como leer el informe de pytest (la linea con >, el KeyError y el WARNING capturado) y despues restaura el codigo.
```

**Qué demuestra**

El test de la almohadilla lo pilla al instante: '#5678' ya no se encuentra. 1 failed, 7 passed. El bug no llega a nadie.

---

## Paso 2 · Primer workflow de CI con GitHub Actions

**Qué construye**

- ci.yml: se dispara en cada push y PR
- Matriz: Python 3.10 y 3.12
- ruff + pytest en una maquina Ubuntu limpia
- github.com/ignaciothepower/mcp-server-ci

**Prompt**

```text
Crea un workflow de GitHub Actions en .github/workflows/ci.yml que se dispare en cada push y pull request a main. Debe: instalar Python con actions/setup-python (en una matriz 3.10 y 3.12), cachear las dependencias de pip, instalar requirements-dev.txt, pasar ruff check y ruff format --check y ejecutar pytest. Usa las versiones actuales de las actions. Explica la estructura workflow / jobs / steps con comentarios y como leer el resultado en la pestana Actions. Luego ayudame a crear el repositorio en GitHub y a subir el codigo con git push.
```

**Qué deberías ver**

Verde a la primera: 2 jobs en 42 s. Y un aviso: checkout@v4 usa Node.js 20, que esta obsoleto.

---

## Paso 3 · Gestionar los secretos correctamente

**Qué construye**

- Las claves de LangFuse (las de la S3) a .env
- .env en .gitignore: Git no lo ve
- config.py las lee del entorno
- Comprobacion: LangFuse acepta las claves

**Prompt**

```text
Refactoriza el proyecto para que ninguna credencial este escrita en el codigo: crea config.py que cargue un .env con python-dotenv y lea LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY y LANGFUSE_HOST del entorno, anade .env al .gitignore y crea un .env.example sin claves reales. Anade scripts/check_langfuse.py que compruebe que las variables existen y que LangFuse las acepta, mostrando las claves enmascaradas. Comprueba con git check-ignore que .env no se subira. Recalca por que una clave en Git ya esta comprometida.
```

**Qué deberías ver**

.env no aparece en git status: .gitignore lo protege. Y el script nunca imprime una clave entera: sk-lf-****.

### Variación en vivo: Variación · ¿y si alguien escribe la clave en el codigo?

```text
Crea un fichero de prueba con una clave inventada escrita en el codigo (LANGFUSE_SECRET_KEY = 'sk-lf-...') y pasale ruff. Explicame la regla S105 y por que tenerla en la CI es una red de seguridad. Luego borra el fichero.
```

**Qué demuestra**

Ruff lo marca con S105: 'Possible hardcoded password'. Como ruff corre en la CI, ese push saldria en rojo antes de llegar a main.

---

## Paso 4 · Añadir logging estructurado y monitorizacion

**Qué construye**

- logs.py: una linea JSON por evento
- Siempre a stderr: stdout es de MCP
- Campos: ts, nivel, evento, tool, ms
- LangFuse para las llamadas al LLM

**Prompt**

```text
Anade logging estructurado al servidor: un logs.py con un Formatter que escriba cada evento como una linea JSON (ts, nivel, servicio, evento y campos extra como tool y ms) en stderr, porque stdout es el canal de MCP. Mide la latencia de la llamada a la API. Despues integra LangFuse en host_ollama.py: una traza por pregunta, una generation por cada llamada a llama3.1 con sus tokens (prompt_eval_count y eval_count) y latencia, y un observation de tipo tool por cada tool MCP. Ejecutalo una vez y ensename que aparece en el dashboard.
```

**Qué deberías ver**

La tool que llama a la API tardo 101 ms. El '12a' queda como WARNING con su campo numero.

---

## Paso 5 · Pipeline completo y checklist de produccion

**Qué construye**

- push -> calidad (x2) -> secretos
- README: tests, CI, secretos y monitorizacion
- Badge 'passing' en la portada
- github.com/ignaciothepower/mcp-server-ci

**Prompt**

```text
Repasa el pipeline completo de punta a punta y escribe un README que documente: como instalarlo y correr los tests, que hace el workflow de CI (jobs calidad y secretos), como se gestionan los secretos (.env, Secrets y Variables) y como se monitoriza (logs JSON y LangFuse). Anade el badge de la CI, los enlaces al repositorio y a Actions, y un checklist de 'listo para produccion' (tests, linting, secretos fuera del codigo, logging, monitorizacion). Deja el proyecto listo para compartir como material de clase.
```

**Qué deberías ver**

El badge de la CI en el README se actualiza solo: cualquiera ve si el proyecto esta en verde.

---

## Ejercicio 1 · Pon tu proyecto en verde

**Qué construye**

- 2 tests con pytest
- Claves a .env
- ci.yml con ruff + pytest
- Check en verde en Actions

**Prompt**

```text
Coge un proyecto Python pequeno (por ejemplo el servidor MCP de la Sesion 10). Anade dos tests con pytest, configura ruff, mueve cualquier clave a un .env (con .gitignore y un .env.example sin claves reales) y crea .github/workflows/ci.yml para que GitHub Actions pase ruff y los tests en cada push. Ayudame a crear el repositorio en GitHub, subirlo y comprobar que el check sale en verde en la pestana Actions.
```

**Qué deberías ver**

Un check verde en la pestana Actions y el badge 'passing' en tu README.

---

## Ejercicio 2 · Reto: lleva tu proyecto a produccion

**Qué construye**

- Tests + CI en verde
- Secretos bien gestionados
- Logging estructurado
- Monitorizacion + README

**Prompt**

```text
Lleva tu proyecto a produccion: tests con pytest, un workflow de CI en GitHub Actions que pase ruff y los tests en verde, ninguna clave en el codigo (.env en local y GitHub Secrets en la CI, con un job que compruebe que las claves llegan), logging estructurado en JSON a stderr con niveles y, si el proyecto usa un LLM, monitorizacion con LangFuse (trazas con tokens y latencia). Escribe un README con el badge de la CI y un checklist de 'listo para produccion'.
```

**Qué deberías ver**

Todos los jobs de la CI en verde, la traza en LangFuse y el README con el checklist.

---

*Material del Master AI Engineer · The Power · Ignacio de Pastors*
