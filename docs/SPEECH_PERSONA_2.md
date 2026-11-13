# Guion de Exposición Oral — PERSONA 2

> **Rol en la defensa:** Orquestación (k3s / k3d), Mensajería MQTT, Motores Big Data (Hadoop vs. Spark), Análisis de Experimentos E1–E5, **Demostración en Vivo 2 (k3s + Spark + Ansible)** y Conclusiones Técnicas.  
> **Duración estimada de intervención:** ~9 minutos (alternada con Persona 1 para un total de 17–18 minutos).

---

## Bloque A: Marco Teórico II y III — Orquestación, MQTT y Big Data (Minutos 4:30 a 7:30)

> *(Toma la palabra Persona 2 tras Diapositiva 4 de Persona 1)*

### Diapositiva 5 — Marco Teórico II: Orquestación (k8s / k3s) y Mensajería MQTT *(4:30 – 6:00)*
> `[Avanzar a Diapositiva 5]`
>
> "Muchas gracias. Continuando con las capas superiores de nuestra arquitectura, en un entorno distribuido real no podemos administrar contenedores de forma manual; necesitamos **orquestación**.
>
> Kubernetes provee el plano de control para gestionar **Pods**, **Deployments** y **Services**, realizando reconciliación continua: si declaramos que debe haber cinco réplicas activas y una falla, el controlador la reemplaza automáticamente. Sin embargo, un clúster Kubernetes tradicional demanda varios gigabytes de RAM solo para sus servicios de control.
>
> Por eso elegimos **k3s** desplegado mediante **k3d**, una distribución certificada por la CNCF que reduce drásticamente el consumo de memoria y nos permitió crear dentro de Docker un clúster de **tres nodos** —un servidor *control-plane* y dos nodos agentes *workers*— conservando exactamente las mismas abstracciones y comandos `kubectl` que un entorno productivo.
>
> En cuanto a la comunicación entre sensores y consumidores, adoptamos el protocolo **MQTT** con **Eclipse Mosquitto**. Frente a HTTP tradicional, MQTT trabaja mediante publicación/suscripción sobre TCP con cabeceras mínimas y garantiza tres niveles de desacoplamiento —espacial, temporal y de sincronización— utilizando **QoS 1** (*al menos una vez*) para asegurar que ninguna alerta crítica se pierda en tránsito."

---

### Diapositiva 6 — Marco Teórico III: Hadoop MapReduce vs. Apache Spark *(6:00 – 7:30)*
> `[Avanzar a Diapositiva 6]`
>
> "Por último, para analizar grandes volúmenes históricos de telemetría hidropónica comparamos dos paradigmas clásicos de procesamiento distribuido:
> - Por un lado, **Apache Hadoop MapReduce**, que divide cualquier cómputo en fases de *Map*, ordenamiento *Shuffle* y *Reduce*. Su limitación histórica es que entre etapas persiste los resultados intermedios en disco, lo cual introduce una penalización severa de entrada/salida. Para este laboratorio implementamos un pipeline de *Hadoop Streaming* en Python ejecutando exactamente la misma lógica de agregación.
> - Por otro lado, **Apache Spark**, que supera esa barrera procesando datos en **memoria RAM distribuida** mediante DataFrames y el optimizador **Catalyst**, y además nos permite procesar eventos en tiempo real con **Structured Streaming** vigilando los archivos JSON generados por nuestro recolector.
>
> Le devuelvo la palabra a **[Nombre Persona 1]** para que muestre cómo se integra todo esto en la arquitectura del sistema y nos muestre la primera demostración en vivo."
>
> `[Handoff -> Toma la palabra Persona 1 en Diapositiva 7]`

---

## Bloque B: Experimentos E1–E5 y DEMO EN VIVO 2 (Minutos 11:30 a 16:45)

> *(Retoma la palabra Persona 2 tras la Demo 1 de Persona 1 en Diapositiva 9)*

### Diapositiva 10 — Experimento E1: Rendimiento según Volumen (1M vs. 10M) *(11:30 – 12:45)*
> `[Avanzar a Diapositiva 10]`
>
> "Excelente, ya vimos la capa IoT funcionando en tiempo real. Ahora pasemos a los resultados cuantitativos de la campaña experimental, donde cada medición fue repetida **3 veces** en procesos aislados reportando media y desvío estándar.
>
> En la **Figura 1** tenemos el Experimento E1, comparando **Python secuencial**, **Hadoop Streaming** y **Apache Spark** al procesar 1 millón y 10 millones de lecturas sintéticas:
> - Fíjense en un detalle muy interesante en **1 millón de registros**: Python secuencial fue el más rápido (**3,28 segundos**), seguido de Hadoop (**4,21 segundos**) y Spark (**5,37 segundos** de cómputo). ¿Por qué ocurre esto? Porque en volúmenes pequeños, el costo fijo de inicializar la JVM, repartir particiones y planificar el DAG en Spark no se llega a amortizar.
> - Pero miren lo que sucede al multiplicar por diez el volumen, pasando a **10 millones de registros**: mientras Python escala linealmente a **34,20 segundos** y Hadoop sube a **38,09 segundos** por el cuello de botella del ordenamiento en tuberías, **Apache Spark resuelve los 10 millones de filas en apenas 8,86 segundos**. Eso significa que en 10 millones de registros Spark ya es **3,86 veces más rápido que Python** y **4,30 veces más rápido que Hadoop**."

---

### Diapositiva 11 — Experimento E2: Escalabilidad de Spark y Ley de Amdahl *(12:45 – 13:45)*
> `[Avanzar a Diapositiva 11]`
>
> "En el Experimento E2 medimos cómo escala Spark sobre el dataset de 10 millones al asignar **1, 2 y 3 workers**.
>
> Como se observa en la **Figura 2**:
> - Con **1 worker**, el cómputo tarda **14,78 segundos** (base $1,00\times$).
> - Con **2 workers**, baja a **11,09 segundos**, logrando un *Speedup* de **$1,33\times$** y una eficiencia paralela del **66,6 %**.
> - Con **3 workers**, baja a **9,18 segundos**, alcanzando un *Speedup* de **$1,61\times$** y una eficiencia del **53,6 %**.
>
> ¿Por qué la curva real se separa de la línea punteada del *Speedup* ideal? Es la demostración empírica directa de la **Ley de Amdahl**: todo algoritmo distribuido tiene una fracción secuencial irreducible —en nuestro caso la lectura inicial del CSV, la coordinación del driver y la etapa de *shuffle* entre particiones—, por lo que al agregar más workers la ganancia marginal disminuye de forma cóncava."

---

### Diapositiva 12 — DEMO EN VIVO 2 + E3 & E4: Orquestación k3s, Tolerancia a Fallos y Ansible *(13:45 – 15:45)*
> `[Avanzar a Diapositiva 12 — Cambiar a la Terminal]`
>
> *(Nota operativa: Continuar `./scripts/demo_en_vivo.sh` con Bloques 2, 3 y 4. Si hay algún inconveniente en vivo, reproducir `docs/videos/02_demo_k3s_escalado_tolerancia.mp4` y `03_demo_spark_hadoop_ansible.mp4`).*
>
> "Pasemos a la segunda demostración en vivo para comprobar el procesamiento en Spark, la orquestación en k3s y la idempotencia en Ansible."
>
> *(Ejecutar Bloque 2 — Spark sobre 1M)*
> "Aquí vemos el job de PySpark calculando exactamente los promedios de pH, conductividad, temperatura y conteo de alertas por cada zona de cultivo."
>
> *(Ejecutar Bloque 3 — k3s / k3d)*
> "Ahora miramos nuestro clúster k3s de tres nodos (`1 server` y `2 agents`) ya levantado con `k3d`. Desplegamos el simulador con 1 réplica y lo escalamos a **5 réplicas** con `kubectl scale`."
> *(Mostrar `kubectl get pods` con los 5 pods en estado `Running`)*
> "En apenas ~3 segundos Kubernetes distribuyó las 5 réplicas entre los nodos agentes.
>
> Ahora simulamos una falla crítica en producción: **eliminamos deliberadamente uno de los pods** con `kubectl delete pod`..."
> *(Ejecutar `kubectl delete pod ...` y luego `kubectl get pods`)*
> "Como pueden ver inmediatamente, el controlador `ReplicaSet` detectó la desviación respecto al estado deseado y levantó un pod sustituto nuevo en **menos de 2 segundos**, manteniendo el sistema operativo sin intervención manual (*self-healing*)."
>
> *(Ejecutar Bloque 4 — Ansible)*
> "Y finalmente ejecutamos nuestro playbook de **Ansible** por segunda vez: observen el resumen final `changed=0`. Esto demuestra **idempotencia**, garantizando que la infraestructura queda exactamente en el estado esperado sin efectos colaterales al re-ejecutarse."

---

### Diapositiva 13 — Experimento E5: Latencia Fin-a-Fin del Controlador *(15:45 – 16:45)*
> `[Avanzar a Diapositiva 13 — Volver a las Diapositivas]`
>
> "Para validar el comportamiento en tiempo real del lazo cerrado bajo carga creciente, en el Experimento E5 medimos la latencia real a través del broker Mosquitto variando entre **1, 10 y 50 sensores concurrentes** disparando anomalías simultáneas:
> - Con **1 sensor**, la latencia media fue de apenas **0,11 ms** (percentil 95 de **0,49 ms**).
> - Con **10 sensores**, la media subió a **2,22 ms** (P95 de **4,56 ms**).
> - Con **50 sensores** disparando en ráfaga simultánea, la media fue de **7,56 ms** (P95 de **19,56 ms**).
>
> En todos los escenarios, la respuesta ante una anomalía crítica se ejecuta en el orden de pocos milisegundos, lo cual es órdenes de magnitud más rápido que las constantes de tiempo biológicas y químicas de un cultivo hidropónico."

---

## Bloque C: Cierre Técnico (Minutos 17:15 a 17:45)

> *(Tras la intervención de Persona 1 en Diapositiva 14)*

### Diapositiva 14 — Conclusiones *(Parte 2: 17:15 – 17:45)*
> "Complementando las conclusiones, desde la perspectiva de procesamiento y resiliencia comprobamos tres puntos clave:
> - **Big Data en memoria:** Apache Spark mostró una clara ventaja a partir de los 10 millones de registros, aunque su eficiencia paralela está sujeta a la Ley de Amdahl.
> - **Orquestación resiliente:** k3s con k3d permitió validar escalado elástico y autorrecuperación de pods en menos de dos segundos.
> - **Reproducibilidad:** Ansible y la generación determinista con semilla fija aseguran que cualquier docente o investigador pueda reproducir exactamente estos mismos resultados paso a paso.
>
> Le devuelvo la palabra a **[Nombre Persona 1]** para cerrar con las líneas de trabajo futuro."
>
> `[Handoff -> Toma la palabra Persona 1 en Diapositiva 15]`

