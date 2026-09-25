#!/usr/bin/env bash
# Sesion 12 · Desplegar el servidor MCP en AWS (EC2 + Docker) y probar S3.
# Pensado para ejecutarse en AWS CloudShell (la terminal del navegador): ya tiene la AWS CLI
# y usa tu sesion de la consola, asi que NO hace falta crear access keys.
# Estos son los mismos comandos que se ejecutaron en clase, en el mismo orden.
set -euo pipefail

REGION=${AWS_REGION:-eu-north-1}
PORTATIL_IP=${PORTATIL_IP:?"Pon la IP publica de tu portatil: export PORTATIL_IP=\$(curl -s checkip.amazonaws.com) (ejecutado EN TU PORTATIL)"}
ACC=$(aws sts get-caller-identity --query Account --output text)
MIIP=$(curl -s https://checkip.amazonaws.com)          # IP de esta CloudShell (para el SSH)

# ---- Paso 1 · alerta de presupuesto: 5 USD/mes, aviso al 80 % real y al 100 % previsto
# (el usuario IAM administrador lo crea el dueno de la cuenta en la consola: IAM > Users > Create user)
MAIL=${MAIL:?"Pon el email de la alerta: export MAIL=tu@email"}
aws budgets create-budget --account-id "$ACC" \
  --budget '{"BudgetName":"s12-limite-5usd","BudgetLimit":{"Amount":"5","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}' \
  --notifications-with-subscribers "[{\"Notification\":{\"NotificationType\":\"ACTUAL\",\"ComparisonOperator\":\"GREATER_THAN\",\"Threshold\":80,\"ThresholdType\":\"PERCENTAGE\"},\"Subscribers\":[{\"SubscriptionType\":\"EMAIL\",\"Address\":\"$MAIL\"}]},{\"Notification\":{\"NotificationType\":\"FORECASTED\",\"ComparisonOperator\":\"GREATER_THAN\",\"Threshold\":100,\"ThresholdType\":\"PERCENTAGE\"},\"Subscribers\":[{\"SubscriptionType\":\"EMAIL\",\"Address\":\"$MAIL\"}]}]"

# ---- Paso 2 · red y maquina
VPC=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
# Security group (cortafuegos): NADA de 0.0.0.0/0. SSH solo desde CloudShell y el 8000 solo desde tu portatil
SG=$(aws ec2 create-security-group --group-name s12-mcp --vpc-id "$VPC" \
  --description "S12: SSH solo desde CloudShell, 8000 solo desde el portatil" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG" --protocol tcp --port 22   --cidr "$MIIP/32"
aws ec2 authorize-security-group-ingress --group-id "$SG" --protocol tcp --port 8000 --cidr "$PORTATIL_IP/32"
# Par de claves: la privada se queda en CloudShell con permisos 400 y NUNCA se imprime
aws ec2 create-key-pair --key-name s12-clave --query KeyMaterial --output text > ~/s12-clave.pem
chmod 400 ~/s12-clave.pem
# Imagen oficial y siempre actualizada de Amazon Linux 2023
AMI=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query Parameter.Value --output text)
# t3.micro = incluida en el Free Tier. HttpTokens=required = metadatos de la instancia solo con IMDSv2 (mas seguro)
ID=$(aws ec2 run-instances --image-id "$AMI" --instance-type t3.micro --key-name s12-clave \
  --security-group-ids "$SG" --metadata-options HttpTokens=required \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=s12-mcp}]' \
  --query 'Instances[0].InstanceId' --output text)
aws ec2 wait instance-running --instance-ids "$ID"
IP=$(aws ec2 describe-instances --instance-ids "$ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "Instancia $ID en $IP (espera ~20 s a que arranque el SSH)"
sleep 20
S="ssh -i $HOME/s12-clave.pem -o StrictHostKeyChecking=accept-new ec2-user@$IP"

# ---- Paso 3 · Docker en la EC2: instalar, clonar, construir y arrancar
$S "sudo dnf install -y -q docker git && sudo systemctl enable --now docker"
$S "git clone -q https://github.com/ignaciothepower/mcp-server-ci.git && cd mcp-server-ci && sudo docker build -q -t mcp-server ."
$S "sudo docker run -d --name mcp --restart unless-stopped -p 8000:8000 mcp-server && sleep 4 && curl -s localhost:8000/salud"
echo "Prueba desde TU PORTATIL:  curl http://$IP:8000/salud   y   python cliente_http.py http://$IP:8000"

# ---- Paso 4 · S3: bucket privado (AWS bloquea el acceso publico por defecto) y enlace temporal
B=s12-tienda-$ACC
aws s3api create-bucket --bucket "$B" --create-bucket-configuration LocationConstraint="$REGION"
aws s3 cp datos/politica_devoluciones.txt "s3://$B/datos/"
aws s3api get-public-access-block --bucket "$B" --output table
# Compartir UN fichero sin abrir el bucket: URL firmada que caduca a los 5 minutos
aws s3 presign "s3://$B/datos/politica_devoluciones.txt" --expires-in 300

echo "HECHO. Cuando acabes: bash aws/apagar.sh"
