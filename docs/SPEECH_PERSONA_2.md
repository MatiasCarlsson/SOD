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
> "Para el análisis histórico comparamos dos paradigmas. **Hadoop MapReduce** divide el trabajo en Map, Shuffle y Reduce, y escribe los resultados intermedios en disco: eso penaliza cada etapa con entrada/salida. Lo implementamos con Hadoop Streaming en Python.
>
> **Spark** mantiene los datos en memoria, arma un plan DAG y lo optimiza con Catalyst; además soporta batch y streaming.
>
> Para que la comparación sea justa, Python, Hadoop y Spark ejecutan exactamente la misma agregación: promedios por zona y conteo de alertas.
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
> "En el E1 comparamos los tres motores con 1 y 10 millones de filas.
>
> Con **1 millón** gana Python: **3,28 s**, contra 4,21 s de Hadoop y 5,37 s de Spark. Spark pierde porque paga el arranque de la JVM y la planificación, y con poco volumen ese costo no se amortiza.
>
> Con **10 millones** la historia cambia: Python sube a **34,20 s**, Hadoop a **38,09 s** y Spark resuelve en **8,86 s**. Es decir, **3,86 veces más rápido que Python** y **4,30 veces más rápido que Hadoop**."

### Diapositiva 17 — E2 · Escalabilidad de Spark *(12:20 – 13:20)*
> "En el E2 medimos cómo escala Spark sobre 10 millones de filas. Con 1 worker tarda **14,78 s**; con 2, **11,09 s** (speedup **1,33×**); con 3, **9,18 s** (speedup **1,61×**). La eficiencia cae del 100 % al **53,6 %**.
>
> La línea punteada es el ideal. La separación entre ambas curvas es la **Ley de Amdahl**: hay una parte secuencial —leer el CSV, el *collect* en el driver y el *shuffle*— que ningún worker extra puede acelerar."

### Diapositiva 18 — Demo 2 · k3s: escalado y self-healing *(13:20 – 14:30)*
> *(Hacé **clic sobre el video** o ejecutá el Bloque 3 de `./scripts/demo_en_vivo.sh`.)*
>
> "Este es nuestro clúster k3d de tres nodos. Escalamos el simulador a **cinco réplicas** con `kubectl scale`, y en unos **3 segundos** están corriendo, repartidas entre los nodos.
>
> Ahora simulamos una falla: **borramos un pod** con `kubectl delete pod`. El ReplicaSet detecta que hay menos réplicas de las deseadas y levanta un reemplazo en **menos de 2 segundos**. Nadie lo recreó a mano: lo hizo el bucle de reconciliación."

### Diapositiva 19 — Demo 3 · Spark e idempotencia *(14:30 – 15:30)*
> *(Hacé **clic sobre el video** o ejecutá los Bloques 2 y 4 de `./scripts/demo_en_vivo.sh`.)*
>
> "Primero ejecutamos el job de Spark sobre 1 millón de lecturas: calcula los promedios de pH, conductividad y temperatura, y las alertas por zona. Después corremos el mismo cálculo con Hadoop Streaming. En esta corrida puntual con 1M, Spark tardó unos 5,4 s y Hadoop unos 4,1 s, lo mismo que mostró el E1 para volúmenes chicos.
>
> Por último corremos el playbook de **Ansible** una segunda vez. El `PLAY RECAP` muestra **changed=0**: la infraestructura ya estaba en el estado deseado y no se modificó nada. Eso es idempotencia."

### Diapositiva 20 — E5 · Latencia del lazo cerrado *(15:30 – 16:20)*
> "En el E5 medimos la latencia real a través de Mosquitto y el controlador, con 1, 10 y 50 sensores concurrentes.
> - 1 sensor: media **0,11 ms**, P95 **0,49 ms**.
> - 10 sensores: media **2,22 ms**, P95 **4,56 ms**.
> - 50 sensores en ráfaga: media **7,56 ms**, P95 **19,56 ms**.
>
> Es decir, el 95 % de las reacciones ocurre en menos de 20 ms, muy por debajo de los tiempos químicos y biológicos del cultivo. Alcanza para tiempo real blando."

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
