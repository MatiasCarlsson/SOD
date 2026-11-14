# Guion de Exposición Oral Unificado — PERSONA 1 + PERSONA 2 (Versión Completa y Detallada)

> **Presentación:** `docs/Presentacion_TIF_SOD_2026.pptx` (24 diapositivas, estilo *Textmode Overlay*, transición *fade* y videos MP4 embebidos).  
> **Duración total estimada:** ~18 minutos (~9 minutos Persona 1 + ~9 minutos Persona 2, en orden cronológico de la defensa).  
> **Distribución de roles:**
> - **`[Persona 1]`** *(verde arriba a la derecha en la diapositiva)*: Apertura, contexto agronómico (sistema hidropónico NFT), desafíos de Sistemas Operativos Distribuidos, objetivos, virtualización (Proxmox/KVM vs. Docker), arquitectura general, simulación de sensores y lazo cerrado, **Demo 1** y cierre (conclusiones de infraestructura + trabajo futuro).
> - **`[Persona 2]`** *(ámbar arriba a la derecha en la diapositiva)*: Orquestación en Kubernetes ligero (k3s sobre k3d), mensajería MQTT (Mosquitto), comparativa de Big Data (Hadoop MapReduce vs. Apache Spark), análisis completo de la campaña experimental (**E1, E2, E3, E4 y E5**), **Demo 2 (k3s)**, **Demo 3 (Spark + Ansible)** y conclusiones de datos y resiliencia.
> - **`[Persona 1 + 2]`** *(blanco)*: Diapositiva 23 de conclusiones compartidas.

---

## Bloque A — Apertura, Contexto Agronómico y Marco Teórico (0:00 – 7:20)

### Diapositiva 1 — Portada *(0:00 – 0:40)* · `[Persona 1]`
**Qué se ve en pantalla:** Líneas de arranque `[ OK ]` de los 4 subsistemas (`mosquitto`, `k3d`, `spark`, `ansible`), título principal y recuadro `TIF · AE 4`.

**Qué decir (`[Persona 1]`):**
> "Buenas tardes a los integrantes del tribunal y compañeros. Hoy vamos a presentar nuestro Trabajo Integrador Final de la cátedra de **Sistemas Operativos Distribuidos**, titulado *'Sistema automatizado de cultivo hidropónico distribuido'*.
>
> El equipo está integrado por **[Nombre Persona 2]** y quien les habla, **[Nombre Persona 1]**. En este proyecto integramos Internet de las Cosas con MQTT, contenedores Docker, orquestación con Kubernetes ligero (k3s), procesamiento paralelo con Hadoop y Apache Spark, y automatización con Ansible. Todo lo que van a ver a lo largo de la presentación —tanto las métricas como los gráficos y las demostraciones en video— proviene de ejecuciones y mediciones reales de nuestro laboratorio."

---

### Diapositiva 2 — Agenda `> ls -la ./defensa` *(0:40 – 1:10)* · `[Persona 1]`
**Qué se ve en pantalla:** Los 5 bloques de la defensa (`01 contexto/`, `02 teoria/`, `03 arquitectura/`, `04 resultados/`, `05 cierre/`) con el responsable (`P1`, `P2`) y el minuto de inicio.

**Qué decir (`[Persona 1]`):**
> "Organizamos la exposición en cinco bloques que recorren desde el problema real hasta la validación experimental:
> 1. Primero vamos a ver el **contexto agronómico** y por qué un cultivo hidropónico exige un sistema distribuido.
> 2. En el segundo bloque repasamos el **marco teórico** comparando máquinas virtuales contra contenedores, orquestación en k3s, mensajería MQTT y Hadoop frente a Spark.
> 3. En el tercer bloque mostramos la **arquitectura de nuestro laboratorio** y la **primera demostración** del lazo cerrado IoT.
> 4. En el cuarto bloque analizamos los **cinco experimentos cuantitativos (E1 a E5)** junto con las **demostraciones de k3s, Spark y Ansible**.
> 5. Y cerramos con las **conclusiones** y las líneas de **trabajo futuro**."

---

### Diapositiva 3 — `> Hidroponía: sin margen de error` *(1:10 – 2:05)* · `[Persona 1]`
**Qué se ve en pantalla:** Subtítulo sobre sistema NFT recirculante, 4 paneles con los rangos críticos (`5,5–6,5`, `< 30 %`, `18–24 °C`, `1,2–2,5`) y el panel inferior ámbar `CONSECUENCIA`.

**Conceptos clave para entender antes de hablar:**
- **Hidroponía NFT (*Nutrient Film Technique* o Técnica de Película Nutritiva):** Es un método de cultivo sin tierra. Las plantas se colocan en caños o canales ligeramente inclinados y por debajo pasa continuamente una película fina (un hilo de agua) con todos los nutrientes disueltos.
- **Solución recirculante:** Significa que el agua no se tira: una bomba la impulsa desde un tanque principal hacia los canales donde están las raíces, el agua recorre las plantas y por gravedad vuelve a caer al mismo tanque para volver a bombearse en circuito cerrado.
- **Cavitación de bombas:** Cuando el tanque se queda con poca agua, la bomba empieza a aspirar aire mezclado con agua; se forman burbujas de vacío que explotan contra las paletas internas, recalientan el motor y queman la bomba.

**Qué decir (`[Persona 1]`):**
> "¿Por qué elegimos la hidroponía como caso de estudio? En la agricultura tradicional, la tierra funciona como un colchón o amortiguador natural: retiene humedad y nutrientes durante días. En cambio, nosotros modelamos un sistema **NFT** (*Nutrient Film Technique* o técnica de película nutritiva). En este sistema **no hay suelo**: las raíces de las plantas están suspendidas dentro de canales por donde corre una lámina fina de agua con sales minerales disueltas. Y se llama **solución recirculante** porque una bomba impulsa esa agua desde un tanque hacia los canales, baña las raíces y vuelve al mismo tanque en un circuito continuo.
>
> Al no haber tierra que amortigüe los cambios, cualquier desvío afecta a la planta de inmediato. Fíjense en los cuatro paneles de la diapositiva:
> - **Primero (`5,5–6,5`):** es el rango seguro de **pH** (la acidez del agua). Si el pH se sale de ese rango —por ejemplo si sube de 6,5—, minerales esenciales como el hierro, el calcio y el fósforo dejan de estar disueltos, **precipitan** (se vuelven sólidos que caen al fondo del tanque como sarro) y la planta no puede absorberlos.
> - **Segundo (`< 30 %`, en ámbar):** es el nivel crítico del tanque de agua. Si por evaporación o consumo el tanque baja del 30 %, la bomba empieza a chupar aire; ese fenómeno se llama **cavitación**, recalienta y quema la bomba, y las raíces se secan rápidamente.
> - **Tercero (`18–24 °C`):** es la temperatura ideal de la solución. Si el agua se calienta de más, pierde el oxígeno disuelto que respiran las raíces.
> - **Cuarto (`1,2–2,5 mS/cm`):** es la **conductividad eléctrica**. Como las sales nutritivas conducen la electricidad, medir la conductividad nos dice qué tan concentrado está el fertilizante en el agua.
>
> Como resume el cuadro inferior **CONSECUENCIA**, una falla no corregida destruye el cultivo en cuestión de **horas**. Por eso necesitamos monitoreo continuo y reacción automática sin depender de una persona."

---

### Diapositiva 4 — `> Del cultivo a los Sistemas Distribuidos` *(2:05 – 2:45)* · `[Persona 1]`
**Qué se ve en pantalla:** Grilla 2×2 de paneles (`DESACOPLAMIENTO → MQTT Pub/Sub`, `TIEMPO REAL → Lazo cerrado`, `TOLERANCIA A FALLOS → k3s self-healing`, `ESCALABILIDAD → Spark vs. Hadoop`).

**Qué decir (`[Persona 1]`):**
> "Si traducimos ese problema agronómico a la informática, cada necesidad del cultivo equivale exactamente a un pilar de **Sistemas Operativos Distribuidos**, como muestran los cuatro paneles:
> 1. Arriba a la izquierda, **Desacoplamiento**: en un invernadero con decenas de sensores y actuadores en distintas zonas, no podemos cablear direcciones IP fijas punto a punto; si cambia un nodo se rompería todo. Lo resolvemos con mensajería **MQTT Publicación/Suscripción**.
> 2. Arriba a la derecha, **Tiempo Real**: cuando el pH se dispara, no podemos esperar a un proceso nocturno; necesitamos un **controlador en lazo cerrado** que detecte el desvío y active el dosificador en milisegundos.
> 3. Abajo a la izquierda, **Tolerancia a Fallos**: si un contenedor o nodo sensor se cae, el sistema no puede quedar ciego en esa zona; necesitamos que un orquestador como **k3s** lo detecte y lo levante solo (*self-healing*).
> 4. Y abajo a la derecha, **Escalabilidad**: un sensor enviando datos cada segundo en múltiples zonas genera millones de registros históricos; para analizarlos comparamos procesamiento paralelo en **Apache Spark frente a Hadoop MapReduce**."

---

### Diapositiva 5 — `> Objetivos del trabajo` *(2:45 – 3:30)* · `[Persona 1]`
**Qué se ve en pantalla:** Lista numerada `[1]` a `[5]` con verbos en verde (`Comparar`, `Desplegar`, `Simular`, `Orquestar`, `Medir`).

**Qué decir (`[Persona 1]`):**
> "A partir de esto definimos los cinco objetivos del trabajo:
> - **Primero, comparar** a nivel teórico y práctico la virtualización completa con hipervisores (como Proxmox con KVM) frente a los contenedores ligeros (Docker), y el modelo MapReduce frente a Spark en memoria.
> - **Segundo, desplegar** un laboratorio distribuido 100 % reproducible usando Docker Compose y automatizar su verificación de forma idempotente con **Ansible**.
> - **Tercero, simular** nodos sensores multizona con comportamiento físico realista y un controlador automático en lazo cerrado comunicado por **MQTT**.
> - **Cuarto, orquestar** los sensores en un clúster **k3s multinodo** para probar escalado horizontal de réplicas y autorrecuperación ante caídas.
> - **Y quinto, medir** de manera rigurosa cinco experimentos (**E1 a E5**), repitiendo cada prueba tres veces para reportar tiempos, aceleración (*speedup*), eficiencia y latencia."

---

### Diapositiva 6 — Separador `02 // MARCO TEÓRICO` *(3:30 – 3:40)* · `[Persona 1]`
**Qué se ve en pantalla:** Número `02`, barra de progreso al `20%` y comando `$ cat teoria/*.md | less`.

**Qué decir (`[Persona 1]`):**
> "Pasamos entonces al segundo bloque para repasar el marco teórico que sustenta nuestras decisiones de diseño."

---

### Diapositiva 7 — `> KVM (Proxmox) vs. Docker` *(3:40 – 4:40)* · `[Persona 1]`
**Qué se ve en pantalla:** Tabla comparativa de 5 filas (`Abstracción`, `Aislamiento`, `Overhead`, `Arranque`, `Densidad 16 GB`) entre `Proxmox VE / KVM` y `Docker / LXC`, y panel inferior `DECISIÓN DE DISEÑO`.

**Conceptos clave para entender:**
- **Hipervisor Tipo 1 (KVM en Proxmox):** Software que corre sobre el hardware físico y crea máquinas virtuales completas; cada VM cree que tiene su propia placa madre, disco y CPU, y carga un sistema operativo entero (con su propio kernel).
- **Namespaces (espacios de nombres del kernel Linux):** Mecanismo que aísla qué puede *ver* un contenedor (sus propios procesos `PID`, su propia interfaz de red `NET`, sus puntos de montaje `MNT`), de modo que un contenedor no ve a los demás.
- **cgroups (grupos de control):** Mecanismo del kernel que limita cuánto hardware puede *usar* un contenedor (tope de CPU y memoria RAM).
- **OverlayFS:** Sistema de archivos en capas; si levantamos 10 contenedores con Python, no se copia Python 10 veces en disco, sino que comparten la misma capa base de solo lectura.

**Qué decir (`[Persona 1]`):**
> "La primera gran decisión arquitectónica fue cómo virtualizar los nodos del laboratorio. En la tabla comparamos la **virtualización completa con Proxmox VE y KVM** frente a la **virtualización a nivel de sistema operativo con Docker**:
> - Fíjense en las primeras dos filas (*Abstracción* y *Aislamiento*): en **KVM**, un hipervisor de Tipo 1 emula hardware completo y cada máquina virtual levanta su propio sistema operativo huésped con un kernel independiente. Eso da un aislamiento muy fuerte, pero —como vemos en las filas de *Overhead* y *Arranque*— obliga a reservar gigabytes de RAM fija para cada sistema operativo duplicado y tarda entre **30 y 90 segundos** en arrancar. En una computadora de 16 GB de RAM apenas podríamos correr entre **4 y 8 máquinas virtuales**.
> - En cambio, en la columna derecha vemos cómo trabaja **Docker**: todos los contenedores comparten el único kernel Linux de la máquina anfitriona. El aislamiento se logra con dos funciones nativas del kernel: los **namespaces** —que aíslan la vista de procesos, red y archivos de cada contenedor— y los **cgroups** —que limitan cuánta CPU y RAM puede consumir cada uno—, sumado a **OverlayFS** para reutilizar capas de disco sin duplicar archivos. Gracias a eso un contenedor arranca en **medio segundo a 2 segundos** y consume solo la memoria de su proceso.
>
> Como sintetiza el cuadro inferior **DECISIÓN DE DISEÑO**, estudiamos Proxmox teóricamente, pero en el laboratorio elegimos Docker porque nos permite simular decenas de contenedores, redes aisladas y un clúster Kubernetes de 3 nodos en una sola máquina sin saturar el hardware.
>
> Ahora le cedo la palabra a **[Nombre Persona 2]** para explicar la orquestación con k3s, el protocolo MQTT y los motores de Big Data."
>
> `[Handoff → Toma la palabra Persona 2 en Diapositiva 8]`

---

### Diapositiva 8 — `> Orquestación con k3s sobre k3d` *(4:40 – 5:35)* · `[Persona 2]`
**Qué se ve en pantalla:** Izquierda: panel `CONCEPTOS` (modelo declarativo, bucle de reconciliación, k3s `< 512 MB`, k3d en Docker). Derecha: panel `TOPOLOGÍA DEL LAB` con el árbol `server-0 (control plane)` → `agent-0` y `agent-1` (`pods ▪ ▪ ▪`) y nota `sensor-simulator → MQTT vía host.k3d.internal:1883`.

**Conceptos clave para entender antes de hablar:**
- **Orquestación declarativa:** En vez de correr comandos manuales como `docker run` uno por uno, escribimos un archivo YAML donde declaramos *"quiero 5 réplicas de este sensor siempre activas"*.
- **Pod, Deployment y ReplicaSet:** En Kubernetes, un **Pod** es la cajita mínima que envuelve a nuestro contenedor; el **ReplicaSet** es el vigilante que cuenta cuántos pods hay vivos en todo momento; y el **Deployment** gestiona las versiones y actualizaciones de esos pods.
- **Bucle de reconciliación:** Es un ciclo infinito del plano de control que compara el *estado real* (ej. "hay 4 pods vivos porque uno falló") contra el *estado deseado* ("el YAML dice 5") y crea el pod faltante automáticamente.
- **k3s y k3d:** Kubernetes común (k8s) es muy pesado porque usa una base de datos distribuida llamada `etcd` que consume gigabytes de RAM. **k3s** es una versión oficial liviana que reemplaza `etcd` por `SQLite` y gasta menos de 512 MB. Y **k3d** es la herramienta que nos permite simular varios servidores de un clúster k3s metiendo cada nodo dentro de un contenedor Docker.

**Qué decir (`[Persona 2]`):**
> "Muchas gracias. Una vez que tenemos contenedores en Docker, aparece el siguiente problema: en un sistema distribuido con decenas de sensores no podemos levantar o reiniciar contenedores a mano cada vez que uno falla. Necesitamos un **orquestador**, y el estándar en la industria es **Kubernetes**.
>
> Como vemos en el panel izquierdo **CONCEPTOS**:
> - Kubernetes trabaja con un **modelo declarativo**: nosotros no le damos órdenes paso a paso, sino que le entregamos un manifiesto diciendo cuál es el *estado deseado* —por ejemplo, *'quiero 5 pods del sensor corriendo'*— a través de objetos como **Deployments**, **ReplicaSets**, **Pods** y **Services**.
> - El corazón de Kubernetes es su **bucle de reconciliación**: el plano de control compara todo el tiempo el estado real contra el deseado; si un pod cae, crea otro automáticamente para volver a coincidir.
> - Como un clúster Kubernetes tradicional consume más de 2 GB de RAM solo para administrarse, elegimos **k3s**, una distribución liviana certificada que reemplaza la base de datos `etcd` por **SQLite**, reduciendo el consumo a **menos de 512 MB de RAM**. Y para no necesitar tres computadoras físicas, usamos **k3d**, que ejecuta cada nodo del clúster k3s dentro de contenedores Docker.
>
> En el diagrama de la derecha (**TOPOLOGÍA DEL LAB**) se ve exactamente cómo armamos nuestro clúster de **3 nodos**: arriba tenemos a **`server-0`**, que actúa como plano de control (*control plane* con el API Server y el planificador), y abajo cuelgan dos nodos trabajadores, **`agent-0`** y **`agent-1`**, donde se reparten los pods simuladores. Además, configuramos el puente DNS **`host.k3d.internal:1883`** para que los pods que viven dentro de la red de Kubernetes puedan publicar sus lecturas hacia el broker Mosquitto que corre en el host."

---

### Diapositiva 9 — `> Mensajería MQTT (Mosquitto)` *(5:35 – 6:20)* · `[Persona 2]`
**Qué se ve en pantalla:** Diagrama superior `SENSORES (publish) ──► MOSQUITTO (:1883) ──► SUSCRIPTORES (subscribe)` con el tópico `hidroponia/+/telemetria → controlador · recolector`. Abajo: 4 paneles (`ESPACIO`, `TIEMPO`, `LIVIANO`, `QoS 1`).

**Conceptos clave para entender:**
- **Tópico con comodín (`hidroponia/+/telemetria`):** En MQTT los mensajes se envían a "canales" llamados tópicos, como carpetas (`hidroponia/zona_1/telemetria`, `hidroponia/zona_2/telemetria`). El signo **`+`** es un comodín de un nivel: al suscribirse a `hidroponia/+/telemetria`, el controlador escucha todas las zonas a la vez sin importar cuántas agreguemos.
- **QoS 1 (Calidad de Servicio 1) y PUBACK:** MQTT tiene 3 niveles: QoS 0 ("disparar y olvidar", se puede perder), **QoS 1 ("al menos una vez")**, donde quien recibe devuelve un paquete de confirmación llamado **`PUBACK`** (si no llega el `PUBACK`, se reenvía), y QoS 2 ("exactamente una vez", más lento).

**Qué decir (`[Persona 2]`):**
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

### Diapositiva 10 — `> Hadoop MapReduce vs. Apache Spark` *(6:20 – 7:20)* · `[Persona 2]`
**Qué se ve en pantalla:** Izquierda: panel `HADOOP STREAMING` (`Map ─► [disco] ─► Shuffle ─► Reduce`). Derecha: panel `APACHE SPARK` (`DAG ─► [RAM] ─► Catalyst ─► Acción`). Abajo: panel ámbar `COMPARACIÓN JUSTA`.

**Conceptos clave para entender:**
- **Map, Shuffle y Reduce (Hadoop):** *Map* lee cada fila del archivo y extrae pares clave-valor (ej. `zona_1 → pH 6,2`); *Shuffle* agrupa y ordena en disco todos los datos de la misma zona; *Reduce* calcula el promedio final por zona. El problema es que entre cada paso escribe y lee del disco duro (**I/O bound**).
- **DAG y Catalyst (Spark):** En lugar de ejecutar paso a paso escribiendo en disco, Spark arma un **DAG** (*Grafo Acíclico Dirigido*, una receta completa de todas las operaciones) en **memoria RAM** y su optimizador **Catalyst** reordena y simplifica las cuentas antes de tocar los datos.

**Qué decir (`[Persona 2]`):**
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

## Bloque B — Arquitectura, Simulación y Demo 1 (7:20 – 11:00)

### Diapositiva 11 — Separador `03 // ARQUITECTURA` *(7:20 – 7:30)* · `[Persona 1]`
**Qué se ve en pantalla:** Número `03`, barra de progreso al `40%` y comando `$ docker compose up -d && make k3s-deploy`.

**Qué decir (`[Persona 1]`):**
> "Muchas gracias. Con las herramientas teóricas claras, veamos ahora cómo las integramos en la arquitectura de nuestro laboratorio."

---

### Diapositiva 12 — `> Arquitectura del laboratorio` *(7:30 – 8:40)* · `[Persona 1]`
**Qué se ve en pantalla:** Diagrama de bloques numerados del `1` al `5` conectados por flechas: `1 · SENSORES` → `2 · BROKER (Mosquitto)` → bifurcación hacia `3A · CONTROLADOR` y `3B · RECOLECTOR` → `4 · PROCESAMIENTO DISTRIBUIDO` y `5 · IaC ANSIBLE`.

**Qué decir (`[Persona 1]`):**
> "En esta diapositiva vemos el diagrama completo del sistema, que se lee siguiendo las flechas de izquierda a derecha:
> - En el bloque **`1 · SENSORES`** tenemos los nodos simuladores, que pueden correr como contenedores en Docker Compose o escalarse de **1 a 20 pods dentro del clúster k3s**. Cada sensor genera lecturas de pH, conductividad, temperatura, humedad y nivel de agua.
> - Esas lecturas se publican por red hacia el bloque **`2 · BROKER`**, que es nuestro servidor **Eclipse Mosquitto 2.0** escuchando en el puerto TCP `1883` con calidad de servicio `QoS 1`.
> - A la salida del broker ocurre algo clave en el diseño: el flujo **se bifurca en dos caminos independientes**:
>   - Arriba, el bloque **`3A · CONTROLADOR`** recibe cada lectura al instante, evalúa en memoria si algún valor violó los umbrales agronómicos y, si hay una anomalía, publica inmediatamente la orden hacia los actuadores y registra la latencia en un archivo CSV.
>   - Abajo, el bloque **`3B · RECOLECTOR`** también escucha las lecturas pero sin bloquear al controlador: las junta en un *buffer* en memoria RAM y cada cierto número de eventos las vuelca de forma atómica como archivos JSON en la carpeta compartida `data/raw/`.
> - Esos archivos alimentan abajo a la izquierda al bloque **`4 · PROCESAMIENTO DISTRIBUIDO`**, donde corren **Apache Spark** (tanto en modo Batch como en Structured Streaming), **Hadoop Streaming** y nuestra línea base en Python sobre datasets de 1 y 10 millones de filas.
> - Y abajo a la derecha, el bloque **`5 · IaC ANSIBLE`** transversalmente verifica que Docker, k3d, kubectl, las carpetas y las configuraciones estén listas de manera idempotente."

---

### Diapositiva 13 — `> Simulación y control reactivo` *(8:40 – 9:40)* · `[Persona 1]`
**Qué se ve en pantalla:** Izquierda: panel `SENSOR SIMULADO`. Derecha arriba: tabla de 5 reglas (`Condición | Actuador | Orden`). Derecha abajo: panel `LATENCIA FIN A FIN` (`Δt = t_comando − t_emisión_sensor`).

**Conceptos clave para entender:**
- **Ruido gaussiano (`σ = 0,03`):** En la vida real ningún sensor electrónico mide siempre `6,000` clavado; siempre hay pequeñas fluctuaciones térmicas y eléctricas que siguen una campana de Gauss (distribución normal con desvío estándar `σ`).
- **Deriva sinusoidal:** Variación lenta y suave a lo largo del tiempo (como una onda seno) para simular cómo sube y baja la temperatura a lo largo del día o cómo se evapora el agua.
- **Semilla fija (`seed=42`):** En computación, si inicializamos el generador aleatorio con el mismo número (`42`), genera exactamente la misma secuencia de datos en cada corrida. Eso permite comparar Python, Hadoop y Spark sobre exactamente los mismos datos.

**Qué decir (`[Persona 1]`):**
> "Veamos en detalle cómo funcionan el sensor y el controlador. En el panel izquierdo **SENSOR SIMULADO** listamos las características de nuestro generador en Python:
> - Simula las **5 variables físicas** del cultivo (pH, conductividad, temperatura, humedad y nivel de agua).
> - Para que no sean números estáticos irreales, le sumamos **ruido gaussiano** —pequeñas fluctuaciones aleatorias propias de cualquier electrodo real, con desvío estándar de `0,03` en pH—, además de una **deriva sinusoidal** que imita los ciclos suaves de temperatura y la caída gradual de agua por evaporación.
> - También inyectamos de forma controlada alrededor de un **8 % de anomalías** (picos fuera de rango) para poner a prueba al controlador, todo bajo una **semilla aleatoria fija** que garantiza que los experimentos sean 100 % reproducibles.
>
> En la **tabla de la derecha** vemos las cinco reglas del controlador en lazo cerrado:
> - Si el **pH supera `6,5`** (agua muy alcalina), le envía al `dosificador_acido` la orden `DOSIFICAR_ACIDO`.
> - Si el **pH baja de `5,5`** (agua muy ácida), le ordena al `dosificador_base` `DOSIFICAR_BASE`.
> - Si el **nivel de agua cae del `30 %`**, activa la `bomba_agua` con `REPONER_AGUA`.
> - Y si la **temperatura** supera los `24 °C` o baja de `18 °C`, activa el `enfriador` o el `calefactor`.
>
> Finalmente, en el recuadro inferior **LATENCIA FIN A FIN**, mostramos la fórmula exacta que medimos en el Experimento E5: cada mensaje del sensor lleva estampada la hora exacta en que salió (`t_emisión_sensor`); cuando el controlador dispara la orden al actuador (`t_comando`), calcula la diferencia `Δt` en milisegundos y la guarda en `controller_latencies.csv`."

---

### Diapositiva 14 — `> Demo 1 · Lazo cerrado IoT` *(9:40 – 11:00)* · `[Persona 1]`
**Qué se ve en pantalla:** Izquierda: panel `PASOS` con los 4 comandos. Derecha: video MP4 embebido `01_demo_iot_lazo_cerrado.mp4` mostrando la terminal en vivo.

**Qué hacer:** Hacer **clic sobre el video** en la diapositiva para reproducirlo (dura 16 segundos) o ejecutar el Bloque 1 de `./scripts/demo_en_vivo.sh`.

**Qué decir mientras corre el video (`[Persona 1]`):**
> "Vamos a verlo funcionando en nuestra primera demostración. En el panel izquierdo tienen los cuatro pasos que se ejecutan en el video de la derecha:
> 1. Primero ejecutamos `docker compose up -d` para levantar los cuatro contenedores del circuito IoT: el broker Mosquitto, el simulador zonal, el controlador y el recolector.
> 2. En el segundo paso, con `docker compose ps`, observamos en la tabla de la terminal que los cuatro servicios pasan inmediatamente al estado `Up`.
> 3. Luego inspeccionamos los logs del simulador y del controlador: ahí se ve cómo ambos se conectan al broker en `mosquitto:1883` y el controlador queda suscripto al tópico `hidroponia/+/telemetria` vigilando cada lectura en tiempo real.
> 4. Y en el cuarto paso ejecutamos `ls -lh data/raw/`, donde se ven los archivos `batch_*.json` que el recolector va escribiendo en disco de manera atómica —primero los escribe en un archivo temporal y luego los renombra a `.json` para que ningún proceso lector lea un archivo incompleto—.
>
> *(Si además lo corrés en vivo en la terminal y aparece una alerta amarilla:)* Fíjense cómo ante un pH mayor a 6,5 el controlador emite instantáneamente `DOSIFICAR_ACIDO` en menos de un milisegundo.
>
> Comprobado el funcionamiento de la capa IoT, le paso la palabra a **[Nombre Persona 2]** para ver los resultados de la campaña experimental y las demos de Kubernetes, Spark y Ansible."
>
> `[Handoff → Toma la palabra Persona 2 en Diapositiva 15]`

---

## Bloque C — Campaña Experimental (E1–E5) y Demos 2 y 3 (11:00 – 16:50)

### Diapositiva 15 — Separador `04 // RESULTADOS` *(11:00 – 11:10)* · `[Persona 2]`
**Qué se ve en pantalla:** Número `04`, barra de progreso al `60%` y comando `$ make benchmark && make analyze`.

**Qué decir (`[Persona 2]`):**
> "Pasamos ahora al cuarto bloque: los resultados de nuestra campaña experimental. Todas las pruebas que van a ver se ejecutaron **tres veces cada una** en subprocesos aislados, reportando la media y el desvío estándar."

---

### Diapositiva 16 — `> E1 · Rendimiento según volumen` *(11:10 – 12:20)* · `[Persona 2]`
**Qué se ve en pantalla:** Izquierda: gráfico de barras agrupadas `TIEMPO (s)` comparando `Python`, `Hadoop` y `Spark` con barras **verde oscuro (`1M filas`)** y **verde claro (`10M filas`)**. Derecha: cifras gigantes **`3,86×`** y **`4,30×`** + recuadro ámbar `PUNTO DE INFLEXIÓN`.

**Qué decir señalando el gráfico (`[Persona 2]`):**
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

### Diapositiva 17 — `> E2 · Escalabilidad de Spark` *(12:20 – 13:20)* · `[Persona 2]`
**Qué se ve en pantalla:** Izquierda: gráfico de líneas `SPEEDUP` con curva **verde continua (`Real`: `1,00× → 1,33× → 1,61×`)** y curva **gris punteada (`Ideal`: `1,00× → 2,00× → 3,00×`)**. Derecha arriba: tabla con `Workers | Cómputo (μ ± σ) | Speedup | Efic.`. Derecha abajo: panel `LEY DE AMDAHL` con la ecuación `S(p) = 1 / ((1−f) + f/p)`.

**Conceptos clave para entender:**
- **Speedup (`S(p) = T(1) / T(p)`):** Cuántas veces más rápido termina el trabajo usando `p` workers comparado contra usar 1 solo worker. Si con 1 worker tarda `14,78 s` y con 3 tarda `9,18 s`, entonces `14,78 / 9,18 = 1,61×`.
- **Eficiencia paralela (`E(p) = Speedup / p`):** Qué porcentaje de la capacidad de cada worker se transforma realmente en velocidad (`1,61 / 3 = 53,6 %`).
- **Ley de Amdahl:** En cualquier programa paralelo hay una parte paralelizable (`f`) y una parte secuencial (`1 - f`) que no se puede dividir (abrir el archivo, juntar los promedios en el nodo maestro, enviar datos por red). Esa parte secuencial hace que agregar workers rinda cada vez un poco menos.

**Qué decir señalando gráfico, tabla y fórmula (`[Persona 2]`):**
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

### Diapositiva 18 — `> Demo 2 · k3s: escalado y self-healing` *(13:20 – 14:30)* · `[Persona 2]`
**Qué se ve en pantalla:** Izquierda: panel `PASOS` (`k3d cluster: 1 server + 2 agents`, `kubectl scale --replicas=5 (~3 s)`, `kubectl delete pod → ReplicaSet lo recrea en < 2 s`, `kubectl get pods -o wide`). Derecha: video embebido `02_demo_k3s_escalado_tolerancia.mp4`.

**Qué hacer:** Hacer **clic sobre el video** para reproducirlo (dura 23 segundos) o ejecutar el Bloque 3 de `./scripts/demo_en_vivo.sh`.

**Qué decir mientras corre el video (`[Persona 2]`):**
> "Pasemos a la **Demostración 2**, donde ejecutamos en vivo los **Experimentos E3 (escalado horizontal)** y **E4 (tolerancia a fallos)** sobre nuestro clúster k3s de tres nodos (`server-0`, `agent-0` y `agent-1`).
>
> Siguiendo los pasos de la izquierda en el video:
> 1. Primero verificamos los 3 nodos del clúster con `kubectl get nodes` y vemos que inicialmente hay **1 solo pod** del simulador corriendo.
> 2. Ahí ejecutamos el **Experimento E3**: lanzamos `kubectl scale deployment sensor-simulator --replicas=5`. Observen en la tabla de `kubectl get pods -o wide` cómo en apenas **3 segundos** ya tenemos las **5 réplicas en estado `Running` (`1/1`)**, y si miran la columna `NODE` a la derecha de la tabla, el planificador de Kubernetes las repartió automáticamente entre `agent-0`, `agent-1` y `server-0`.
> 3. Inmediatamente después probamos el **Experimento E4 (tolerancia a fallos)**: simulamos la caída abrupta de un nodo eliminando un pod con `kubectl delete pod --now`.
> 4. Y cuando listamos los pods un instante después, vemos que siguen habiendo **5 pods activos**: el `ReplicaSet` detectó al instante que había 4 en lugar de 5 y creó un pod sustituto nuevo en **menos de 2 segundos**. Esto es *self-healing* real: el sistema se curó solo sin que ningún operador humano interviniera."

---

### Diapositiva 19 — `> Demo 3 · Spark e idempotencia` *(14:30 – 15:30)* · `[Persona 2]`
**Qué se ve en pantalla:** Izquierda: panel `PASOS` (`spark batch_analysis.py (1M) → 5,39 s`, `run_hadoop_job.py (1M) → 4,09 s`, `ansible-playbook playbook.yml`, `PLAY RECAP → changed=0`). Derecha: video embebido `03_demo_spark_hadoop_ansible.mp4`.

**Concepto clave para entender:**
- **Idempotencia (en Ansible):** Propiedad matemática y de ingeniería según la cual aplicar una operación una vez o diez veces seguidas produce exactamente el mismo estado final, sin duplicar configuraciones ni romper lo que ya estaba bien. En Ansible se comprueba viendo **`changed=0`** en el resumen final (`PLAY RECAP`).

**Qué hacer:** Hacer **clic sobre el video** para reproducirlo (dura 20 segundos) o ejecutar los Bloques 2 y 4 de `./scripts/demo_en_vivo.sh`.

**Qué decir mientras corre el video (`[Persona 2]`):**
> "En la **Demostración 3** mostramos dos cosas: la equivalencia analítica entre Spark y Hadoop, y la automatización con Ansible:
> 1. En la primera mitad del video lanzamos el trabajo de **Apache Spark (`batch_analysis.py`)** sobre el dataset de **1 millón de lecturas**. Ahí aparece la tabla de resultados con las 5 zonas del cultivo (`zona_1` a `zona_5`), mostrando alrededor de 200.000 lecturas por zona, los promedios exactos de pH (`~6,06`), conductividad (`~1,80`), temperatura (`~21 °C`) y unas 60.000 alertas por zona, completando el cómputo en **`5,39 segundos`**.
> 2. Justo debajo ejecutamos el mismo cálculo con **Hadoop Streaming (`run_hadoop_job.py`)**, que arroja **exactamente los mismos números** en **`4,09 segundos`** —confirmando en vivo lo que vimos en el gráfico E1 para volúmenes de 1 millón—.
> 3. Y en la segunda mitad del video ejecutamos nuestro playbook de **Ansible (`ansible-playbook playbook.yml`)**. Ansible revisa paquetes, el demonio de Docker, los directorios de datos y el archivo `mosquitto.conf`. Como el entorno ya estaba configurado, miren la última línea del **`PLAY RECAP`**: dice **`ok=8, changed=0, failed=0`**. Ese **`changed=0`** demuestra **idempotencia estricta**: podemos correr el aprovisionamiento todas las veces que queramos con la certeza de que no altera nada que ya esté en el estado correcto."

---

### Diapositiva 20 — `> E5 · Latencia del lazo cerrado` *(15:30 – 16:20)* · `[Persona 2]`
**Qué se ve en pantalla:** Izquierda: gráfico de barras agrupadas `LATENCIA (ms)` para `1 sensor`, `10 sensores` y `50 sensores` con **barras verdes (`Media`)** y **barras ámbar (`P95`)**. Derecha arriba: cifra destacada **`19,56 ms`** (`P95 con 50 sensores concurrentes`). Derecha medio: tabla con `Sensores | μ ± σ (ms) | P95`. Derecha abajo: panel `VEREDICTO`.

**Conceptos clave para entender:**
- **Percentil 95 (P95):** Si ordenamos 100 mediciones de menor a mayor, el P95 es el valor número 95. Significa que **el 95 % de las veces el sistema responde en ese tiempo o menos**. En sistemas de tiempo real es mucho más importante que el promedio, porque el promedio puede esconder demoras.
- **Tiempo real blando (*soft real-time*):** Un sistema donde responder en milisegundos es deseable y necesario para la calidad del control, pero donde una variación de 5 o 15 ms no produce una catástrofe física instantánea (porque la química del agua en un tanque cambia a lo largo de minutos).

**Qué decir señalando el gráfico y la tabla (`[Persona 2]`):**
> "El último experimento cuantitativo es el **E5**, donde medimos la **latencia real extremo a extremo del lazo cerrado**: cuánto tarda en viajar una anomalía desde el sensor, pasar por el broker Mosquitto, ser evaluada por el contenedor controlador y salir como orden hacia el actuador.
>
> En el gráfico de la izquierda, las **barras verdes** muestran la **latencia media** y las **barras ámbar** muestran el **Percentil 95 (P95)** —es decir, el tiempo máximo dentro del cual se resuelve el 95 % de las alertas— al estresar el broker con **1, 10 y 50 sensores disparando ráfagas al mismo tiempo**:
> - Como detalla la tabla de la derecha, con **1 sensor** la reacción es casi instantánea: media de **`0,11 ± 0,22 ms`** y P95 de **`0,49 ms`** (menos de medio milisegundo).
> - Con **10 sensores concurrentes** (150 anomalías), la media es de **`2,22 ± 1,46 ms`** y el P95 de **`4,56 ms`**.
> - Y en el escenario de estrés con **50 sensores disparando en simultáneo** (750 anomalías en ráfaga), la media es de **`7,56 ± 7,03 ms`** y el P95 llega a **`19,56 ms`**, el valor destacado arriba a la derecha.
>
> Como concluye el recuadro **VEREDICTO**, incluso bajo una tormenta de 50 sensores concurrentes, **el 95 % de las órdenes correctivas se emite en menos de 20 milisegundos**. Tratándose de un cultivo hidropónico donde el pH y el nivel de agua evolucionan en escalas de minutos, esta arquitectura cumple de sobra con los requisitos de **tiempo real blando**."

---

### Diapositiva 21 — `> tail -f resultados.log` (Resumen de Experimentos) *(16:20 – 16:50)* · `[Persona 2]`
**Qué se ve en pantalla:** Grilla de 6 tarjetas KPI (`E1: 3,86×`, `E2: 1,61×`, `E3: ~3 s`, `E4: < 2 s`, `E5: 19,56 ms`, `IaC: changed=0`).

**Qué decir (`[Persona 2]`):**
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
> `[Handoff → Persona 1 toma la palabra en Diapositiva 22]`

---

## Bloque D — Cierre, Conclusiones y Trabajo Futuro (16:50 – 18:30)

### Diapositiva 22 — Separador `05 // CIERRE` *(16:50 – 16:55)* · `[Persona 1]`
**Qué se ve en pantalla:** Número `05`, barra de progreso al `90%` y comando `$ git log --oneline | head -1`.

**Qué decir (`[Persona 1]`):**
> "Entramos ahora al último bloque de la exposición para sintetizar nuestras conclusiones y el trabajo futuro."

---

### Diapositiva 23 — `> Conclusiones` *(16:55 – 17:50)* · `[Persona 1 + Persona 2]`
**Qué se ve en pantalla:** Izquierda: panel verde `INFRA + IoT · P1`. Derecha: panel ámbar `DATOS + RESILIENCIA · P2`. Abajo: frase resumen `$ echo $TESIS`.

**Qué decir (`[Persona 1]` — columna izquierda verde, 16:55 – 17:20):**
> "En el panel izquierdo, desde el punto de vista de la **infraestructura y la capa IoT**, nos llevamos tres conclusiones principales:
> - **Primero:** combinar contenedores **Docker con k3d** nos permitió modelar un clúster distribuido multinodo completo en una sola computadora consumiendo menos de 1,5 GB de RAM basal, algo que con máquinas virtuales tradicionales en KVM habría demandado más de 12 GB de RAM fija.
> - **Segundo:** el protocolo **MQTT sobre Mosquitto** probó ser ideal para sistemas ciberfísicos: desacopló por completo a los sensores de los consumidores manteniendo latencias de pocos milisegundos.
> - **Y tercero:** haber separado arquitectónicamente el **control reactivo en memoria** (camino rápido) de la **ingesta por lotes en disco** (camino analítico) evitó cuellos de botella y dio estabilidad ante ráfagas de datos."

**Qué decir (`[Persona 2]` — columna derecha ámbar + tesis, 17:20 – 17:50):**
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

---

### Diapositiva 24 — `> Trabajo futuro` y Preguntas *(17:50 – 18:30)* · `[Persona 1]`
**Qué se ve en pantalla:** 3 paneles (`KAFKA`, `PROMETHEUS + GRAFANA`, `CEPH / PROXMOX`), mensaje central `¡Gracias! ¿Preguntas?` y enlace `$ git clone https://github.com/MatiasCarlsson/SOD.git`.

**Qué decir (`[Persona 1]`):**
> "Para cerrar, proyectamos tres evoluciones naturales para escalar este laboratorio a un entorno industrial:
> 1. En el primer panel, incorporar **Apache Kafka** detrás o en lugar de Mosquitto para tener *event sourcing*: es decir, guardar el flujo de eventos en un registro particionado y replicado en disco que permita reprocesar semanas enteras de telemetría si sumamos nuevos modelos analíticos.
> 2. En el segundo panel, sumar **Prometheus y Grafana** para observabilidad en vivo: recolectar métricas de uso de CPU y RAM de cada pod de k3s y de los workers de Spark junto con tableros visuales de pH y nivel de agua.
> 3. Y en el tercer panel, llevar este esquema a un clúster físico con **Proxmox VE y almacenamiento distribuido Ceph**, de modo que los lotes crudos y checkpoints de Spark se guarden en bloques replicados entre varios servidores físicos sin punto único de falla.
>
> Abajo tienen el enlace a nuestro repositorio público de GitHub con el informe completo en formato APA 7, el código fuente, los scripts automatizados y los videos de respaldo. Muchísimas gracias por su tiempo y quedamos a total disposición para las preguntas del tribunal."
