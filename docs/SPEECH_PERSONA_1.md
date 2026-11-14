# Guion de Exposición Oral — PERSONA 1 (Versión Explicada y Detallada)

> **Rol en la defensa:** Apertura, contexto agronómico (sistema hidropónico NFT), desafíos de Sistemas Operativos Distribuidos, objetivos, virtualización (Proxmox/KVM vs. Docker), arquitectura general, simulación de sensores y lazo cerrado, **Demo 1** y cierre (conclusiones de infraestructura + trabajo futuro).  
> **Presentación:** `docs/Presentacion_TIF_SOD_2026.pptx` (24 diapositivas, estilo *Textmode Overlay*, transición *fade* y videos MP4 embebidos).  
> **Duración estimada de tu parte:** ~9 minutos (alternando con Persona 2 para un total de 17–18 minutos).  
> **Pista visual en pantalla:** arriba a la derecha, **`[ Persona 1 ]` en verde** indica tus diapositivas; **`[ Persona 2 ]` en ámbar** las de tu compañero; **blanco** cuando participan ambos.

---

## Bloque A — Apertura, Contexto Agronómico y Virtualización (0:00 – 4:40)

### Diapositiva 1 — Portada *(0:00 – 0:40)*
**Qué se ve en pantalla:** Líneas de arranque `[ OK ]` de los 4 subsistemas (`mosquitto`, `k3d`, `spark`, `ansible`), título principal y recuadro `TIF · AE 4`.

**Qué decir:**
> "Buenas tardes a los integrantes del tribunal y compañeros. Hoy vamos a presentar nuestro Trabajo Integrador Final de la cátedra de **Sistemas Operativos Distribuidos**, titulado *'Sistema automatizado de cultivo hidropónico distribuido'*.
>
> El equipo está integrado por **[Nombre Persona 2]** y quien les habla, **[Nombre Persona 1]**. En este proyecto integramos Internet de las Cosas con MQTT, contenedores Docker, orquestación con Kubernetes ligero (k3s), procesamiento paralelo con Hadoop y Apache Spark, y automatización con Ansible. Todo lo que van a ver a lo largo de la presentación —tanto las métricas como los gráficos y las demostraciones en video— proviene de ejecuciones y mediciones reales de nuestro laboratorio."

---

### Diapositiva 2 — Agenda `> ls -la ./defensa` *(0:40 – 1:10)*
**Qué se ve en pantalla:** Los 5 bloques de la defensa (`01 contexto/`, `02 teoria/`, `03 arquitectura/`, `04 resultados/`, `05 cierre/`) con el responsable (`P1`, `P2`) y el minuto de inicio.

**Qué decir:**
> "Organizamos la exposición en cinco bloques que recorren desde el problema real hasta la validación experimental:
> 1. Primero vamos a ver el **contexto agronómico** y por qué un cultivo hidropónico exige un sistema distribuido.
> 2. En el segundo bloque repasamos el **marco teórico** comparando máquinas virtuales contra contenedores, orquestación en k3s, mensajería MQTT y Hadoop frente a Spark.
> 3. En el tercer bloque mostramos la **arquitectura de nuestro laboratorio** y la **primera demostración** del lazo cerrado IoT.
> 4. En el cuarto bloque analizamos los **cinco experimentos cuantitativos (E1 a E5)** junto con las **demostraciones de k3s, Spark y Ansible**.
> 5. Y cerramos con las **conclusiones** y las líneas de **trabajo futuro**."

---

### Diapositiva 3 — `> Hidroponía: sin margen de error` *(1:10 – 2:05)*
**Qué se ve en pantalla:** Subtítulo sobre sistema NFT recirculante, 4 paneles con los rangos críticos (`5,5–6,5`, `< 30 %`, `18–24 °C`, `1,2–2,5`) y el panel inferior ámbar `CONSECUENCIA`.

**Conceptos clave para entender antes de hablar:**
- **Hidroponía NFT (*Nutrient Film Technique* o Técnica de Película Nutritiva):** Es un método de cultivo sin tierra. Las plantas se colocan en caños o canales ligeramente inclinados y por debajo pasa continuamente una película fina (un hilo de agua) con todos los nutrientes disueltos.
- **Solución recirculante:** Significa que el agua no se tira: una bomba la impulsa desde un tanque principal hacia los canales donde están las raíces, el agua recorre las plantas y por gravedad vuelve a caer al mismo tanque para volver a bombearse en circuito cerrado.
- **Cavitación de bombas:** Cuando el tanque se queda con poca agua, la bomba empieza a aspirar aire mezclado con agua; se forman burbujas de vacío que explotan contra las paletas internas, recalientan el motor y queman la bomba.

**Qué decir:**
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

### Diapositiva 4 — `> Del cultivo a los Sistemas Distribuidos` *(2:05 – 2:45)*
**Qué se ve en pantalla:** Grilla 2×2 de paneles (`DESACOPLAMIENTO → MQTT Pub/Sub`, `TIEMPO REAL → Lazo cerrado`, `TOLERANCIA A FALLOS → k3s self-healing`, `ESCALABILIDAD → Spark vs. Hadoop`).

**Qué decir:**
> "Si traducimos ese problema agronómico a la informática, cada necesidad del cultivo equivale exactamente a un pilar de **Sistemas Operativos Distribuidos**, como muestran los cuatro paneles:
> 1. Arriba a la izquierda, **Desacoplamiento**: en un invernadero con decenas de sensores y actuadores en distintas zonas, no podemos cablear direcciones IP fijas punto a punto; si cambia un nodo se rompería todo. Lo resolvemos con mensajería **MQTT Publicación/Suscripción**.
> 2. Arriba a la derecha, **Tiempo Real**: cuando el pH se dispara, no podemos esperar a un proceso nocturno; necesitamos un **controlador en lazo cerrado** que detecte el desvío y active el dosificador en milisegundos.
> 3. Abajo a la izquierda, **Tolerancia a Fallos**: si un contenedor o nodo sensor se cae, el sistema no puede quedar ciego en esa zona; necesitamos que un orquestador como **k3s** lo detecte y lo levante solo (*self-healing*).
> 4. Y abajo a la derecha, **Escalabilidad**: un sensor enviando datos cada segundo en múltiples zonas genera millones de registros históricos; para analizarlos comparamos procesamiento paralelo en **Apache Spark frente a Hadoop MapReduce**."

---

### Diapositiva 5 — `> Objetivos del trabajo` *(2:45 – 3:30)*
**Qué se ve en pantalla:** Lista numerada `[1]` a `[5]` con verbos en verde (`Comparar`, `Desplegar`, `Simular`, `Orquestar`, `Medir`).

**Qué decir:**
> "A partir de esto definimos los cinco objetivos del trabajo:
> - **Primero, comparar** a nivel teórico y práctico la virtualización completa con hipervisores (como Proxmox con KVM) frente a los contenedores ligeros (Docker), y el modelo MapReduce frente a Spark en memoria.
> - **Segundo, desplegar** un laboratorio distribuido 100 % reproducible usando Docker Compose y automatizar su verificación de forma idempotente con **Ansible**.
> - **Tercero, simular** nodos sensores multizona con comportamiento físico realista y un controlador automático en lazo cerrado comunicado por **MQTT**.
> - **Cuarto, orquestar** los sensores en un clúster **k3s multinodo** para probar escalado horizontal de réplicas y autorrecuperación ante caídas.
> - **Y quinto, medir** de manera rigurosa cinco experimentos (**E1 a E5**), repitiendo cada prueba tres veces para reportar tiempos, aceleración (*speedup*), eficiencia y latencia."

---

### Diapositiva 6 — Separador `02 // MARCO TEÓRICO` *(3:30 – 3:40)*
**Qué se ve en pantalla:** Número `02`, barra de progreso al `20%` y comando `$ cat teoria/*.md | less`.

**Qué decir:**
> "Pasamos entonces al segundo bloque para repasar el marco teórico que sustenta nuestras decisiones de diseño."

---

### Diapositiva 7 — `> KVM (Proxmox) vs. Docker` *(3:40 – 4:40)*
**Qué se ve en pantalla:** Tabla comparativa de 5 filas (`Abstracción`, `Aislamiento`, `Overhead`, `Arranque`, `Densidad 16 GB`) entre `Proxmox VE / KVM` y `Docker / LXC`, y panel inferior `DECISIÓN DE DISEÑO`.

**Conceptos clave para entender:**
- **Hipervisor Tipo 1 (KVM en Proxmox):** Software que corre sobre el hardware físico y crea máquinas virtuales completas; cada VM cree que tiene su propia placa madre, disco y CPU, y carga un sistema operativo entero (con su propio kernel).
- **Namespaces (espacios de nombres del kernel Linux):** Mecanismo que aísla qué puede *ver* un contenedor (sus propios procesos `PID`, su propia interfaz de red `NET`, sus puntos de montaje `MNT`), de modo que un contenedor no ve a los demás.
- **cgroups (grupos de control):** Mecanismo del kernel que limita cuánto hardware puede *usar* un contenedor (tope de CPU y memoria RAM).
- **OverlayFS:** Sistema de archivos en capas; si levantamos 10 contenedores con Python, no se copia Python 10 veces en disco, sino que comparten la misma capa base de solo lectura.

**Qué decir:**
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

## Bloque B — Arquitectura, Simulación y Demo 1 (7:20 – 11:00)

> *(Retomás la palabra después de que Persona 2 termina la Diapositiva 10)*

### Diapositiva 11 — Separador `03 // ARQUITECTURA` *(7:20 – 7:30)*
**Qué se ve en pantalla:** Número `03`, barra de progreso al `40%` y comando `$ docker compose up -d && make k3s-deploy`.

**Qué decir:**
> "Muchas gracias. Con las herramientas teóricas claras, veamos ahora cómo las integramos en la arquitectura de nuestro laboratorio."

---

### Diapositiva 12 — `> Arquitectura del laboratorio` *(7:30 – 8:40)*
**Qué se ve en pantalla:** Diagrama de bloques numerados del `1` al `5` conectados por flechas: `1 · SENSORES` → `2 · BROKER (Mosquitto)` → bifurcación hacia `3A · CONTROLADOR` y `3B · RECOLECTOR` → `4 · PROCESAMIENTO DISTRIBUIDO` y `5 · IaC ANSIBLE`.

**Qué decir:**
> "En esta diapositiva vemos el diagrama completo del sistema, que se lee siguiendo las flechas de izquierda a derecha:
> - En el bloque **`1 · SENSORES`** tenemos los nodos simuladores, que pueden correr como contenedores en Docker Compose o escalarse de **1 a 20 pods dentro del clúster k3s**. Cada sensor genera lecturas de pH, conductividad, temperatura, humedad y nivel de agua.
> - Esas lecturas se publican por red hacia el bloque **`2 · BROKER`**, que es nuestro servidor **Eclipse Mosquitto 2.0** escuchando en el puerto TCP `1883` con calidad de servicio `QoS 1`.
> - A la salida del broker ocurre algo clave en el diseño: el flujo **se bifurca en dos caminos independientes**:
>   - Arriba, el bloque **`3A · CONTROLADOR`** recibe cada lectura al instante, evalúa en memoria si algún valor violó los umbrales agronómicos y, si hay una anomalía, publica inmediatamente la orden hacia los actuadores y registra la latencia en un archivo CSV.
>   - Abajo, el bloque **`3B · RECOLECTOR`** también escucha las lecturas pero sin bloquear al controlador: las junta en un *buffer* en memoria RAM y cada cierto número de eventos las vuelca de forma atómica como archivos JSON en la carpeta compartida `data/raw/`.
> - Esos archivos alimentan abajo a la izquierda al bloque **`4 · PROCESAMIENTO DISTRIBUIDO`**, donde corren **Apache Spark** (tanto en modo Batch como en Structured Streaming), **Hadoop Streaming** y nuestra línea base en Python sobre datasets de 1 y 10 millones de filas.
> - Y abajo a la derecha, el bloque **`5 · IaC ANSIBLE`** transversalmente verifica que Docker, k3d, kubectl, las carpetas y las configuraciones estén listas de manera idempotente."

---

### Diapositiva 13 — `> Simulación y control reactivo` *(8:40 – 9:40)*
**Qué se ve en pantalla:** Izquierda: panel `SENSOR SIMULADO`. Derecha arriba: tabla de 5 reglas (`Condición | Actuador | Orden`). Derecha abajo: panel `LATENCIA FIN A FIN` (`Δt = t_comando − t_emisión_sensor`).

**Conceptos clave para entender:**
- **Ruido gaussiano (`σ = 0,03`):** En la vida real ningún sensor electrónico mide siempre `6,000` clavado; siempre hay pequeñas fluctuaciones térmicas y eléctricas que siguen una campana de Gauss (distribución normal con desvío estándar `σ`).
- **Deriva sinusoidal:** Variación lenta y suave a lo largo del tiempo (como una onda seno) para simular cómo sube y baja la temperatura a lo largo del día o cómo se evapora el agua.
- **Semilla fija (`seed=42`):** En computación, si inicializamos el generador aleatorio con el mismo número (`42`), genera exactamente la misma secuencia de datos en cada corrida. Eso permite comparar Python, Hadoop y Spark sobre exactamente los mismos datos.

**Qué decir:**
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

### Diapositiva 14 — `> Demo 1 · Lazo cerrado IoT` *(9:40 – 11:00)*
**Qué se ve en pantalla:** Izquierda: panel `PASOS` con los 4 comandos. Derecha: video MP4 embebido `01_demo_iot_lazo_cerrado.mp4` mostrando la terminal en vivo.

**Qué hacer:** Hacer **clic sobre el video** en la diapositiva para reproducirlo (dura 16 segundos) o ejecutar el Bloque 1 de `./scripts/demo_en_vivo.sh`.

**Qué decir mientras corre el video:**
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

## Bloque C — Cierre, Conclusiones y Trabajo Futuro (16:50 – 18:30)

> *(Retomás la palabra después de que Persona 2 explica el Resumen en la Diapositiva 21)*

### Diapositiva 22 — Separador `05 // CIERRE` *(16:50 – 16:55)*
**Qué se ve en pantalla:** Número `05`, barra de progreso al `90%` y comando `$ git log --oneline | head -1`.

**Qué decir:**
> "Entramos ahora al último bloque de la exposición para sintetizar nuestras conclusiones y el trabajo futuro."

---

### Diapositiva 23 — `> Conclusiones` *(Parte 1: 16:55 – 17:20)*
**Qué se ve en pantalla:** Izquierda: panel verde `INFRA + IoT · P1`. Derecha: panel ámbar `DATOS + RESILIENCIA · P2`. Abajo: frase resumen `$ echo $TESIS`.

**Qué decir:**
> "En el panel izquierdo, desde el punto de vista de la **infraestructura y la capa IoT**, nos llevamos tres conclusiones principales:
> - **Primero:** combinar contenedores **Docker con k3d** nos permitió modelar un clúster distribuido multinodo completo en una sola computadora consumiendo menos de 1,5 GB de RAM basal, algo que con máquinas virtuales tradicionales en KVM habría demandado más de 12 GB de RAM fija.
> - **Segundo:** el protocolo **MQTT sobre Mosquitto** probó ser ideal para sistemas ciberfísicos: desacopló por completo a los sensores de los consumidores manteniendo latencias de pocos milisegundos.
> - **Y tercero:** haber separado arquitectónicamente el **control reactivo en memoria** (camino rápido) de la **ingesta por lotes en disco** (camino analítico) evitó cuellos de botella y dio estabilidad ante ráfagas de datos."
>
> *(Ahora habla Persona 2 para cubrir el panel derecho ámbar y la tesis inferior, y te devuelve la palabra para la última diapositiva.)*

---

### Diapositiva 24 — `> Trabajo futuro` y Preguntas *(17:50 – 18:30)*
**Qué se ve en pantalla:** 3 paneles (`KAFKA`, `PROMETHEUS + GRAFANA`, `CEPH / PROXMOX`), mensaje central `¡Gracias! ¿Preguntas?` y enlace `$ git clone https://github.com/MatiasCarlsson/SOD.git`.

**Qué decir:**
> "Para cerrar, proyectamos tres evoluciones naturales para escalar este laboratorio a un entorno industrial:
> 1. En el primer panel, incorporar **Apache Kafka** detrás o en lugar de Mosquitto para tener *event sourcing*: es decir, guardar el flujo de eventos en un registro particionado y replicado en disco que permita reprocesar semanas enteras de telemetría si sumamos nuevos modelos analíticos.
> 2. En el segundo panel, sumar **Prometheus y Grafana** para observabilidad en vivo: recolectar métricas de uso de CPU y RAM de cada pod de k3s y de los workers de Spark junto con tableros visuales de pH y nivel de agua.
> 3. Y en el tercer panel, llevar este esquema a un clúster físico con **Proxmox VE y almacenamiento distribuido Ceph**, de modo que los lotes crudos y checkpoints de Spark se guarden en bloques replicados entre varios servidores físicos sin punto único de falla.
>
> Abajo tienen el enlace a nuestro repositorio público de GitHub con el informe completo en formato APA 7, el código fuente, los scripts automatizados y los videos de respaldo. Muchísimas gracias por su tiempo y quedamos a total disposición para las preguntas del tribunal."
