#!/usr/bin/env bash
# Borra TODO lo de la practica (app, entorno, registro de imagenes y logs) borrando su grupo de recursos,
# y comprueba que no queda nada que pueda costar dinero.
# Uso:   bash azure/apagar.sh
set -euo pipefail

RG=${RG:-rg-master-mcp}

echo "== Borrando el grupo de recursos $RG (todo lo que hay dentro se va con el)"
time az group delete --name "$RG" --yes

echo "== Comprobacion final"
echo "Grupo $RG existe:            $(az group exists --name "$RG")"
echo "Container Apps en la cuenta: $(az containerapp list --query 'length(@)' -o tsv)"
echo "Registros de imagenes:       $(az acr list --query 'length(@)' -o tsv)"
