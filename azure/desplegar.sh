#!/usr/bin/env bash
# Despliega el servidor MCP de la tienda en Azure Container Apps: HTTPS publico, escala a cero y solo tu IP puede entrar.
#
# Requisitos: Azure CLI con la sesion iniciada (az login). No hace falta Docker en el portatil:
# la imagen se construye en la nube a partir del Dockerfile del repo.
# Uso (desde la raiz del repo):   bash azure/desplegar.sh
# Al terminar:                    bash azure/apagar.sh
set -euo pipefail

RG=${RG:-rg-master-mcp}          # grupo de recursos: todo lo de la practica vive aqui y se borra de una vez
LOC=${LOC:-westeurope}           # region (Paises Bajos)
APP=${APP:-mcp-tienda}           # nombre de la Container App
MI_IP=${MI_IP:?Pon la IP publica de tu portatil: export MI_IP=x.x.x.x (en el portatil: curl https://api.ipify.org)}

echo "== 1. Extension y proveedores (solo la primera vez tarda)"
az extension add --name containerapp --upgrade --only-show-errors
for p in Microsoft.App Microsoft.OperationalInsights Microsoft.ContainerRegistry; do
  az provider register --namespace "$p" --wait
done

echo "== 2. Grupo de recursos"
az group create --name "$RG" --location "$LOC" --query "{grupo:name, region:location, estado:properties.provisioningState}" -o table

echo "== 3. Construir la imagen en la nube y crear la app (Dockerfile del repo)"
time az containerapp up --name "$APP" --resource-group "$RG" --location "$LOC" --source . \
  --ingress external --target-port 8000 --env-vars MCP_TRANSPORT=http PORT=8000

echo "== 4. Escala: de 0 a 1 replica (sin peticiones no hay contenedor encendido)"
az containerapp update --name "$APP" --resource-group "$RG" --min-replicas 0 --max-replicas 1 \
  --query "properties.template.scale" -o table

echo "== 5. Cortafuegos: solo tu IP"
az containerapp ingress access-restriction set --name "$APP" --resource-group "$RG" \
  --rule-name mi-portatil --ip-address "$MI_IP/32" --action Allow -o table

URL="https://$(az containerapp show --name "$APP" --resource-group "$RG" --query properties.configuration.ingress.fqdn -o tsv)"
echo "== 6. Comprobacion"
echo "URL del servidor MCP: $URL/mcp"
echo "Desde aqui (esta IP no es la de tu portatil): HTTP $(curl -s -o /dev/null -w '%{http_code}' "$URL/salud")  <- 403 = el cortafuegos funciona"
echo "Desde tu portatil:  curl $URL/salud   y   python cliente_http.py $URL"
