# Presentación y Defensa Oral: Sistema Automatizado de Cultivo Hidropónico Distribuido

**Materia:** Sistemas Operativos Distribuidos  
**Carrera:** Ingeniería en Sistemas de Información  
**Facultad de Ingeniería, Tecnología y Arquitectura**  
**Autores:** Equipo de Trabajo Integrador Final (TIF - AE 4)  

---

## Estructura de la Exposición (Duración estimada: 15–20 minutos)

1. **Introducción y Motivación (2 min):** El desafío de la agricultura de precisión y la computación distribuida.
2. **Marco Teórico y Comparativa Tecnológica (4 min):**
   - Virtualización Completa (KVM/Proxmox) vs. Contenedores (Docker).
   - Orquestación con Kubernetes/k3s.
   - Paradigmas de Procesamiento: Hadoop MapReduce vs. Apache Spark.
   - Comunicación Desacoplada: Modelo Pub/Sub con MQTT.
3. **Arquitectura del Sistema y Diseño Práctico (4 min):**
   - Sensores, Recolector, Controlador en Lazo Cerrado y Broker Mosquitto.
   - Clúster k3s multinodo en k3d y automatización con Ansible.
4. **Resultados de la Campaña Experimental E1 a E5 (4 min):**
   - Comparativa de volumen (1M y 10M registros).
   - Escalabilidad y Speedup de Spark (Ley de Amdahl).
   - Latencia fin-a-fin del controlador reactivo.
   - Tolerancia a fallos y autorrecuperación en k3s.
5. **Demostración en Vivo (4 min):**
   - Levantamiento con `docker compose up -d`.
   - Inyección de anomalía de pH y reacción del controlador.
   - Escalado de réplicas en k3s (`kubectl scale`).
   - Caída y autorreinicio de pod (`kubectl delete pod`).
6. **Conclusiones y Preguntas del Tribunal (2 min).**

---

## Diapositivas de Apoyo

### Diapositiva 1: Portada
- **Título:** Modelado y Análisis de un Sistema Automatizado de Cultivo Hidropónico Distribuido
- **Subtítulo:** Integración de IoT, Contenedores, Orquestación en k3s, MapReduce y Apache Spark
- **Materia:** Sistemas Operativos Distribuidos (2026)

### Diapositiva 2: El Problema
- El cultivo hidropónico requiere estabilidad estricta: desvíos de pH (> 6.5) o falta de agua (< 30%) pueden destruir la cosecha en horas.
- La telemetría masiva continua exige sistemas desacoplados, tolerantes a fallos y con procesamiento analítico tanto en flujo (streaming) como por lotes (batch).
- ¿Cómo diseñar una infraestructura resiliente, escalable y reproducible usando herramientas modernas de sistemas distribuidos?

### Diapositiva 3: Comparativa Teórica de Virtualización
| Criterio | Virtualización Completa (Proxmox / KVM) | Virtualización por Contenedores (Docker / LXC) |
| :--- | :--- | :--- |
| **Aislamiento** | Aislamiento a nivel de hardware mediante Hypervisor Tipo 1 | Aislamiento a nivel de kernel (Namespaces y cgroups) |
| **Sobrecarga (Overhead)** | Alta: SO huésped completo, emulación de BIOS y memoria reservada | Mínima: comparte kernel con el host, asignación dinámica de memoria |
| **Tiempo de Arranque** | 30 a 90 segundos | 0.5 a 3 segundos |
| **Densidad** | 5 a 15 VMs por host | Decenas a cientos de contenedores por host |
| **Caso de Uso en SOD** | Entornos multitenant aislados y soporte para distintos SO | Microservicios de sensor, controladores e ingesta rápida |

### Diapositiva 4: Arquitectura del Laboratorio
```
[ Sensores en k3s ]  --> (MQTT: 1883) --> [ Broker Mosquitto ]
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
     [ Controlador Lazo Cerrado ]                                      [ Recolector ]
     (Detecta anomalías de pH/H2O)                                     (Persistencia en disco)
                 │                                                             │
                 ▼                                                             ▼
     [ Actuadores Simulados ]                                     [ Volúmenes Compartidos ]
     (Dosificador ácido / Bomba)                                               │
                                                ┌──────────────────────────────┴──────────────┐
                                                ▼                                             ▼
                                     [ Apache Spark Batch ]                        [ Hadoop MapReduce ]
                                     (DataFrames en memoria)                       (Streaming / Pipes)
```

### Diapositiva 5: Automatización e Idempotencia (Ansible)
- Despliegue declarativo reproducible con `ansible-playbook`.
- Principio de idempotencia: ejecutar el playbook múltiples veces no altera el estado deseado ni produce efectos colaterales (`changed=0`).

### Diapositiva 6: Resultados Experimentales E1 (Volumen) y E2 (Spark)
- **E1:** Spark supera a Hadoop y Python a medida que el volumen escala a millones de registros gracias al procesamiento en memoria y al optimizador Catalyst.
- **E2:** Factor de aceleración (*Speedup*) con 1, 2 y 3 workers muestra una curva cóncava coherente con la Ley de Amdahl debido a la sobrecarga inherente de shuffle y serialización.

### Diapositiva 7: Resultados E3, E4 y E5 (Orquestación y Control)
- **E3 (Escalado k3s):** Despliegue rápido de pods con arranque inferior a 2 segundos por réplica.
- **E4 (Tolerancia a fallos):** Al eliminar un pod con `kubectl delete pod`, el ReplicaSet de k3s detecta la discrepancia y crea un reemplazo en ~1.5 s sin pérdida de telemetría global.
- **E5 (Control reactivo):** Latencia media fin-a-fin inferior a 5 ms para emitir la orden correctiva al actuador ante una anomalía de pH.

---

## Guion Técnico para la Demostración en Vivo

```bash
# 1. Levantamiento del stack base en Compose
docker compose up -d mosquitto collector controller sensor-simulator
docker compose ps

# 2. Demostración del lazo cerrado (ver logs del controlador ante alertas)
docker compose logs -f controller --tail=10

# 3. Creación y verificación del clúster k3s multinodo
k3d cluster list
kubectl get nodes -o wide

# 4. Escalado horizontal del simulador de sensores
kubectl scale deployment sensor-simulator --replicas=5
kubectl get pods -l app=sensor-simulator

# 5. Demostración de autorrecuperación (Self-Healing)
# Eliminar deliberadamente uno de los pods:
POD_NAME=$(kubectl get pods -l app=sensor-simulator -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD_NAME
# Mostrar que k3s crea inmediatamente un nuevo pod:
kubectl get pods -l app=sensor-simulator

# 6. Ejecución del job de Spark
python src/processing/spark/batch_analysis.py --input data/datasets/synthetic_1M.csv --master "local[2]"
```

