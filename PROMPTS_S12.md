# Sesión 12 · Cloud Deployment: fundamentos de la nube · Prompts para Claude Code

Estos son los prompts que usamos en la práctica, en el mismo orden que en clase. Cópialos y pégalos en Claude Code uno a uno.

**Cómo usarlos**
1. Pega el prompt del paso y deja que Claude Code proponga los cambios.
2. **Lee el código antes de aceptar** (y los comandos, como `pip install`, antes de permitirlos).
3. Ejecuta y compara con el apartado *Qué deberías ver*.
4. Si no sale lo esperado, vuelve a pedírselo con lo que has aprendido.

> Antes de empezar: una cuenta en el proveedor de nube que elijas, con su **plan gratuito** o capa gratuita (no cobra salvo que pases al plan de pago; suele pedir tarjeta para verificar) o, si no quieres tarjeta, una cuenta gratuita de Render o Railway. Todo se hace desde **la terminal web de la consola** (la que se abre en el navegador), sin instalar nada ni crear claves de acceso. Código del servidor: https://github.com/ignaciothepower/mcp-server-ci. Los scripts de despliegue y apagado (`nube/desplegar.sh` y `nube/apagar.sh`) los genera el asistente para tu proveedor; **léelos antes de ejecutarlos**. **Al terminar, apaga todo** (`bash nube/apagar.sh`).

El resultado de referencia, con todo el código comentado, está en la carpeta `mcp-server-ci` del material de la sesión.

---

## Paso 1 · Cuenta en la capa gratuita, seguridad y CLI

**Qué construye**

- La CLI del proveedor en la terminal web de la consola: ya viene instalada
- ¿Con quién estoy trabajando? (identidad actual)
- Alerta de presupuesto: 5 USD al mes
- Usuario de trabajo (no root): lo crea el dueño de la cuenta

**Prompt**

```text
Guíame para: 1) comprobar con la CLI de mi proveedor de nube con qué identidad estoy trabajando y explicarme por qué no debo usar la cuenta root en el día a día. 2) crear en la consola de mi proveedor de nube, en la gestión de identidades y permisos, un usuario de trabajo (no root) con permisos de administrador para usarlo en lugar de root, y activar MFA tanto en root como en ese usuario. 3) crear con la CLI del proveedor una alerta de presupuesto de 5 USD al mes que me avise por email al 80 % del gasto real y al 100 % del previsto. Usa la terminal web de la consola (la que se abre en el navegador) para no tener que crear claves de acceso. Explica cada paso de seguridad. Si el alumno prefiere no dar tarjeta, dame la alternativa equivalente en Render o Railway.
```

**Qué deberías ver**

La identidad que devuelve la CLI es la de root: recién creada la cuenta, trabajas con la llave maestra. Justo lo que no hay que hacer.

---

## Paso 2 · Lanzar una máquina virtual y conectarse

**Qué construye**

- Cortafuegos: solo las IPs que hacen falta
- Par de claves: la privada nunca se imprime
- La máquina virtual más pequeña de la capa gratuita, con el Linux que ofrece el proveedor
- SSH desde la terminal web de la consola

**Prompt**

```text
Explícame paso a paso cómo lanzar con la CLI de mi proveedor de nube una máquina virtual del tamaño más pequeño incluido en la capa gratuita, con el Linux que ofrece el proveedor y en la región más cercana: la elección de la imagen, el par de claves y el cortafuegos. El cortafuegos solo debe abrir el puerto 22 a la IP de la terminal web de la consola y el 8000 a la IP de mi portátil, nunca a 0.0.0.0/0. Activa la protección de metadatos de la máquina en su modo más estricto. Luego dame el comando SSH para conectarme y comprobar qué máquina es. Recuérdame eliminar la máquina al acabar.
```

**Qué deberías ver**

De 'lanzar' a 'running' en 16 segundos. 2 CPUs y 913 MB de memoria, en una zona de la región más cercana (en clase, una del norte de Europa) y con su IP pública.

---

## Paso 3 · Desplegar la app con Docker en la máquina virtual

**Qué construye**

- El servidor de la S10/S11, ahora por HTTP
- Docker y git en la máquina virtual; clonar el repo
- docker build + docker run -p 8000:8000
- Probarlo desde mi portátil, por internet

**Prompt**

```text
En la máquina virtual de mi proveedor de nube, guíame para: instalar Docker y git, clonar mi repositorio de GitHub, construir la imagen Docker del servidor MCP y arrancar el contenedor en el puerto 8000. Antes, prepara el proyecto: que el servidor pueda usar el transporte Streamable HTTP (variable MCP_TRANSPORT=http), una ruta GET /salud para comprobar que está vivo, un Dockerfile pequeño que no corra como root, y un cliente_http.py que se conecte por URL. Después genera un script nube/desplegar.sh para mi proveedor que haga todo el despliegue y explícamelo para que lo lea antes de ejecutarlo. Luego pruébalo desde mi portátil. Explica cada comando y recuérdame que esto consume capa gratuita y hay que apagarlo.
```

**Qué deberías ver**

Una imagen de 198 MB construida en 18,6 s. Desde mi portátil al norte de Europa: conecta en 193 ms y cada tool responde en décimas. El mismo servidor de la S10.

---

## Paso 4 · Almacén de objetos: subir ficheros y asegurar el bucket

**Qué construye**

- Bucket s12-tienda-<cuenta> en el norte de Europa
- Subimos la política de devoluciones y el README
- Bloqueo de acceso público: activado
- Enlace firmado para compartir con caducidad

**Prompt**

```text
Guíame para crear un bucket en el almacén de objetos de mi proveedor de nube y subir unos ficheros con la CLI del proveedor. Muy importante: enséñame la configuración de permisos por defecto (el bloqueo de acceso público) y comprueba desde fuera que un fichero no se puede leer sin permiso. Luego enséñame la forma correcta de compartir un solo fichero: un enlace firmado que caduque en 5 minutos. Explica cuándo y cómo se abriría un bucket para un sitio estático y recalca el error típico de dejar un bucket público por error y sus consecuencias.
```

**Qué deberías ver**

Los bloqueos de acceso público vienen activados sin tocar nada: el bucket es privado por defecto. Sin firma, 403; con el enlace firmado, 200.

---

## Paso 5 · APAGAR todo, coste y checklist

**Qué construye**

- Eliminar la máquina virtual (su disco se va con ella)
- Borrar el cortafuegos y el par de claves
- Vaciar y borrar el bucket
- Comprobar: todo a cero

**Prompt**

```text
Ayúdame a hacer la limpieza completa para no incurrir en coste: eliminar la máquina virtual y esperar a que conste como eliminada, borrar el cortafuegos y el par de claves, vaciar y borrar el bucket, y comprobar con la CLI de mi proveedor de nube que no queda nada: máquinas, discos, IPs fijas, instantáneas y buckets. Genera tú mismo todo esto en un script nube/apagar.sh para mi proveedor que se pueda lanzar varias veces sin fallar, y explícamelo para que lo lea antes de ejecutarlo. Luego escribe en el README los pasos de despliegue, el checklist de 'apagar todo', un resumen de los conceptos (máquina virtual, almacén de objetos, red privada, gestión de identidades y permisos) y la alternativa gratuita.
```

**Qué deberías ver**

31 segundos para eliminar la máquina. Después, el resto en cadena: cortafuegos, claves y bucket. El coste de toda la práctica, menos de 1 céntimo.

---

## Ejercicio 1 · Saca tu app a internet

**Qué construye**

- Elige tu proveedor de nube o Render/Railway
- Despliega
- Comprueba que funciona online
- Si fue tu proveedor de nube: apaga y comprueba

**Prompt**

```text
Quiero desplegar un proyecto pequeño (el servidor MCP de la Sesión 10) y dejarlo accesible online. Elige conmigo entre la capa gratuita de mi proveedor de nube (la máquina virtual más pequeña + Docker, desde la terminal web de la consola, con un script nube/desplegar.sh que generes tú y yo lea antes de ejecutarlo) o, si no quiero dar tarjeta, Render o Railway con el Dockerfile del repositorio. Guíame para desplegarlo, comprobar desde mi portátil que responde con su URL y, si fue mi proveedor de nube, eliminar todos los recursos con nube/apagar.sh y comprobar en la facturación que el gasto queda a cero.
```

**Qué deberías ver**

La app respondiendo con su URL y, si usaste tu proveedor de nube, todo a cero al final.

---

## Ejercicio 2 · Reto: despliegue seguro y con la cuenta vigilada

**Qué construye**

- Cuenta segura
- Cortafuegos mínimo
- Un bucket privado
- Nota de coste y checklist

**Prompt**

```text
Despliega mi proyecto en la capa gratuita de mi proveedor de nube cuidando la seguridad y el gasto: trabaja con un usuario de trabajo (no root) con MFA, crea una alerta de presupuesto de 5 USD (80 % real y 100 % previsto), lanza la máquina virtual con un cortafuegos que no abra ningún puerto a 0.0.0.0/0 (el 22 solo para la IP de la terminal web y el 8000 solo para mi IP), guarda algún fichero en un bucket privado y comprueba desde fuera que da 403, y comparte un fichero con un enlace firmado de 5 minutos. Al final elimina todo, comprueba que no queda nada y escribe una nota de coste con el checklist de apagado.
```

**Qué deberías ver**

Las capturas de seguridad, el 403 del bucket y el recuento final a cero.

---

*Material del Máster AI Engineer · The Power*
