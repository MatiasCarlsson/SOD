#!/usr/bin/env bash

# Script Interactivo de Demostración en Vivo (Defensa Oral - SOD 2026)
# Uso: ./scripts/demo_en_vivo.sh

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

pause_step() {
    echo ""
    echo -e "${YELLOW}${BOLD}>>> Presiona [ENTER] para continuar al siguiente paso...${NC}"
    read -r
}

clear
echo -e "${CYAN}${BOLD}${NC}"
echo -e "${CYAN}${BOLD}   DEMO EN VIVO: SISTEMA AUTOMATIZADO DE CULTIVO HIDROPÓNICO DISTRIBUIDO${NC}"
echo -e "${CYAN}${BOLD}${NC}"
echo ""
echo "Este asistente ejecuta de forma guiada los 4 bloques de demostración práctica:"
echo "  1. [Persona 1] Stack IoT en Docker Compose (Mosquitto + Sensor + Controlador)"
echo "  2. [Persona 2] Procesamiento Paralelo en Apache Spark (1M de registros)"
echo "  3. [Persona 2] Orquestación k3s/k3d: Escalado (kubectl scale) y Self-Healing"
echo "  4. [Persona 2] Idempotencia con Ansible (changed=0)"
pause_step

# Bloque 1: IoT y lazo cerrado
echo -e "${GREEN}${BOLD}[DEMO 1] Levantando broker Mosquitto, sensor, recolector y controlador...${NC}"
docker compose up -d mosquitto collector controller sensor-simulator
sleep 4
echo -e "${CYAN}--> Contenedores activos:${NC}"
docker compose ps

echo ""
echo -e "${CYAN}--> Observando telemetría y reacciones en tiempo real (Ctrl+C no detendrá el script, mostramos 12 segundos de logs)...${NC}"
timeout 12s docker compose logs -f sensor-simulator controller || true

echo ""
echo -e "${CYAN}--> Archivos persistidos por el recolector en data/raw/:${NC}"
ls -lh data/raw/ | tail -n 5
pause_step

# Bloque 2: Apache Spark
echo -e "${GREEN}${BOLD}[DEMO 2] Ejecutando Job PySpark Batch sobre 1.000.000 de lecturas sintéticas...${NC}"
.venv/bin/python src/processing/spark/batch_analysis.py --input data/datasets/synthetic_1M.csv --master "local[2]"
pause_step

# Bloque 3: k3s / k3d orquestación, escalado y tolerancia a fallos
echo -e "${GREEN}${BOLD}[DEMO 3] Verificando / Creando clúster k3s multinodo (1 server + 2 agents)...${NC}"
if ! k3d cluster list | grep -q "sod-cluster"; then
    make k3s-up
fi
kubectl get nodes -o wide

echo ""
echo -e "${CYAN}--> Desplegando simulador de sensores en k3s...${NC}"
make k3s-deploy
sleep 4
kubectl get pods -l app=sensor-simulator -o wide
pause_step

echo -e "${GREEN}${BOLD}[DEMO 3b] Escalando horizontalmente de 1 a 5 réplicas (kubectl scale)...${NC}"
kubectl scale deployment sensor-simulator --replicas=5
sleep 4
kubectl get pods -l app=sensor-simulator -o wide
pause_step

echo -e "${GREEN}${BOLD}[DEMO 3c] Inyectando falla: eliminando un pod deliberadamente...${NC}"
VICTIM_POD=$(kubectl get pods -l app=sensor-simulator -o jsonpath='{.items[0].metadata.name}')
echo -e "${YELLOW}Eliminando pod: $VICTIM_POD${NC}"
kubectl delete pod "$VICTIM_POD" --now
sleep 3
echo -e "${CYAN}--> Estado inmediato tras la falla (Self-Healing en acción):${NC}"
kubectl get pods -l app=sensor-simulator -o wide
pause_step

# Bloque 4: Ansible idempotencia
echo -e "${GREEN}${BOLD}[DEMO 4] Verificando idempotencia de infraestructura con Ansible...${NC}"
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
pause_step

# Limpieza final
echo -e "${YELLOW}${BOLD}Limpiando entorno de demo (Docker Compose + k3d)...${NC}"
docker compose down
k3d cluster delete sod-cluster || true
echo -e "${GREEN}${BOLD}Demo en vivo finalizada con éxito.${NC}"

