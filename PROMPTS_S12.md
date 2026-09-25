# Sesión 12 · Cloud Deployment: fundamentos de AWS · Prompts para Claude Code

Estos son los prompts que usamos en la práctica, en el mismo orden que en clase. Cópialos y pégalos en Claude Code uno a uno.

**Cómo usarlos**
1. Pega el prompt del paso y deja que Claude Code proponga los cambios.
2. **Lee el código antes de aceptar** (y los comandos, como `pip install`, antes de permitirlos).
3. Ejecuta y compara con el apartado *Qué deberías ver*.
4. Si no sale lo esperado, vuelve a pedírselo con lo que has aprendido.

> Antes de empezar: una cuenta de AWS con el **Free plan** (no cobra salvo que pases al plan de pago; pide tarjeta para verificar) o, si no quieres tarjeta, una cuenta gratuita de Render o Railway. Todo se hace desde **AWS CloudShell**, sin instalar nada ni crear access keys. Código y comandos: https://github.com/ignaciothepower/mcp-server-ci (carpeta `aws/`). **Al terminar, apaga todo** (`bash aws/apagar.sh`).

El resultado de referencia, con todo el código comentado, está en la carpeta `mcp-server-ci` del material de la sesión.

---

## Paso 1 · Cuenta Free Tier, seguridad y CLI

**Qué construye**

- La AWS CLI en CloudShell: ya viene instalada
- ¿Con quien estoy trabajando? (sts)
- Alerta de presupuesto: 5 USD al mes
- Usuario IAM: lo crea el dueno de la cuenta

**Prompt**

```text
Guiame para: 1) comprobar con la AWS CLI con que identidad estoy trabajando (aws sts get-caller-identity) y explicarme por que no debo usar la cuenta root en el dia a dia. 2) crear un usuario IAM con permisos de administrador desde la consola (IAM > Users > Create user) para usarlo en lugar de root, y activar MFA en root. 3) crear con la AWS CLI una alerta de presupuesto (AWS Budgets) de 5 USD al mes que me avise por email al 80 % del gasto real y al 100 % del previsto. Usa AWS CloudShell para no tener que crear access keys. Explica cada paso de seguridad. Si el alumno prefiere no dar tarjeta, dame la alternativa equivalente en Render o Railway.
```

**Qué deberías ver**

El Arn acaba en ':root': recien creada la cuenta, trabajas con la llave maestra. Justo lo que no hay que hacer.

---

## Paso 2 · Lanzar una maquina EC2 y conectarse

**Qué construye**

- Security group: solo las IPs que hacen falta
- Par de claves: la privada nunca se imprime
- t3.micro con Amazon Linux 2023
- SSH desde CloudShell

**Prompt**

```text
Explicame paso a paso como lanzar con la AWS CLI una instancia EC2 t3.micro marcada 'Free Tier eligible' con Amazon Linux 2023: la eleccion de la imagen (AMI, desde el parametro publico de SSM), el par de claves (key pair) y el security group. El security group solo debe abrir el puerto 22 a la IP de mi CloudShell y el 8000 a la IP de mi portatil, nunca a 0.0.0.0/0. Activa IMDSv2 obligatorio. Luego dame el comando SSH para conectarme y comprobar que maquina es. Recuerdame terminar la instancia al acabar.
```

**Qué deberías ver**

De 'lanzar' a 'running' en 16 segundos. Tipo t3.micro, zona eu-north-1b (Estocolmo) y su IP publica.

---

## Paso 3 · Desplegar la app con Docker en la EC2

**Qué construye**

- El servidor de la S10/S11, ahora por HTTP
- Docker y git en la EC2; clonar el repo
- docker build + docker run -p 8000:8000
- Probarlo desde mi portatil, por internet

**Prompt**

```text
En la instancia EC2, guiame para: instalar Docker y git, clonar mi repositorio de GitHub, construir la imagen Docker del servidor MCP y arrancar el contenedor en el puerto 8000. Antes, prepara el proyecto: que el servidor pueda usar el transporte Streamable HTTP (variable MCP_TRANSPORT=http), una ruta GET /salud para comprobar que esta vivo, un Dockerfile pequeno que no corra como root, y un cliente_http.py que se conecte por URL. Luego pruebalo desde mi portatil. Explica cada comando y recuerdame que esto consume Free Tier y hay que apagarlo.
```

**Qué deberías ver**

Desde mi portatil a Estocolmo: conecta en 193 ms y cada tool responde en decimas. El mismo servidor de la S10.

---

## Paso 4 · S3: subir ficheros y asegurar el bucket

**Qué construye**

- Bucket s12-tienda-<cuenta> en Estocolmo
- Subimos la politica de devoluciones y el README
- Bloqueo de acceso publico: activado
- Enlace firmado para compartir con caducidad

**Prompt**

```text
Guiame para crear un bucket S3 y subir unos ficheros con la AWS CLI. Muy importante: ensename la configuracion de permisos por defecto (el bloqueo de acceso publico) y comprueba desde fuera que un fichero no se puede leer sin permiso. Luego ensename la forma correcta de compartir un solo fichero: un enlace firmado (presigned URL) que caduque en 5 minutos. Explica cuando y como se abriria un bucket para un sitio estatico y recalca el error tipico de dejar un bucket publico por error y sus consecuencias.
```

**Qué deberías ver**

Los cuatro bloqueos de acceso publico vienen a True sin tocar nada: AWS lo hace privado por defecto.

---

## Paso 5 · APAGAR todo, coste y checklist

**Qué construye**

- Terminar la EC2 (su disco se va con ella)
- Borrar security group y par de claves
- Vaciar y borrar el bucket
- Comprobar: todo a cero

**Prompt**

```text
Ayudame a hacer la limpieza completa para no incurrir en coste: terminar la instancia EC2 y esperar a que este terminated, borrar el security group y el par de claves, vaciar y borrar el bucket S3, y comprobar con la CLI que no queda nada: instancias, discos EBS, IPs elasticas, snapshots y buckets. Deja todo en un script aws/apagar.sh que se pueda lanzar varias veces. Luego escribe en el README los pasos de despliegue, el checklist de 'apagar todo', el resumen de EC2/S3/VPC/IAM y la alternativa gratuita.
```

**Qué deberías ver**

31 segundos para terminar la instancia. Despues, el resto en cadena: security group, claves y bucket.

---

## Ejercicio 1 · Saca tu app a internet

**Qué construye**

- Elige AWS o Render/Railway
- Despliega
- Comprueba que funciona online
- Si fue AWS: apaga y comprueba

**Prompt**

```text
Quiero desplegar un proyecto pequeno (el servidor MCP de la Sesion 10) y dejarlo accesible online. Elige conmigo entre AWS Free Tier (EC2 t3.micro + Docker, desde AWS CloudShell) o, si no quiero dar tarjeta, Render o Railway con el Dockerfile del repositorio. Guiame para desplegarlo, comprobar desde mi portatil que responde con su URL y, si fue AWS, terminar todos los recursos y comprobar que el gasto queda a cero.
```

**Qué deberías ver**

La app respondiendo con su URL y, si usaste AWS, todo a cero al final.

---

## Ejercicio 2 · Reto: despliegue seguro y con la cuenta vigilada

**Qué construye**

- Cuenta segura
- Cortafuegos minimo
- Un bucket privado
- Nota de coste y checklist

**Prompt**

```text
Despliega mi proyecto en AWS Free Tier cuidando la seguridad y el gasto: trabaja con un usuario IAM en lugar de root, crea una alerta de presupuesto, lanza la EC2 con un security group que no abra ningun puerto a 0.0.0.0/0, guarda algun fichero en un bucket S3 privado y comprueba desde fuera que da 403, y comparte un fichero con un enlace firmado. Al final termina todo, comprueba que no queda nada y escribe una nota de coste con el checklist de apagado.
```

**Qué deberías ver**

Las capturas de seguridad, el 403 del bucket y el recuento final a cero.

---

*Material del Master AI Engineer · The Power · Ignacio de Pastors*
