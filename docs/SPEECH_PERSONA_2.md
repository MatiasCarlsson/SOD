# Guion de Exposición Oral — PERSONA 2 (Versión Explicada y Detallada)

> **Rol en la defensa:** Orquestación en Kubernetes ligero (k3s sobre k3d), mensajería MQTT (Mosquitto), comparativa de Big Data (Hadoop MapReduce vs. Apache Spark), análisis completo de la campaña experimental (**E1, E2, E3, E4 y E5**), **Demo 2 (k3s)**, **Demo 3 (Spark + Ansible)** y conclusiones de datos y resiliencia.  
> **Presentación:** `docs/Presentacion_TIF_SOD_2026.pptx` (24 diapositivas, estilo *Textmode Overlay*, transición *fade* y videos MP4 embebidos).  
> **Duración estimada de tu parte:** ~9 minutos (alternando con Persona 1 para un total de 17–18 minutos).  
> **Pista visual en pantalla:** arriba a la derecha, **`[ Persona 2 ]` en ámbar** indica tus diapositivas; **`[ Persona 1 + 2 ]` en blanco** cuando comparten el cierre.

---

## Bloque A — Orquestación (k3s), Mensajería (MQTT) y Big Data (4:40 – 7:20)

> *(Tomás la palabra después de que Persona 1 termina la Diapositiva 7 sobre KVM vs. Docker)*

### Diapositiva 8 — `> Orquestación con k3s sobre k3d` *(4:40 – 5:35)*
**Qué se ve en pantalla:** Izquierda: panel `CONCEPTOS` (modelo declarativo, bucle de reconciliación, k3s `< 512 MB`, k3d en Docker). Derecha: panel `TOPOLOGÍA DEL LAB` con el árbol `server-0 (control plane)` → `agent-0` y `agent-1` (`pods ▪ ▪ ▪`) y nota `sensor-simulator → MQTT vía host.k3d.internal:1883`.

**Conceptos clave para entender antes de hablar:**
- **Orquestación declarativa:** En vez de correr comandos manuales como `docker run` uno por uno, escribimos un archivo YAML donde declaramos *"quiero 5 réplicas de este sensor siempre activas"*.
- **Pod, Deployment y ReplicaSet:** En Kubernetes, un **Pod** es la cajita mínima que envuelve a nuestro contenedor; el **ReplicaSet** es el vigilante que cuenta cuántos pods hay vivos en todo momento; y el **Deployment** gestiona las versiones y actualizaciones de esos pods.
- **Bucle de reconciliación:** Es un ciclo infinito del plano de control que compara el *estado real* (ej. "hay 4 pods vivos porque uno falló") contra el *estado deseado* ("el YAML dice 5") y crea el pod faltante automáticamente.
- **k3s y k3d:** Kubernetes común (k8s) es muy pesado porque usa una base de datos distribuida llamada `etcd` que consume gigabytes de RAM. **k3s** es una versión oficial liviana que reemplaza `etcd` por `SQLite` y gasta menos de 512 MB. Y **k3d** es la herramienta que nos permite simular varios servidores de un clúster k3s metiendo cada nodo dentro de un contenedor Docker.

**Qué decir:**
> "Muchas gracias. Una vez que tenemos contenedores en Docker, aparece el siguiente problema: en un sistema distribuido con decenas de sensores no podemos levantar o reiniciar contenedores a mano cada vez que uno falla. Necesitamos un **orquestador**, y el estándar en la industria es **Kubernetes**.
>
> Como vemos en el panel izquierdo **CONCEPTOS**:
> - Kubernetes trabaja con un **modelo declarativo**: nosotros no le damos órdenes paso a paso, sino que le entregamos un manifiesto diciendo cuál es el *estado deseado* —por ejemplo, *'quiero 5 pods del sensor corriendo'*— a través de objetos como **Deployments**, **ReplicaSets**, **Pods** y **Services**.
> - El corazón de Kubernetes es su **bucle de reconciliación**: el plano de control compara todo el tiempo el estado real contra el deseado; si un pod cae, crea otro automáticamente para volver a coincidir.
> - Como un clúster Kubernetes tradicional consume más de 2 GB de RAM solo para administrarse, elegimos **k3s**, una distribución liviana certificada que reemplaza la base de datos `etcd` por **SQLite**, reduciendo el consumo a **menos de 512 MB de RAM**. Y para no necesitar tres computadoras físicas, usamos **k3d**, que ejecuta cada nodo del clúster k3s dentro de contenedores Docker.
>
> En el diagrama de la derecha (**TOPOLOGÍA DEL LAB**) se ve exactamente cómo armamos nuestro clúster de **3 nodos**: arriba tenemos a **`server-0`**, que actúa como plano de control (*control plane* con el API Server y el planificador), y abajo cuelgan dos nodos trabajadores, **`agent-0`** y **`agent-1`**, donde se reparten los pods simuladores. Además, configuramos el puente DNS **`host.k3d.internal:1883`** para que los pods que viven dentro de la red de Kubernetes puedan publicar sus lecturas hacia el broker Mosquitto que corre en el host."

---

### Diapositiva 9 — `> Mensajería MQTT (Mosquitto)` *(5:35 – 6:20)*
**Qué se ve en pantalla:** Diagrama superior `SENSORES (publish) ──► MOSQUITTO (:1883) ──► SUSCRIPTORES (subscribe)` con el tópico `hidroponia/+/telemetria → controlador · recolector`. Abajo: 4 paneles (`ESPACIO`, `TIEMPO`, `LIVIANO`, `QoS 1`).

**Conceptos clave para entender:**
- **Tópico con comodín (`hidroponia/+/telemetria`):** En MQTT los mensajes se envían a "canales" llamados tópicos, como carpetas (`hidroponia/zona_1/telemetria`, `hidroponia/zona_2/telemetria`). El signo **`+`** es un comodín de un nivel: al suscribirse a `hidroponia/+/telemetria`, el controlador escucha todas las zonas a la vez sin importar cuántas agreguemos.
- **QoS 1 (Calidad de Servicio 1) y PUBACK:** MQTT tiene 3 niveles: QoS 0 ("disparar y olvidar", se puede perder), **QoS 1 ("al menos una vez")**, donde quien recibe devuelve un paquete de confirmación llamado **`PUBACK`** (si no llega el `PUBACK`, se reenvía), y QoS 2 ("exactamente una vez", más lento).

**Qué decir:**
> "¿Y cómo se comunican esos sensores con el resto del sistema? En lugar de usar peticiones HTTP directas —que obligan a conocer la IP del receptor y tienen cabeceras de texto pesadas—, implementamos el protocolo **MQTT** utilizando el broker **Eclipse Mosquitto**.
>
> En el diagrama superior vemos el flujo: a la izquierda los **Sensores** únicamente hacen `publish` hacia **Mosquitto** en el puerto `1883`, y a la derecha los **Suscriptores** —tanto nuestro controlador como el recolector— hacen `subscribe` al tópico con comodín **`hidroponia/+/telemetria`**, donde el signo `+` les permite escuchar automáticamente a cualquier zona nueva que se sume al cultivo.
>
> Abajo vemos las cuatro propiedades que nos da este diseño:
> 1. **Desacoplamiento en Espacio:** sensores y consumidores no conocen las direcciones IP de los demás; solo conocen al broker.
> 2. **Desacoplamiento en Tiempo:** emisor y receptor no necesitan estar ejecutándose en el mismo microsegundo ni bloquearse esperando respuesta.
> 3. **Protocolo Liviano:** una cabecera mínima de apenas 2 bytes frente a cientos de bytes de HTTP, ideal para enviar telemetría cada 1 segundo (1 Hz).
> 4. **Calidad de Servicio `QoS 1`:** exige un acuse de recibo llamado **`PUBACK`**, garantizando que cada lectura llegue *al menos una vez* y que ninguna alerta crítica de pH se pierda en la red."

---

### Diapositiva 10 — `> Hadoop MapReduce vs. Apache Spark` *(6:20 – 7:20)*
**Qué se ve en pantalla:** Izquierda: panel `HADOOP STREAMING` (`Map ─► [disco] ─► Shuffle ─► Reduce`). Derecha: panel `APACHE SPARK` (`DAG ─► [RAM] ─► Catalyst ─► Acción`). Abajo: panel ámbar `COMPARACIÓN JUSTA`.

**Conceptos clave para entender:**
- **Map, Shuffle y Reduce (Hadoop):** *Map* lee cada fila del archivo y extrae pares clave-valor (ej. `zona_1 → pH 6,2`); *Shuffle* agrupa y ordena en disco todos los datos de la misma zona; *Reduce* calcula el promedio final por zona. El problema es que entre cada paso escribe y lee del disco duro (**I/O bound**).
- **DAG y Catalyst (Spark):** En lugar de ejecutar paso a paso escribiendo en disco, Spark arma un **DAG** (*Grafo Acíclico Dirigido*, una receta completa de todas las operaciones) en **memoria RAM** y su optimizador **Catalyst** reordena y simplifica las cuentas antes de tocar los datos.

**Qué decir:**
> "El tercer pilar teórico es cómo procesamos millones de lecturas históricas para obtener estadísticas del cultivo. Aquí contrastamos dos generaciones de procesamiento distribuido:
> - En el panel izquierdo vemos **Hadoop MapReduce**, implementado mediante *Hadoop Streaming* con scripts en Python (`mapper.py` y `reducer.py`). Como muestra su diagrama superior (`Map → [disco] → Shuffle → Reduce`), el modelo divide la tarea en una fase *Map* que filtra cada lectura, una fase *Shuffle* que ordena y agrupa por zona, y una fase *Reduce* que promedia. Su gran cuello de botella es ese bloque rojo **`[disco]`**: vuelca los resultados intermedios al almacenamiento entre etapas, sufriendo una fuerte penalidad de entrada/salida.
> - En el panel derecho vemos **Apache Spark**: su diagrama (`DAG → [RAM] → Catalyst → Acción`) muestra que mantiene los datos distribuidos en **memoria RAM** mediante *DataFrames*. En vez de ir a disco en cada paso, construye un grafo de ejecución (**DAG**) optimizado por el motor **Catalyst**, y además nos permite usar exactamente la misma API tanto para lotes históricos (*Batch*) como para flujo continuo (*Structured Streaming*).
>
> Y como destaca el cuadro inferior **COMPARACIÓN JUSTA**, para que nuestros benchmarks sean totalmente limpios, programamos en los tres motores —Python secuencial, Hadoop Streaming y Spark— **exactamente el mismo cálculo matemático**: promedio de pH, conductividad y temperatura por zona más el conteo total de alertas.
>
> Le devuelvo la palabra a **[Nombre Persona 1]** para ver la arquitectura integrada y la primera demostración."
>
> `[Handoff → Toma la palabra Persona 1 en Diapositiva 11]`

---

## Bloque B — Campaña Experimental (E1–E5) y Demos 2 y 3 (11:00 – 16:50)

> *(Retomás la palabra después de que Persona 1 termina la Demo 1 en la Diapositiva 14)*

### Diapositiva 15 — Separador `04 // RESULTADOS` *(11:00 – 11:10)*
**Qué se ve en pantalla:** Número `04`, barra de progreso al `60%` y comando `$ make benchmark && make analyze`.

**Qué decir:**
> "Pasamos ahora al cuarto bloque: los resultados de nuestra campaña experimental. Todas las pruebas que van a ver se ejecutaron **tres veces cada una** en subprocesos aislados, reportando la media y el desvío estándar."

---

### Diapositiva 16 — `> E1 · Rendimiento según volumen` *(11:10 – 12:20)*
**Qué se ve en pantalla:** Izquierda: gráfico de barras agrupadas `TIEMPO (s)` comparando `Python`, `Hadoop` y `Spark` con barras **verde oscuro (`1M filas`)** y **verde claro (`10M filas`)**. Derecha: cifras gigantes **`3,86×`** y **`4,30×`** + recuadro ámbar `PUNTO DE INFLEXIÓN`.

**Qué decir (señalando el gráfico):**
> "En el **Experimento E1** evaluamos cómo impacta el volumen de datos al pasar de **1 millón** (~61 MB) a **10 millones de lecturas** (~615 MB). En el gráfico de barras de la izquierda, el eje vertical mide el **tiempo de ejecución en segundos** —por lo tanto, **más bajo es mejor**—: las **barras verde oscuro** representan 1 millón de filas y las **barras verde claro** representan 10 millones.
>
> Fíjense primero en las barras bajas de **1 millón de filas**:
> - Aquí **gana Python secuencial con `3,28 segundos`**, seguido por Hadoop con `4,21 s`, mientras que Spark queda último con `5,37 s` de cómputo. ¿Por qué pierde Spark cuando hay pocos datos? Como explica el cuadro **PUNTO DE INFLEXIÓN** abajo a la derecha, Spark tiene un costo fijo inicial (*overhead*): tiene que levantar la máquina virtual de Java (JVM), inicializar el contexto distribuido, armar el plan en Catalyst y repartir tareas. Para un archivo chico, ese trámite tarda más que leerlo directo en Python.
>
> Pero miren las barras altas en **verde claro** cuando multiplicamos por diez el volumen a **10 millones de filas**:
> - Python escala linealmente por diez y se va a **`34,20 segundos`**.
> - Hadoop Streaming sufre con el ordenamiento por tuberías de entrada/salida y sube a **`38,09 segundos`**.
> - En cambio, **Apache Spark procesa los 10 millones de registros en apenas `8,86 segundos`**: el costo fijo ya se amortizó y el paralelismo en memoria hace la diferencia.
>
> Como resaltan los dos indicadores grandes de la derecha, en 10 millones de filas Spark es **`3,86 veces` más rápido que Python** y **`4,30 veces` más rápido que Hadoop**."

---

### Diapositiva 17 — `> E2 · Escalabilidad de Spark` *(12:20 – 13:20)*
**Qué se ve en pantalla:** Izquierda: gráfico de líneas `SPEEDUP` con curva **verde continua (`Real`: `1,00× → 1,33× → 1,61×`)** y curva **gris punteada (`Ideal`: `1,00× → 2,00× → 3,00×`)**. Derecha arriba: tabla con `Workers | Cómputo (μ ± σ) | Speedup | Efic.`. Derecha abajo: panel `LEY DE AMDAHL` con la ecuación `S(p) = 1 / ((1−f) + f/p)`.

**Conceptos clave para entender:**
- **Speedup (`S(p) = T(1) / T(p)`):** Cuántas veces más rápido termina el trabajo usando `p` workers comparado contra usar 1 solo worker. Si con 1 worker tarda `14,78 s` y con 3 tarda `9,18 s`, entonces `14,78 / 9,18 = 1,61×`.
- **Eficiencia paralela (`E(p) = Speedup / p`):** Qué porcentaje de la capacidad de cada worker se transforma realmente en velocidad (`1,61 / 3 = 53,6 %`).
- **Ley de Amdahl:** En cualquier programa paralelo hay una parte paralelizable (`f`) y una parte secuencial (`1 - f`) que no se puede dividir (abrir el archivo, juntar los promedios en el nodo maestro, enviar datos por red). Esa parte secuencial hace que agregar workers rinda cada vez un poco menos.

**Qué decir (señalando gráfico, tabla y fórmula):**
> "Una vez demostrado que Spark gana en 10 millones de filas, en el **Experimento E2** nos preguntamos: *¿qué pasa si a ese mismo dataset de 10 millones lo procesamos con 1, 2 y 3 workers en paralelo?*
>
> En la **tabla de arriba a la derecha** vemos las mediciones exactas con su desvío estándar:
> - Con **1 worker**, el cómputo tarda **`14,78 ± 0,26 segundos`** (nuestro punto de partida: speedup `1,00×` y eficiencia `100 %`).
> - Al pasar a **2 workers**, el tiempo baja a **`11,09 ± 0,05 segundos`**, logrando un speedup de **`1,33×`** y una eficiencia del **`66,6 %`**.
> - Y con **3 workers**, el tiempo desciende a **`9,18 ± 0,13 segundos`**, alcanzando un speedup de **`1,61×`** y una eficiencia del **`53,6 %`**.
>
> Si miran el **gráfico de líneas de la izquierda**, la línea **gris punteada** muestra el mundo ideal (donde 2 workers irían al doble de velocidad, `2,00×`, y 3 workers al triple, `3,00×`), mientras que la **línea verde continua** muestra nuestro speedup real (`1,00× → 1,33× → 1,61×`).
>
> ¿Por qué la curva verde se aplana y se separa del ideal? Como muestra el recuadro inferior derecho, es la verificación empírica de la **Ley de Amdahl** (`S(p) = 1 / ((1−f) + f/p)`): en todo sistema distribuido existe una fracción secuencial irreducible `(1 − f)` que no se puede paralelizar —en nuestro caso la lectura inicial del archivo CSV, el intercambio de datos por red durante el *shuffle* para agrupar por zona y el `collect` final en el *driver*—, lo que pone un techo físico a la aceleración."

---

### Diapositiva 18 — `> Demo 2 · k3s: escalado y self-healing` *(13:20 – 14:30)*
**Qué se ve en pantalla:** Izquierda: panel `PASOS` (`k3d cluster: 1 server + 2 agents`, `kubectl scale --replicas=5 (~3 s)`, `kubectl delete pod → ReplicaSet lo recrea en < 2 s`, `kubectl get pods -o wide`). Derecha: video embebido `02_demo_k3s_escalado_tolerancia.mp4`.

**Qué hacer:** Hacer **clic sobre el video** para reproducirlo (dura 23 segundos) o ejecutar el Bloque 3 de `./scripts/demo_en_vivo.sh`.

**Qué decir mientras corre el video:**
> "Pasemos a la **Demostración 2**, donde ejecutamos en vivo los **Experimentos E3 (escalado horizontal)** y **E4 (tolerancia a fallos)** sobre nuestro clúster k3s de tres nodos (`server-0`, `agent-0` y `agent-1`).
>
> Siguiendo los pasos de la izquierda en el video:
> 1. Primero verificamos los 3 nodos del clúster con `kubectl get nodes` y vemos que inicialmente hay **1 solo pod** del simulador corriendo.
> 2. Ahí ejecutamos el **Experimento E3**: lanzamos `kubectl scale deployment sensor-simulator --replicas=5`. Observen en la tabla de `kubectl get pods -o wide` cómo en apenas **3 segundos** ya tenemos las **5 réplicas en estado `Running` (`1/1`)**, y si miran la columna `NODE` a la derecha de la tabla, el planificador de Kubernetes las repartió automáticamente entre `agent-0`, `agent-1` y `server-0`.
> 3. Inmediatamente después probamos el **Experimento E4 (tolerancia a fallos)**: simulamos la caída abrupta de un nodo eliminando un pod con `kubectl delete pod --now`.
> 4. Y cuando listamos los pods un instante después, vemos que siguen habiendo **5 pods activos**: el `ReplicaSet` detectó al instante que había 4 en lugar de 5 y creó un pod sustituto nuevo en **menos de 2 segundos**. Esto es *self-healing* real: el sistema se curó solo sin que ningún operador humano interviniera."

---

### Diapositiva 19 — `> Demo 3 · Spark e idempotencia` *(14:30 – 15:30)*
**Qué se ve en pantalla:** Izquierda: panel `PASOS` (`spark batch_analysis.py (1M) → 5,39 s`, `run_hadoop_job.py (1M) → 4,09 s`, `ansible-playbook playbook.yml`, `PLAY RECAP → changed=0`). Derecha: video embebido `03_demo_spark_hadoop_ansible.mp4`.

**Concepto clave para entender:**
- **Idempotencia (en Ansible):** Propiedad matemática y de ingeniería según la cual aplicar una operación una vez o diez veces seguidas produce exactamente el mismo estado final, sin duplicar configuraciones ni romper lo que ya estaba bien. En Ansible se comprueba viendo **`changed=0`** en el resumen final (`PLAY RECAP`).

**Qué hacer:** Hacer **clic sobre el video** para reproducirlo (dura 20 segundos) o ejecutar los Bloques 2 y 4 de `./scripts/demo_en_vivo.sh`.

**Qué decir mientras corre el video:**
> "En la **Demostración 3** mostramos dos cosas: la equivalencia analítica entre Spark y Hadoop, y la automatización con Ansible:
> 1. En la primera mitad del video lanzamos el trabajo de **Apache Spark (`batch_analysis.py`)** sobre el dataset de **1 millón de lecturas**. Ahí aparece la tabla de resultados con las 5 zonas del cultivo (`zona_1` a `zona_5`), mostrando alrededor de 200.000 lecturas por zona, los promedios exactos de pH (`~6,06`), conductividad (`~1,80`), temperatura (`~21 °C`) y unas 60.000 alertas por zona, completando el cómputo en **`5,39 segundos`**.
> 2. Justo debajo ejecutamos el mismo cálculo con **Hadoop Streaming (`run_hadoop_job.py`)**, que arroja **exactamente los mismos números** en **`4,09 segundos`** —confirmando en vivo lo que vimos en el gráfico E1 para volúmenes de 1 millón—.
> 3. Y en la segunda mitad del video ejecutamos nuestro playbook de **Ansible (`ansible-playbook playbook.yml`)**. Ansible revisa paquetes, el demonio de Docker, los directorios de datos y el archivo `mosquitto.conf`. Como el entorno ya estaba configurado, miren la última línea del **`PLAY RECAP`**: dice **`ok=8, changed=0, failed=0`**. Ese **`changed=0`** demuestra **idempotencia estricta**: podemos correr el aprovisionamiento todas las veces que queramos con la certeza de que no altera nada que ya esté en el estado correcto."

---

### Diapositiva 20 — `> E5 · Latencia del lazo cerrado` *(15:30 – 16:20)*
**Qué se ve en pantalla:** Izquierda: gráfico de barras agrupadas `LATENCIA (ms)` para `1 sensor`, `10 sensores` y `50 sensores` con **barras verdes (`Media`)** y **barras ámbar (`P95`)**. Derecha arriba: cifra destacada **`19,56 ms`** (`P95 con 50 sensores concurrentes`). Derecha medio: tabla con `Sensores | μ ± σ (ms) | P95`. Derecha abajo: panel `VEREDICTO`.

**Conceptos clave para entender:**
- **Percentil 95 (P95):** Si ordenamos 100 mediciones de menor a mayor, el P95 es el valor número 95. Significa que **el 95 % de las veces el sistema responde en ese tiempo o menos**. En sistemas de tiempo real es mucho más importante que el promedio, porque el promedio puede esconder demoras.
- **Tiempo real blando (*soft real-time*):** Un sistema donde responder en milisegundos es deseable y necesario para la calidad del control, pero donde una variación de 5 o 15 ms no produce una catástrofe física instantánea (porque la química del agua en un tanque cambia a lo largo de minutos).

**Qué decir (señalando el gráfico y la tabla):**
> "El último experimento cuantitativo es el **E5**, donde medimos la **latencia real extremo a extremo del lazo cerrado**: cuánto tarda en viajar una anomalía desde el sensor, pasar por el broker Mosquitto, ser evaluada por el contenedor controlador y salir como orden hacia el actuador.
>
> En el gráfico de la izquierda, las **barras verdes** muestran la **latencia media** y las **barras ámbar** muestran el **Percentil 95 (P95)** —es decir, el tiempo máximo dentro del cual se resuelve el 95 % de las alertas— al estresar el broker con **1, 10 y 50 sensores disparando ráfagas al mismo tiempo**:
> - Como detalla la tabla de la derecha, con **1 sensor** la reacción es casi instantánea: media de **`0,11 ± 0,22 ms`** y P95 de **`0,49 ms`** (menos de medio milisegundo).
> - Con **10 sensores concurrentes** (150 anomalías), la media es de **`2,22 ± 1,46 ms`** y el P95 de **`4,56 ms`**.
> - Y en el escenario de estrés con **50 sensores disparando en simultáneo** (750 anomalías en ráfaga), la media es de **`7,56 ± 7,03 ms`** y el P95 llega a **`19,56 ms`**, el valor destacado arriba a la derecha.
>
> Como concluye el recuadro **VEREDICTO**, incluso bajo una tormenta de 50 sensores concurrentes, **el 95 % de las órdenes correctivas se emite en menos de 20 milisegundos**. Tratándose de un cultivo hidropónico donde el pH y el nivel de agua evolucionan en escalas de minutos, esta arquitectura cumple de sobra con los requisitos de **tiempo real blando**."

---

### Diapositiva 21 — `> tail -f resultados.log` (Resumen de Experimentos) *(16:20 – 16:50)*
**Qué se ve en pantalla:** Grilla de 6 tarjetas KPI (`E1: 3,86×`, `E2: 1,61×`, `E3: ~3 s`, `E4: < 2 s`, `E5: 19,56 ms`, `IaC: changed=0`).

**Qué decir:**
> "En esta pantalla resumimos de un vistazo los seis indicadores que dejó toda la campaña experimental:
> - **E1 (`3,86×`):** la ventaja de Spark sobre Python (y `4,30×` sobre Hadoop) al escalar a 10 millones de filas.
> - **E2 (`1,61×`):** la aceleración real con 3 workers (eficiencia del `53,6 %`), explicada por la Ley de Amdahl.
> - **E3 (`~3 s`):** el tiempo que tarda k3s en escalar horizontalmente a 5 réplicas.
> - **E4 (`< 2 s`):** el tiempo de autorrecuperación (*self-healing*) cuando cae un pod.
> - **E5 (`19,56 ms`):** el percentil 95 de latencia de control con 50 sensores concurrentes.
> - **E IaC (`changed=0`):** la garantía de idempotencia de nuestro playbook en Ansible.
>
> Le doy paso a **[Nombre Persona 1]** para iniciar el bloque de cierre."
>
> `[Handoff → Persona 1 presenta el separador en Diapositiva 22 y la columna verde de Diapositiva 23]`

---

## Bloque C — Conclusiones Técnicas (17:20 – 17:50)

> *(En la Diapositiva 22 Persona 1 presenta el cierre y en la Diapositiva 23 explica la columna izquierda verde; luego intervenís vos en la misma Diapositiva 23)*

### Diapositiva 23 — `> Conclusiones` *(Parte 2, columna ámbar: 17:20 – 17:50)*
**Qué se ve en pantalla:** Columna derecha ámbar `DATOS + RESILIENCIA · P2` y recuadro inferior `$ echo $TESIS`.

**Qué decir:**
> "Complementando desde el lado del **procesamiento de datos y la resiliencia** en el panel derecho:
> - **Primero:** comprobamos empíricamente el punto de inflexión de **Apache Spark**: mientras que en volúmenes chicos pesa el arranque de la JVM, en 10 millones de registros su motor en memoria supera por **`3,86×` a Python** y **`4,30×` a Hadoop Streaming**.
> - **Segundo:** verificamos que el escalado paralelo no es infinito sino que obedece a la **Ley de Amdahl**, acotado por las etapas secuenciales de lectura, *shuffle* y recolección en el *driver*.
> - **Y tercero:** demostramos que **k3s** aporta tolerancia a fallos real recuperando pods caídos en **menos de 2 segundos**, mientras que **Ansible** asegura despliegues reproducibles e idempotentes con **`changed=0`**.
>
> En definitiva, como dice la línea inferior **`$ echo $TESIS`**: *un diseño distribuido convierte un cultivo biológicamente frágil en un sistema autónomo, medible y resiliente*.
>
> **[Nombre Persona 1]** cierra ahora con el trabajo futuro."
>
> `[Handoff → Persona 1 cierra en Diapositiva 24]`
