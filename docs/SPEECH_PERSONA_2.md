# Guion de Exposición Oral — PERSONA 2

> **Rol en la defensa:** orquestación (k3s/k3d), MQTT, Hadoop vs. Spark, experimentos E1–E5, **Demo 2 (k3s)**, **Demo 3 (Spark + Ansible)** y conclusiones técnicas.
> **Presentación:** `docs/Presentacion_TIF_SOD_2026.pptx` — 24 diapositivas, estilo *Textmode Overlay*, transición *fade* y videos MP4 embebidos.
> **Duración de tu parte:** ~9 minutos, alternando con Persona 1 (total ~18 min).
> **Pista visual:** etiqueta **ámbar** arriba a la derecha = te toca a vos.

---

## Bloque A — Orquestación, mensajería y Big Data (4:40 – 7:20)

> *(Tomás la palabra después de la Diapositiva 7 de Persona 1)*

### Diapositiva 8 — Orquestación con k3s sobre k3d *(4:40 – 5:30)*
> "Gracias. En un sistema distribuido real no administramos contenedores a mano: necesitamos **orquestación**.
>
> Kubernetes es declarativo: describimos el estado deseado —por ejemplo, cinco réplicas— y un bucle de reconciliación se encarga de que el estado real coincida. Si un pod muere, lo reemplaza.
>
> Usamos **k3s**, que reemplaza etcd por SQLite y consume menos de 512 MB de RAM, y **k3d**, que lo ejecuta dentro de Docker. A la derecha está nuestra topología: un *server* con el plano de control y dos *agents* donde corren los pods. Los sensores del clúster llegan al broker mediante `host.k3d.internal:1883`."

### Diapositiva 9 — Mensajería MQTT *(5:30 – 6:15)*
> "Para comunicar todo usamos **MQTT** con Mosquitto. Los sensores publican, el broker distribuye y los suscriptores —controlador y recolector— reciben del tópico `hidroponia/+/telemetria`.
>
> Ganamos cuatro cosas: desacoplamiento en **espacio** (nadie conoce las IPs de los demás), en **tiempo** (emisor y receptor no necesitan coincidir), un protocolo **liviano** ideal para telemetría a 1 Hz, y **QoS 1**, que con el PUBACK garantiza que ninguna alerta se pierda."

### Diapositiva 10 — Hadoop MapReduce vs. Apache Spark *(6:15 – 7:20)*
> "Para el análisis histórico comparamos dos arquitecturas, ilustradas arriba de cada tarjeta:
> - A la izquierda, **Hadoop MapReduce** sigue el flujo `Map → [disco] → Shuffle → Reduce`: persiste resultados intermedios en disco entre etapas, pagando penalidad de I/O. Lo implementamos con Hadoop Streaming (`mapper.py` y `reducer.py`).
> - A la derecha, **Apache Spark** sigue `DAG → [RAM] → Catalyst → Acción`: procesa DataFrames distribuidos en memoria, optimiza el plan lógico con Catalyst y unifica Batch y Structured Streaming.
>
> Como aclara el recuadro inferior **COMPARACIÓN JUSTA**, los tres motores (Python secuencial, Hadoop y Spark) ejecutan exactamente la misma agregación —promedios por zona y conteo de alertas— para que la comparativa sea válida.
>
> Le devuelvo la palabra a **[Nombre Persona 1]** para la arquitectura."
>
> `[Handoff → Persona 1 en Diapositiva 11]`

---

## Bloque B — Resultados y Demos 2 y 3 (11:00 – 16:50)

> *(Retomás la palabra después de la Demo 1, Diapositiva 14)*

### Diapositiva 15 — Separador `04 // RESULTADOS` *(11:00 – 11:10)*
> "Todo lo que sigue son mediciones reales, con tres repeticiones en procesos aislados."

### Diapositiva 16 — E1 · Rendimiento según volumen *(11:10 – 12:20)*
> "En el gráfico de barras de la izquierda comparamos el tiempo medio de cómputo en segundos (menor es mejor) para los tres motores: las **barras verde oscuro** corresponden a **1 millón de filas** y las **barras verde claro** a **10 millones de filas**.
>
> - Con **1 millón** (barras oscuras) gana Python con **3,28 s**, contra **4,21 s** de Hadoop y **5,37 s** de Spark. Como indica el cuadro **PUNTO DE INFLEXIÓN**, con volumen chico Spark pierde porque paga el arranque de la JVM y la planificación del DAG.
> - Al multiplicar por diez a **10 millones** (barras claras), el escenario se invierte: Python salta a **34,20 s** y Hadoop a **38,09 s** por el I/O de tuberías y disco, mientras que **Spark resuelve en 8,86 s**.
>
> Por eso los dos indicadores de la derecha resumen el resultado: en 10M de filas, Spark es **3,86× más rápido que Python** y **4,30× más rápido que Hadoop**."

### Diapositiva 17 — E2 · Escalabilidad de Spark *(12:20 – 13:20)*
> "En el gráfico de líneas de la izquierda medimos la aceleración (*Speedup*) de Spark sobre **10 millones de filas** al pasar de **1 a 3 workers**: la línea **gris punteada** muestra el speedup **Ideal** (`1×, 2×, 3×`) y la línea **verde continua** es el **Real** medido.
>
> En la **tabla de la derecha** vemos los tiempos exactos con su desvío estándar: con **1 worker** tarda **14,78 ± 0,26 s** (base `1,00×`, `100 %` de eficiencia); con **2 workers** baja a **11,09 ± 0,05 s** (`1,33×`, `66,6 %`); y con **3 workers** baja a **9,18 ± 0,13 s** (`1,61×`, `53,6 %`).
>
> La brecha creciente entre la curva verde real y la punteada ideal se explica con el panel inferior derecho de la **Ley de Amdahl** (`S(p) = 1 / ((1 − f) + f/p)`): la fracción secuencial —lectura del CSV, *shuffle* en red y *collect* en el driver— limita cuánto puede acelerar el paralelismo."

### Diapositiva 18 — Demo 2 · k3s: escalado y self-healing *(13:20 – 14:30)*
> *(Hacé **clic sobre el video** o ejecutá el Bloque 3 de `./scripts/demo_en_vivo.sh` siguiendo los pasos de la izquierda.)*
>
> "En este video sobre nuestro clúster k3d de tres nodos (`1 server + 2 agents`) mostramos dos pruebas en vivo:
> - **E3 (Escalado):** partimos de 1 pod activo y ejecutamos `kubectl scale --replicas=5`. Como se ve en la salida de `kubectl get pods -o wide`, en unos **3 segundos** los 5 pods quedan en `Running` distribuidos entre `agent-0`, `agent-1` y `server-0`.
> - **E4 (Self-healing):** luego borramos uno de los pods a propósito con `kubectl delete pod`. Al instante siguiente `get pods` muestra que el `ReplicaSet` detectó la falta y levantó un pod nuevo de reemplazo (con nuevo sufijo) en **menos de 2 segundos**, sin intervención manual."

### Diapositiva 19 — Demo 3 · Spark e idempotencia *(14:30 – 15:30)*
> *(Hacé **clic sobre el video** o ejecutá los Bloques 2 y 4 de `./scripts/demo_en_vivo.sh`.)*
>
> "Aquí en el video validamos procesamiento e infraestructura como código:
> - Arriba se ve la tabla de salida del job `batch_analysis.py` en Spark sobre **1 millón de lecturas** —calculando lecturas, promedio de pH, conductividad, temperatura y alertas por cada zona (`zona_1` a `zona_5`) en **5,39 s** de cómputo—, seguido del mismo pipeline en Hadoop Streaming (**4,09 s**).
> - Después ejecutamos `ansible-playbook playbook.yml` por segunda vez: en el `PLAY RECAP` final se observa **`changed=0` y `failed=0`**, comprobando idempotencia estricta."

### Diapositiva 20 — E5 · Latencia del lazo cerrado *(15:30 – 16:20)*
> "En el gráfico de barras de la izquierda medimos la latencia real extremo a extremo (en milisegundos) a través de Mosquitto y el controlador en Docker para **1, 10 y 50 sensores** concurrentes. Las **barras verdes** representan la **Media** y las **barras ámbar** el **percentil 95 (P95)**.
>
> Como detalla la **tabla de la derecha**:
> - Con **1 sensor**: media **0,11 ± 0,22 ms** y P95 **0,49 ms**.
> - Con **10 sensores**: media **2,22 ± 1,46 ms** y P95 **4,56 ms**.
> - Con **50 sensores en ráfaga simultánea**: media **7,56 ± 7,03 ms** y P95 **19,56 ms** —el número que destacamos arriba a la derecha.
>
> El panel **VEREDICTO** resume por qué esto es suficiente: el 95 % de las reacciones ocurre en **menos de 20 ms**, apto para tiempo real blando frente a las variables lentas de un cultivo hidropónico."

### Diapositiva 21 — Resumen `tail -f resultados.log` *(16:20 – 16:50)*
> "En resumen, cada número responde a un pilar: **3,86×** de Spark en E1, **1,61×** de speedup en E2, escalado en **~3 s** en E3, recuperación en **menos de 2 s** en E4, **19,56 ms** de P95 en E5 y **changed=0** en Ansible."
>
> `[Handoff → Persona 1 en Diapositiva 22]`

---

## Bloque C — Conclusiones técnicas (17:20 – 17:50)

> *(En Diapositiva 22 `05 // CIERRE`, Persona 1 introduce el cierre y luego cubre la columna verde de Diapositiva 23.)*

### Diapositiva 23 — Conclusiones, columna ámbar *(17:20 – 17:50 · después de Persona 1)*
> "Desde el procesamiento y la resiliencia:
> - Spark supera **3,86×** a Python y **4,30×** a Hadoop con 10 millones de filas.
> - Su escalabilidad respeta la Ley de Amdahl.
> - k3s se recupera solo en menos de 2 segundos, y Ansible hace que el despliegue sea reproducible e idempotente.
>
> Nuestra tesis queda abajo: un diseño distribuido convierte un cultivo frágil en un sistema autónomo, medible y resiliente.
>
> **[Nombre Persona 1]** cierra con el trabajo futuro."
>
> `[Handoff → Persona 1 en Diapositiva 24]`
