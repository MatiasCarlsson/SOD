# Guion de Exposición Oral — PERSONA 1

> **Rol en la defensa:** apertura, contexto agronómico, objetivos, virtualización (Proxmox vs. Docker), arquitectura, simulación IoT, **Demo 1** y cierre.
> **Presentación:** `docs/Presentacion_TIF_SOD_2026.pptx` — 24 diapositivas, estilo *Textmode Overlay* (terminal), transición *fade* y videos MP4 embebidos.
> **Duración de tu parte:** ~9 minutos, alternando con Persona 2 (total ~18 min).
> **Pista visual:** el color de la etiqueta arriba a la derecha indica quién habla — **verde = Persona 1**, ámbar = Persona 2, blanco = ambos.

---

## Bloque A — Contexto y teoría (0:00 – 4:40)

### Diapositiva 1 — Portada `./defensa --start` *(0:00 – 0:40)*
> "Buenas tardes a los integrantes del tribunal y compañeros. Hoy presentamos nuestro Trabajo Integrador Final de Sistemas Operativos Distribuidos: un **sistema automatizado de cultivo hidropónico distribuido**.
>
> El equipo lo integramos **[Nombre Persona 2]** y quien les habla, **[Nombre Persona 1]**. Todo lo que van a ver —métricas, gráficos y videos— sale de mediciones reales de nuestro laboratorio."

### Diapositiva 2 — Agenda `ls -la ./defensa` *(0:40 – 1:10)*
> "La exposición tiene cinco bloques: el contexto del problema, el marco teórico, la arquitectura con una primera demo, los resultados con dos demos más, y el cierre. El color de cada bloque indica quién lo expone."

### Diapositiva 3 — Hidroponía: sin margen de error *(1:10 – 2:00)*
> "¿Por qué hidroponía? En un sistema NFT no hay suelo que amortigüe errores: las raíces dependen por completo de la solución recirculante.
>
> Estos cuatro números son el margen de seguridad: pH entre **5,5 y 6,5**; fuera de ese rango precipitan hierro, calcio y fósforo. Tanque por debajo del **30 %**: las bombas cavitan. Temperatura entre **18 y 24 °C**, y conductividad entre **1,2 y 2,5 mS/cm**.
>
> La consecuencia es que una desviación no detectada se convierte en pérdida de cultivo en horas. Necesitamos medir siempre y reaccionar sin intervención humana."

### Diapositiva 4 — Del cultivo a los Sistemas Distribuidos *(2:00 – 2:45)*
> "Cada una de esas necesidades es un problema clásico de nuestra materia:
> - **Desacoplamiento:** sensores y actuadores que no se conocen entre sí → MQTT.
> - **Tiempo real:** reaccionar en milisegundos → control en lazo cerrado.
> - **Tolerancia a fallos:** si cae un nodo, que se recupere solo → k3s.
> - **Escalabilidad:** analizar millones de lecturas → Spark frente a Hadoop."

### Diapositiva 5 — Objetivos *(2:45 – 3:30)*
> "De ahí salen cinco objetivos: **comparar** virtualización completa con contenedores, y MapReduce con Spark; **desplegar** un laboratorio reproducible con Docker Compose y Ansible; **simular** sensores realistas con un controlador en lazo cerrado; **orquestar** un clúster k3s multinodo; y **medir** cinco experimentos, E1 a E5, con repeticiones."

### Diapositiva 6 — Separador `02 // MARCO TEÓRICO` *(3:30 – 3:40)*
> "Antes de la implementación, repasemos las bases teóricas."

### Diapositiva 7 — KVM (Proxmox) vs. Docker *(3:40 – 4:40)*
> "En la base está la virtualización. **Proxmox** usa KVM, un hipervisor tipo 1: cada máquina virtual emula hardware y corre su propio kernel. Eso da un aislamiento fuerte, pero cuesta RAM reservada y arranques de 30 a 90 segundos.
>
> **Docker** virtualiza a nivel de sistema operativo: todos los contenedores comparten el kernel del host y se aíslan con **namespaces** y **cgroups**. Arrancan en uno o dos segundos.
>
> Por eso, como muestra el recuadro de decisión, Proxmox lo analizamos en teoría y en el laboratorio usamos Docker para emular varios nodos y un clúster k3s en una sola máquina.
>
> Le paso la palabra a **[Nombre Persona 2]** para la orquestación y la mensajería."
>
> `[Handoff → Persona 2 en Diapositiva 8]`

---

## Bloque B — Arquitectura y Demo 1 (7:20 – 11:00)

> *(Retomás la palabra después de la Diapositiva 10 de Persona 2)*

### Diapositiva 11 — Separador `03 // ARQUITECTURA` *(7:20 – 7:30)*
> "Gracias. Con la teoría clara, veamos cómo lo construimos."

### Diapositiva 12 — Arquitectura del laboratorio *(7:30 – 8:40)*
> "El flujo se lee de izquierda a derecha. **(1)** Los sensores corren en Docker o como pods de k3s y publican en **(2)** Mosquitto, puerto 1883.
>
> Desde el broker el flujo se bifurca: **(3A)** el controlador evalúa cada lectura y ordena al actuador que corresponda, y además registra la latencia; **(3B)** el recolector acumula lecturas en memoria y las vuelca en lotes JSON atómicos en `data/raw/`.
>
> Esos datos alimentan **(4)** el procesamiento distribuido con Spark, Hadoop y una línea base en Python. Y **(5)** Ansible verifica todo el entorno de forma idempotente."

### Diapositiva 13 — Simulación y control reactivo *(8:40 – 9:40)*
> "Los sensores son simulados pero realistas: cinco variables, ruido gaussiano, deriva sinusoidal, evaporación y alrededor de un **8 % de anomalías** inyectadas para exigir al controlador. La semilla fija hace que todo sea reproducible.
>
> En la tabla están las reglas: pH mayor a 6,5 → `DOSIFICAR_ACIDO`; menor a 5,5 → `DOSIFICAR_BASE`; agua por debajo del 30 % → `REPONER_AGUA`; y temperatura fuera de 18–24 °C → enfriador o calefactor.
>
> La latencia fin a fin es el tiempo entre que el sensor emite la lectura y el controlador despacha la orden. Se guarda en un CSV y es la base del experimento E5."

### Diapositiva 14 — Demo 1 · Lazo cerrado IoT *(9:40 – 11:00)*
> *(Nota: hacé **clic sobre el video** para reproducirlo dentro de la diapositiva, o ejecutá el Bloque 1 de `./scripts/demo_en_vivo.sh`.)*
>
> "Veámoslo funcionando. Levantamos el stack con `docker compose up -d`: broker, sensor, controlador y recolector. Con `docker compose ps` comprobamos que los cuatro servicios están arriba en segundos.
>
> En los logs vemos que el sensor y el controlador se conectan al broker y se suscriben a `hidroponia/+/telemetria`. Y con `ls data/raw/` comprobamos que el recolector ya está escribiendo los lotes JSON."
>
> *(Solo si lo ejecutás en vivo y aparece la línea del controlador:)* "Ahí está: llegó un pH por encima de 6,5 y el controlador emitió `DOSIFICAR_ACIDO` al instante."
>
> "Le cedo la palabra a **[Nombre Persona 2]** para los resultados."
>
> `[Handoff → Persona 2 en Diapositiva 15]`

---

## Bloque C — Cierre (16:50 – 18:30)

> *(Retomás la palabra después de la Diapositiva 21 de Persona 2)*

### Diapositiva 22 — Separador `05 // CIERRE` *(16:50 – 16:55)*
> "Vamos cerrando."

### Diapositiva 23 — Conclusiones, columna verde *(16:55 – 17:20)*
> "Desde la infraestructura y la capa IoT:
> - Docker y k3d nos permitieron modelar un clúster multinodo con una fracción de los recursos de las máquinas virtuales.
> - MQTT desacopló productores y consumidores con latencias de milisegundos.
> - Separar el control reactivo de la ingesta batch le dio estabilidad al sistema ante picos de carga."
>
> *(Persona 2 completa la columna ámbar y lee la tesis.)*

### Diapositiva 24 — Trabajo futuro y preguntas *(17:50 – 18:30)*
> "Como trabajo futuro proponemos tres líneas: **Kafka** para retener eventos de forma distribuida, **Prometheus y Grafana** para observar pods, workers y pH en tiempo real, y **Ceph sobre Proxmox** para almacenamiento distribuido en un clúster físico.
>
> El repositorio, con el informe, el código y los datasets reproducibles, está en el enlace. Muchas gracias por su atención; quedamos a disposición para sus preguntas."
