# Trabajo Integrador Final: Sistema Automatizado de Cultivo Hidropónico Distribuido

[![Sistemas Operativos Distribuidos](https://img.shields.io/badge/C%C3%A1tedra-Sistemas%20Operativos%20Distribuidos-blue.svg)]()
[![Docker](https://img.shields.io/badge/Virtualizaci%C3%B3n-Docker-2496ED.svg?logo=docker&logoColor=white)]()
[![k3s](https://img.shields.io/badge/Orquestaci%C3%B3n-k3s%20%2F%20k3d-FFC61C.svg?logo=k3s&logoColor=black)]()
[![MQTT](https://img.shields.io/badge/IoT-Eclipse%20Mosquitto-660066.svg?logo=eclipse-mosquitto&logoColor=white)]()
[![Apache Spark](https://img.shields.io/badge/Big%20Data-Apache%20Spark-E25A1C.svg?logo=apache-spark&logoColor=white)]()
[![Ansible](https://img.shields.io/badge/IaC-Ansible%20Idempotente-EE0000.svg?logo=ansible&logoColor=white)]()

Este repositorio contiene la implementación práctica completa, automatización de infraestructura, campañas de medición y documentación académica para el **Trabajo Integrador Final (TIF - AE 4)** de la cátedra de **Sistemas Operativos Distribuidos** (Ingeniería en Sistemas de Información).

---

## 1. Resumen de la Arquitectura

El sistema modela una instalación agrícola de precisión basada en cultivo hidropónico con control ciberfísico en lazo cerrado:
- **Capa IoT (Simulación y Mensajería):** Estaciones sensoras emiten lecturas continuas (pH, conductividad eléctrica, temperatura del agua, humedad ambiental y nivel de agua) con ruido gaussiano y deriva estacional hacia un broker **Eclipse Mosquitto (MQTT)**.
- **Control Reactivo en Lazo Cerrado:** Un microservicio controlador evalúa anomalías agronómicas en tiempo real (ej. pH > 6.5 o nivel de agua < 30%) y despacha órdenes inmediatas a actuadores simulados (dosificadores y bombas) midiendo latencias fin-a-fin.
- **Orquestación y Alta Disponibilidad:** El simulador se despliega sobre un clúster multinodo de **k3s (vía k3d)** con 1 nodo servidor y 2 nodos agentes en Docker, soportando escalabilidad horizontal (`kubectl scale`) y autorrecuperación (*self-healing*) ante fallas.
- **Procesamiento Distribuido (Big Data):** Comparación cuantitativa de desempeño y escalabilidad entre **Python Secuencial**, **Apache Hadoop (MapReduce Streaming)** y **Apache Spark (Batch y Structured Streaming)** sobre volúmenes de 1M y 10M de registros.
- **Infraestructura como Código (IaC):** Playbook de **Ansible** que garantiza aprovisionamiento determinista e idempotente (`changed=0`).

```
                              [ Clúster k3s (k3d) ]
                              1 Server + 2 Agents
                         ┌─────────────┴─────────────┐
                         ▼                           ▼
                 [ Pod Sensor-Z1 ]           [ Pod Sensor-ZN ]
                         │                           │
                         └─────────────┬─────────────┘
                                       │ Publicación MQTT (1883)
                                       v
                         +---------------------------+
                         |  Broker Eclipse Mosquitto |
                         +-------------+-------------+
                                       |
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
   +-------------------------+                   +-------------------------+
   |  Controlador Reactivo   |                   |   Servicio Recolector   |
   |   (Lazo Cerrado E5)     |                   |  (Ingesta a Disco /raw) |
   +------------+------------+                   +------------+------------+
                │                                             │
                v Órdenes actuador                            v Lotes JSON
   +-------------------------+                   +-------------------------+
   |   Actuadores Simulados  |                   |   Volumen Compartido    |
   | (Dosificador / Bomba)   |                   +------------+------------+
   +-------------------------+                                │
                                             ┌────────────────┴──────────────┐
                                             ▼                               ▼
                                  +--------------------+           +--------------------+
                                  | Apache Spark Batch |           |  Hadoop Streaming  |
                                  |    (DataFrames)    |           |    (MapReduce)     |
                                  +--------------------+           +--------------------+
```

---

## 2. Prerrequisitos de Software

Para reproducir el entorno se requiere una máquina Linux (o WSL2 en Windows) con al menos 8 GB de RAM y los siguientes paquetes:
- **Docker Engine y Docker Compose** (Plugin v2+)
- **k3d** (v5.x+) y **kubectl** (v1.28+)
- **Ansible** (core 2.15+)
- **Python 3.10+** con soporte para `venv`

### Instalación en Arch / CachyOS Linux:
```bash
sudo pacman -S kubectl ansible
yay -S k3d-bin
```

### Instalación en Ubuntu / Debian:
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 kubectl ansible python3-venv
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
```

---

## 3. Guía de Reproducción Paso a Paso

El proyecto incluye un `Makefile` que estandariza todas las operaciones del ciclo de vida del laboratorio:

### Paso 1: Aprovisionamiento y Verificación de Idempotencia (Ansible)
```bash
make setup
```
> Ejecuta el playbook `ansible/playbook.yml`. Al ejecutarlo una segunda vez, comprobará que el estado no produce alteraciones colaterales (`changed=0`).

### Paso 2: Construir e Iniciar el Stack IoT Local
```bash
make build
make up
```
> Levanta Mosquitto (puerto 1883), el recolector, el controlador y una instancia base del sensor, además del master y worker de Apache Spark.

Para verificar que el controlador en lazo cerrado reacciona ante anomalías:
```bash
docker compose logs -f controller
```

### Paso 3: Orquestación con k3s (k3d)
Para demostrar la orquestación distribuida en Kubernetes:
```bash
# 1. Crear el clúster k3s multinodo (1 servidor + 2 agentes)
make k3s-up

# 2. Desplegar los manifiestos del sensor
make k3s-deploy

# 3. Escalar horizontalmente a 5 o 20 réplicas
make k3s-scale N=5

# 4. Demostrar autorrecuperación (Self-Healing)
# Eliminar un pod deliberadamente y observar su regeneración inmediata:
kubectl delete pod $(kubectl get pods -l app=sensor-simulator -o jsonpath='{.items[0].metadata.name}')
kubectl get pods -l app=sensor-simulator -w
```

### Paso 4: Generación de Datos y Campaña Experimental (E1 a E5)
```bash
# 1. Generar datasets sintéticos deterministas (1M y 10M de registros)
make generate-data

# 2. Ejecutar la campaña experimental completa con 3 repeticiones
make benchmark

# 3. Generar los gráficos estadísticos en alta resolución (DPI 300)
make analyze
```
Los gráficos generados se almacenarán en `analysis/figures/` y las métricas crudas en `data/metrics/`.

### Paso 5: Limpieza del Entorno
```bash
make down       # Detiene los contenedores Docker
make k3s-down   # Elimina el clúster k3d
```

---

## 4. Estructura del Repositorio

```text
.
├── AE4_TIF_SOD_2026_D_Hidroponia_ADAPTADA.md   # Consigna oficial de la cátedra
├── PLAN_DE_TRABAJO.md                          # Plan maestro de fases
├── Makefile                                    # Automatización centralizada de comandos
├── docker-compose.yml                          # Orquestación de contenedores del laboratorio
├── config/mosquitto/                           # Configuración del broker MQTT
├── ansible/                                    # Playbooks e inventario para aprovisionamiento
├── k8s/                                        # Manifiestos de Kubernetes (k3s / k3d)
├── src/
│   ├── common/                                 # Constantes, tópicos y umbrales agronómicos
│   ├── sensors/                                # Simulador de sensores con ruido y deriva
│   ├── collector/                              # Recolector MQTT e ingesta particionada
│   ├── controller/                             # Controlador reactivo en lazo cerrado
│   ├── processing/                             # Motores analíticos (Python, Hadoop, Spark)
│   └── benchmarks/                             # Generador masivo de datos sintéticos
├── benchmarks/                                 # Ejecutores de experimentos E1 a E5
├── analysis/                                   # Scripts de visualización y figuras DPI 300
└── docs/
    ├── informe_apa.md                          # Informe académico final (Normas APA 7.ª ed.)
    └── presentacion_defensa.md                 # Guion y diapositivas de la defensa oral
```

---

## 5. Entregables Académicos

1. **Informe Final:** Documento completo bajo normas APA (7.ª edición) en [`docs/informe_apa.md`](docs/informe_apa.md).
2. **Presentación de Defensa:** Guion técnico y diapositivas para la exposición con demostración en vivo en [`docs/presentacion_defensa.md`](docs/presentacion_defensa.md).

