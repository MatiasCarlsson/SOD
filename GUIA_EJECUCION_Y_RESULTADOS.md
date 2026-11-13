# Guía de Ejecución y Comprensión de Resultados Esperados

Este documento explica paso a paso **cómo levantar, probar y demostrar todo el laboratorio**, qué **salidas exactas esperar en pantalla** y **cómo interpretar técnicamente cada resultado** frente al equipo docente.

---

## 1. Preparación Inicial del Entorno (Una sola vez)

Asegúrate de estar en la raíz del proyecto y que el entorno virtual `.venv` esté creado:

```bash
# 1. Verificar herramientas del sistema
docker --version && docker compose version
k3d --version
kubectl version --client
ansible --version

# 2. Validar entorno e idempotencia con Ansible
make setup
```

### Resultado esperado de `make setup`:
- **Primera ejecución:** crea carpetas faltantes si no existían (`changed=1`).
- **Segunda ejecución:** devuelve `ok=8  changed=0  failed=0`.
- **Cómo explicarlo:** *"Ansible aplica un enfoque declarativo e idempotente: si el entorno ya cumple con el estado deseado, no realiza modificaciones adicionales (`changed=0`), garantizando reproducibilidad en cualquier máquina."*

---

## 2. Cómo Ejecutar y Entender el Bloque IoT (Docker Compose + MQTT)

### Comandos de ejecución:
```bash
# Levantar Mosquitto, Recolector, Controlador y Simulador
docker compose up -d mosquitto collector controller sensor-simulator

# Verificar estado de contenedores
docker compose ps

# Ver en vivo la telemetría del sensor y las reacciones del controlador
docker compose logs -f sensor-simulator controller
```

*(Presiona `Ctrl + C` para salir de los logs sin detener los contenedores).*

### Resultados esperados:
1. En `sensor-simulator` verás líneas periódicas (1 lectura/segundo):
   ```text
   [SensorSimulator] Zona: zona_1 | pH: 7.19 | CE: 1.76 | T: 21.4°C | H2O: 84.6% | Alerta: ph_high
   ```
2. En `controller`, cada vez que el pH sale de $[5.5, 6.5]$ o el nivel de agua cae por debajo de $30\%$, aparece inmediatamente:
   ```text
   [ClosedLoopController] ACCION REPORTE -> Zona: zona_1 | Sensor: node_zona_1 | ph=7.19 | Orden: DOSIFICAR_ACIDO (dosificador_acido) | Latencia: 0.57 ms
   ```
3. En `data/raw/`, el servicio `collector` va creando archivos `batch_YYYYMMDD_HHMMSS_*.json` cada ~3 segundos o cada 25 mensajes.

### Qué significa e interpretación técnica:
- **Desacoplamiento (MQTT Pub/Sub):** El sensor no conoce la IP del controlador ni del recolector; solo publica en el tópico `hidroponia/zona_1/telemetria`.
- **Control en Lazo Cerrado:** El controlador detecta el desvío agronómico y emite la orden correctiva hacia `hidroponia/zona_1/actuadores/dosificador_acido` en **~0,5 a 5 milisegundos**, demostrando respuesta en tiempo real blando.

Para detener este bloque:
```bash
docker compose down
```

---

## 3. Cómo Ejecutar y Entender el Bloque k3s / k3d (Orquestación y Tolerancia a Fallos)

### Comandos de ejecución:
```bash
# 1. Crear clúster k3s multinodo (1 control-plane + 2 agentes en Docker)
make k3s-up
kubectl get nodes -o wide

# 2. Importar imagen del sensor y desplegar manifiestos
make k3s-deploy
kubectl get pods -l app=sensor-simulator -o wide

# 3. Escalar horizontalmente a 5 réplicas (o 20)
kubectl scale deployment sensor-simulator --replicas=5
kubectl get pods -l app=sensor-simulator -w

# 4. Inyectar falla eliminando un pod deliberadamente
POD=$(kubectl get pods -l app=sensor-simulator -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod "$POD" --now
kubectl get pods -l app=sensor-simulator -o wide
```

### Resultados esperados:
1. `kubectl get nodes` muestra **3 nodos en estado `Ready`**: `k3d-sod-cluster-server-0` (control-plane) y `k3d-sod-cluster-agent-0` / `agent-1`.
2. Al ejecutar `kubectl scale --replicas=5`, pasan en **~3 segundos** de `ContainerCreating` a `1/1 Running`, distribuidos entre los nodos agentes.
3. Al ejecutar `kubectl delete pod`, el controlador `ReplicaSet` de k3s detecta que hay $4 \neq 5$ réplicas e instancia automáticamente un pod nuevo con otro nombre en **menos de 2 segundos** (*Self-Healing*).

Para limpiar el clúster al finalizar:
```bash
make k3s-down
```

---

## 4. Cómo Ejecutar y Entender el Bloque Big Data (Python vs. Hadoop vs. Spark)

### Comandos de ejecución:
```bash
# 1. Generar datasets sintéticos (si no existen en data/datasets/)
make generate-data

# 2. Ejecutar prueba rápida comparativa sobre 1M de registros
make test-all

# 3. Ejecutar Spark Structured Streaming sobre los archivos de data/raw/
.venv/bin/python src/processing/spark/streaming_processor.py --input-dir data/raw --master "local[2]"
```

### Resultados esperados y por qué ocurren:
Todos los motores devuelven **exactamente las mismas medias y conteo de alertas por zona** (verificando consistencia algorítmica), pero con diferencias notables de tiempo:

1. **Volumen de 1.000.000 de filas (1M):**
   - **Python secuencial** suele ser muy competitivo (~3,2 s) porque lee el archivo localmente sin necesidad de inicializar una máquina virtual Java (JVM) ni distribuir tareas.
   - **Hadoop Streaming** (~4,2 s) paga el costo de crear tuberías de procesos (`mapper.py | sort | reducer.py`).
   - **Apache Spark** (~5,3 s de cómputo + ~8 s de arranque JVM) sufre el *overhead* inicial en datasets pequeños.
2. **Volumen de 10.000.000 de filas (10M):**
   - **Python secuencial** y **Hadoop Streaming** escalan linealmente por ser I/O y CPU bound en un único flujo (~31–42 s).
   - **Apache Spark** procesa en paralelo en memoria usando todos los núcleos y el optimizador *Catalyst*, reduciendo drásticamente el tiempo (~6–8 s), resultando **4× a 6× más rápido**.
3. **Escalabilidad de Spark (E2 - 1, 2 y 3 Workers):**
   - Al pasar de 1 a 2 y 3 workers, el tiempo cae pero el *Speedup* real ($S_p = T_1 / T_p$) no alcanza el lineal ideal ($2\times, 3\times$) debido a la **Ley de Amdahl**: existen fracciones secuenciales (lectura de cabecera/esquema, coordinación del driver y *shuffle* entre particiones) que acotan la aceleración máxima.

---

## 5. Cómo Reproducir la Campaña Experimental Completa y Gráficos

```bash
# 1. Correr experimentos E1, E2 y E5 (3 repeticiones cada uno)
make benchmark

# 2. Generar las figuras académicas en analysis/figures/ (PNG a 300 DPI)
make analyze
```

Los resultados quedan guardados en:
- `data/metrics/experiment_1_volume.csv`
- `data/metrics/experiment_2_spark_scalability.csv`
- `data/metrics/experiment_5_latency_summary.csv`
- `analysis/figures/figura_1_comparacion_volumen.png`
- `analysis/figures/figura_2_speedup_spark.png`
- `analysis/figures/figura_3_latencia_controlador.png`

---

## 6. Modo Rápido para la Defensa: Script Guiado y Videos de Respaldo

- **Demo en vivo asistida:**
  ```bash
  ./scripts/demo_en_vivo.sh
  ```
  Ejecuta paso a paso los 4 bloques de demostración esperando confirmación con `ENTER` entre bloques para que no haya errores de tipeo en vivo.
- **Videos MP4 de respaldo (en caso de fallas de red/recursos en la exposición):**
  Ubicados en `docs/videos/`:
  - `01_demo_iot_lazo_cerrado.mp4`
  - `02_demo_k3s_escalado_tolerancia.mp4`
  - `03_demo_spark_hadoop_ansible.mp4`

---

## 7. Preguntas Clave que Puede Hacer el Tribunal (Respuestas Rápidas)

- **¿Por qué usaron Docker/k3d en lugar de Proxmox con VMs?**  
  *Respuesta:* Proxmox (KVM) realiza virtualización completa de hardware (overhead de kernel por VM, ~30–90 s de arranque y GBs fijos de RAM). Docker virtualiza a nivel de sistema operativo compartiendo el kernel mediante *namespaces* y *cgroups*, permitiendo levantar un clúster de 3 nodos k3s y un clúster Spark en segundos en una laptop de 16 GB sin perder los conceptos teóricos de orquestación, red y aislamiento.
- **¿Por qué Spark le gana a Hadoop en 10M pero pierde en 1M?**  
  *Respuesta:* Por el costo fijo de inicialización del `SparkContext` en JVM y la planificación del DAG. Ese *overhead* se amortiza recién cuando el volumen supera varios millones de registros; en 10M, Spark procesa en memoria distribuida superando ampliamente a MapReduce y a Python monohilo.
- **¿Cómo aseguran que las lecturas no se pierdan si falla un pod?**  
  *Respuesta:* k3s monitorea continuamente el estado deseado (`replicas: 5`) y reprograma el pod en milisegundos. Además, MQTT con QoS 1 garantiza confirmación (`PUBACK`) al publicar hacia el broker Mosquitto, que posee persistencia habilitada.

