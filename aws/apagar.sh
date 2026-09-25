#!/usr/bin/env bash
# Sesion 12 · Paso 5, LO MAS IMPORTANTE: apagar y borrar TODO lo creado, y comprobar que el gasto queda a cero.
# Ejecutar en AWS CloudShell. Se puede lanzar varias veces sin problema.
set -uo pipefail

ACC=$(aws sts get-caller-identity --query Account --output text)
ID=$(aws ec2 describe-instances --filters Name=tag:Name,Values=s12-mcp Name=instance-state-name,Values=pending,running,stopping,stopped \
  --query 'Reservations[].Instances[].InstanceId' --output text)
if [ -n "$ID" ]; then
  aws ec2 terminate-instances --instance-ids $ID --output table
  aws ec2 wait instance-terminated --instance-ids $ID && echo "Instancia terminada (su disco EBS se borra con ella)"
fi
SG=$(aws ec2 describe-security-groups --filters Name=group-name,Values=s12-mcp --query 'SecurityGroups[0].GroupId' --output text)
[ "$SG" != "None" ] && aws ec2 delete-security-group --group-id "$SG" && echo "Security group borrado"
aws ec2 delete-key-pair --key-name s12-clave 2>/dev/null && rm -f ~/s12-clave.pem && echo "Par de claves borrado"
B=s12-tienda-$ACC
aws s3 rb "s3://$B" --force 2>/dev/null && echo "Bucket vaciado y borrado"

echo
echo "---- Comprobacion: todo tiene que salir a 0 ----"
echo "Instancias no terminadas: $(aws ec2 describe-instances --filters Name=instance-state-name,Values=pending,running,stopping,stopped --query 'length(Reservations[].Instances[])' --output text)"
echo "Discos EBS:               $(aws ec2 describe-volumes --query 'length(Volumes)' --output text)"
echo "IPs elasticas:            $(aws ec2 describe-addresses --query 'length(Addresses)' --output text)"
echo "Snapshots propios:        $(aws ec2 describe-snapshots --owner-ids self --query 'length(Snapshots)' --output text)"
echo "Buckets S3:               $(aws s3api list-buckets --query 'length(Buckets)' --output text)"
echo "(La alerta de presupuesto se puede dejar: es gratis y te protege.)"
