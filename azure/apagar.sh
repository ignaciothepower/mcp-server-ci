#!/usr/bin/env bash
# Borra TODO lo de la practica (app, entorno, registro de imagenes y logs) borrando su grupo de recursos,
# y comprueba que no queda nada que pueda costar dinero.
# Uso:   bash azure/apagar.sh
# El entorno de Container Apps tarda en borrarse (20-30 min). El script escribe una linea cada 30 s:
# asi se ve que avanza y la Cloud Shell no se desconecta por inactividad. Se puede relanzar sin problema.
set -euo pipefail

RG=${RG:-rg-master-mcp}

if [ "$(az group exists --name "$RG")" = "true" ]; then
  echo "== Borrando el grupo de recursos $RG (todo lo que hay dentro se va con el)"
  az group delete --name "$RG" --yes --no-wait
  inicio=$SECONDS
  while [ "$(az group exists --name "$RG")" = "true" ]; do
    sleep 30
    echo "   ... borrando ($(( (SECONDS - inicio) / 60 )) min)"
  done
  echo "Grupo borrado en $(( (SECONDS - inicio) / 60 )) min"
else
  echo "== El grupo $RG ya no existe: no hay nada que borrar"
fi

echo "== Comprobacion final"
echo "Grupo $RG existe:            $(az group exists --name "$RG")"
echo "Container Apps en la cuenta: $(az containerapp list --query 'length(@)' -o tsv)"
echo "Registros de imagenes:       $(az acr list --query 'length(@)' -o tsv)"
