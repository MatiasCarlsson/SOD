SHELL := /bin/bash
PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: help setup up down build k3s-up k3s-down k3s-deploy k3s-scale generate-data benchmark analyze test-all clean

help:
	@echo "=========================================================================="
	@echo " LABORATORIO DE SISTEMAS OPERATIVOS DISTRIBUIDOS (TIF - AE 4)"
	@echo " Sistema de Cultivo Hidropónico Automatizado Distribuido"
	@echo "=========================================================================="
	@echo " Comandos disponibles:"
	@echo "   make setup          : Aprovisiona el entorno con Ansible y verifica dependencias"
	@echo "   make build          : Compila las imágenes Docker del proyecto"
	@echo "   make up             : Levanta los servicios IoT (Mosquitto, Sensores, Recolector, Controlador)"
	@echo "   make down           : Detiene todos los contenedores y limpia volúmenes"
	@echo "   make k3s-up         : Crea el clúster k3s multinodo (1 server + 2 agents) con k3d"
	@echo "   make k3s-deploy     : Despliega el simulador de sensores en el clúster k3s"
	@echo "   make k3s-scale N=5  : Escala las réplicas del sensor en k3s a N"
	@echo "   make k3s-down       : Elimina el clúster k3d"
	@echo "   make generate-data  : Genera los datasets sintéticos (1M y 10M filas)"
	@echo "   make benchmark      : Ejecuta la campaña experimental automatizada (E1, E2, E5)"
	@echo "   make analyze        : Genera los gráficos académicos en alta resolución (DPI 300)"
	@echo "   make test-all       : Ejecuta validaciones completas del pipeline"
	@echo "=========================================================================="

setup:
	@echo "--> Ejecutando playbook de Ansible para validar entorno..."
	ansible-playbook -i ansible/inventory.ini ansible/playbook.yml

build:
	@echo "--> Compilando imágenes Docker locales..."
	docker compose build

up:
	@echo "--> Levantando stack IoT y Spark Standalone..."
	docker compose up -d mosquitto collector controller sensor-simulator spark-master spark-worker-1

down:
	@echo "--> Bajando stack Docker..."
	docker compose down -v

k3s-up:
	@echo "--> Creando clúster k3s multinodo con k3d..."
	k3d cluster create sod-cluster --servers 1 --agents 2 --port 8081:80@loadbalancer --wait || true

k3s-deploy:
	@echo "--> Importando imagen a k3d y desplegando manifiestos..."
	docker tag ae4-sensor-simulator:latest sod-sensor-simulator:latest || true
	k3d image import sod-sensor-simulator:latest -c sod-cluster || true
	kubectl apply -f k8s/sensor-deployment.yaml

k3s-scale:
	@echo "--> Escalando despliegue de sensores a $(N) réplicas..."
	kubectl scale deployment sensor-simulator --replicas=$(N)
	kubectl get pods -l app=sensor-simulator -w

k3s-down:
	@echo "--> Eliminando clúster k3d..."
	k3d cluster delete sod-cluster

generate-data:
	@echo "--> Generando datasets sintéticos deterministas..."
	$(PYTHON) src/benchmarks/generate_synthetic_data.py --count 1000000 --output data/datasets/synthetic_1M.csv
	$(PYTHON) src/benchmarks/generate_synthetic_data.py --count 10000000 --output data/datasets/synthetic_10M.csv

benchmark:
	@echo "--> Ejecutando campaña experimental (E1, E2, E5) con 3 repeticiones..."
	$(PYTHON) benchmarks/run_experiments.py --all --repetitions 3

analyze:
	@echo "--> Generando gráficos estadísticos para informe APA..."
	$(PYTHON) analysis/generate_plots.py

test-all: setup
	@echo "--> Verificando sintaxis Python..."
	$(PYTHON) -m py_compile src/common/config.py src/sensors/sensor_simulator.py src/collector/collector.py src/controller/controller.py src/processing/baseline_python/process_baseline.py src/processing/hadoop/mapper.py src/processing/hadoop/reducer.py src/processing/spark/batch_analysis.py src/processing/spark/streaming_processor.py
	@echo "--> Validando procesamiento baseline sobre 1M..."
	$(PYTHON) src/processing/baseline_python/process_baseline.py --input data/datasets/synthetic_1M.csv
	@echo "--> Validando Hadoop streaming sobre 1M..."
	$(PYTHON) src/processing/hadoop/run_hadoop_job.py --input data/datasets/synthetic_1M.csv
	@echo "--> Validando Spark batch sobre 1M..."
	$(PYTHON) src/processing/spark/batch_analysis.py --input data/datasets/synthetic_1M.csv --master "local[2]"
	@echo "--> Todas las pruebas pasaron con éxito."

clean:
	rm -rf data/raw/* data/metrics/* analysis/figures/*

