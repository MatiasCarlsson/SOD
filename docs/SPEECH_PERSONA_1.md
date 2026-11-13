# Guion de Exposición Oral — PERSONA 1

> **Rol en la defensa:** Introducción, Fundamentos Agronómicos, Virtualización (Proxmox vs. Docker), Arquitectura del Sistema, Implementación IoT en Lazo Cerrado y **Demostración en Vivo 1**.  
> **Duración estimada de intervención:** ~9 minutos (distribuidos de forma alternada con Persona 2 para lograr una exposición dinámica de 17–18 minutos).

---

## Bloque A: Apertura, Contexto y Virtualización (Minutos 0:00 a 4:30)

### Diapositiva 1 — Portada *(0:00 – 0:45)*
> *(Mirando al tribunal, tono seguro y pausado)*
>
> "Buenas tardes a los integrantes del tribunal y compañeros. Hoy vamos a presentar nuestro Trabajo Integrador Final de Sistemas Operativos Distribuidos, titulado *'Modelado y análisis de un sistema automatizado de cultivo hidropónico distribuido'*.
>
> El equipo está integrado por **[Nombre Persona 2]** y quien les habla, **[Nombre Persona 1]**. A lo largo de los próximos 18 minutos vamos a recorrer tanto la investigación teórica comparativa de las herramientas como la implementación práctica de nuestro laboratorio, dos demostraciones en vivo y el análisis estadístico de los cinco experimentos que ejecutamos."

---

### Diapositiva 2 — El Problema y el Caso de Estudio: Hidroponía *(0:45 – 2:00)*
> `[Avanzar a Diapositiva 2]`
>
> "¿Por qué elegimos un cultivo hidropónico como caso de estudio? En la agricultura tradicional, el suelo actúa como un amortiguador natural de nutrientes y humedad. En cambio, en un sistema hidropónico —como la técnica de película nutritiva o NFT— las raíces están suspendidas directamente en una solución acuosa recirculante.
>
> Eso vuelve al sistema **crítico en tiempo real**: si el potencial hidrógeno (pH) supera el rango óptimo de 5,5 a 6,5, los nutrientes minerales precipitan y la planta deja de absorberlos; si el nivel del tanque cae por debajo del 30 %, las bombas trabajan en vacío y el cultivo puede perderse en cuestión de horas.
>
> Trasladado a nuestra materia, esto nos plantea cuatro desafíos concretos de sistemas distribuidos:
> 1. Necesitamos **comunicación desacoplada** entre múltiples zonas de sensores y actuadores.
> 2. Exige **control en lazo cerrado con baja latencia** ante anomalías.
> 3. Requiere **alta disponibilidad y tolerancia a fallos** si un nodo sensor cae.
> 4. Y, a gran escala, genera millones de lecturas que demandan **procesamiento paralelo distribuido**."

---

### Diapositiva 3 — Objetivos del Trabajo *(2:00 – 3:00)*
> `[Avanzar a Diapositiva 3]`
>
> "Para dar respuesta a este escenario, nos propusimos cinco objetivos clave:
> - En primer lugar, **investigar y comparar** los paradigmas de virtualización completa frente a contenedores, y de procesamiento por lotes tradicional frente a memoria distribuida.
> - En segundo lugar, **construir un laboratorio reproducible** basado en contenedores Docker, automatizado de forma idempotente con Ansible.
> - Tercero, **modelar el sistema hidropónico** mediante simuladores con ruido gaussiano y deriva temporal, conectados vía MQTT a un controlador automático.
> - Cuarto, **orquestar** los sensores en un clúster multinodo de k3s para probar escalado horizontal y autorrecuperación.
> - Y quinto, **medir y analizar** experimentalmente el desempeño mediante cinco baterías de pruebas (E1 a E5) repetidas al menos tres veces cada una."

---

### Diapositiva 4 — Marco Teórico I: Virtualización Completa vs. Contenedores *(3:00 – 4:30)*
> `[Avanzar a Diapositiva 4]`
>
> "Arrancando por la capa de infraestructura, en la asignatura analizamos **Proxmox VE**, una plataforma basada en hipervisor Tipo 1 con **KVM** para virtualización completa y **LXC** para contenedores.
>
> Como pueden ver en la tabla comparativa de la diapositiva, la diferencia central está en la capa de abstracción:
> - Una máquina virtual en KVM emula hardware completo y ejecuta su propio sistema operativo huésped con un kernel independiente. Eso brinda aislamiento extremo, pero paga una penalidad alta en memoria RAM fija y tiempos de arranque de 30 a 90 segundos.
> - Por el contrario, **Docker** realiza virtualización a nivel de sistema operativo: todos los contenedores comparten el kernel del host Linux, logrando el aislamiento mediante **namespaces** (que separan procesos, red y sistema de archivos) y **cgroups** (que limitan el consumo de CPU y memoria).
>
> Esta ligereza nos permite levantar en segundos varios nodos simulados en una computadora de laboratorio de 16 GB de RAM, manteniendo los mismos conceptos de red aislada, volúmenes y gestión de recursos.
>
> Ahora le paso la palabra a **[Nombre Persona 2]** para que profundice en la orquestación, la mensajería IoT y los motores de Big Data."
>
> `[Handoff -> Toma la palabra Persona 2 en Diapositiva 5]`

---

## Bloque B: Arquitectura, Capa IoT y DEMO EN VIVO 1 (Minutos 7:30 a 11:30)

> *(Retoma la palabra Persona 1 tras Diapositiva 6 de Persona 2)*

### Diapositiva 7 — Arquitectura General del Sistema *(7:30 – 8:45)*
> `[Avanzar a Diapositiva 7]`
>
> "Gracias. Viendo cómo encajan todas estas piezas juntas, en la Diapositiva 7 observamos la arquitectura completa de nuestro laboratorio distribuido.
>
> A la izquierda tenemos la capa de generación: las réplicas del **simulador de sensores** —que pueden ejecutarse tanto en Docker Compose como en el clúster **k3s**— publican sus lecturas hacia el **broker Eclipse Mosquitto** por el puerto 1883.
>
> A partir del broker, el flujo se bifurca de manera totalmente desacoplada hacia dos consumidores simultáneos:
> - Por un lado, nuestro **Controlador Reactivo en Lazo Cerrado**, que evalúa cada lectura en memoria en tiempo real y, si detecta una variable fuera de rango, publica inmediatamente una orden hacia el tópico del actuador correspondiente (por ejemplo, dosificar ácido o encender la bomba de agua).
> - Por otro lado, el **Servicio Recolector**, que acumula las lecturas en buffer y las persiste atómicamente en lotes JSON sobre un volumen compartido, dejándolas listas para ser consumidas tanto por **Apache Spark** (en modo Batch y Structured Streaming) como por **Hadoop MapReduce**."

---

### Diapositiva 8 — Simulación Hidropónica y Control en Lazo Cerrado *(8:45 – 9:45)*
> `[Avanzar a Diapositiva 8]`
>
> "Para que la simulación sea fiel a un entorno físico real, programamos los nodos sensores en Python con **semilla determinista** para reproducibilidad, incorporando **ruido térmico gaussiano** y **deriva temporal** —por ejemplo, una caída paulatina del nivel de agua por evapotranspiración y oscilaciones suaves de pH y temperatura— además de una tasa configurable de inyección de anomalías.
>
> El controlador implementa reglas agronómicas concretas:
> - Si el pH supera **6,5**, dispara la acción `DOSIFICAR_ACIDO`.
> - Si el pH cae debajo de **5,5**, dispara `DOSIFICAR_BASE`.
> - Si el nivel de agua baja de **30 %**, ordena `REPONER_AGUA`.
> - Y en cada evento anómalo registra el *timestamp* exacto desde que el sensor emitió la lectura hasta que el controlador despachó la orden al actuador, lo que nos permite medir la latencia real del lazo cerrado."

---

### Diapositiva 9 — DEMO EN VIVO 1: Stack IoT y Control Reactivo *(9:45 – 11:30)*
> `[Avanzar a Diapositiva 9 — Cambiar a la Terminal]`
>
> *(Nota operativa: Ejecutar `./scripts/demo_en_vivo.sh` o los comandos de Compose del Bloque 1. Si hubiera un inconveniente con la máquina en el aula, reproducir `docs/videos/01_demo_iot_lazo_cerrado.mp4`).*
>
> "Vamos a verlo funcionando en vivo. Aquí en la terminal levantamos el stack base con `docker compose up -d` incluyendo Mosquitto, el recolector, el controlador y un simulador de zona 1."
>
> *(Mostrar `docker compose ps`)*
> "Como pueden ver, los cuatro contenedores están activos y saludables en cuestión de segundos.
>
> Ahora observamos los logs en tiempo real del sensor y del controlador..."
> *(Esperar 4–5 segundos a que aparezca una línea `ACCION REPORTE` en amarillo/naranja)*
> "¡Ahí está! Fíjense en esa línea: el sensor reportó un pico anómalo de pH por encima de 6,5 e inmediatamente el controlador emitió la orden `DOSIFICAR_ACIDO` al tópico `dosificador_acido`, registrando una **latencia fin-a-fin por debajo de 1 milisegundo**."
>
> *(Mostrar `ls -lh data/raw/`)*
> "Y en paralelo, el recolector ya está escribiendo los lotes de archivos JSON en el volumen compartido `/data/raw`, listos para ser ingeridos por Spark Structured Streaming.
>
> Con esto comprobado en vivo, le cedo nuevamente la palabra a **[Nombre Persona 2]** para analizar los experimentos de Big Data y la segunda demo en Kubernetes."
>
> `[Handoff -> Toma la palabra Persona 2 en Diapositiva 10]`

---

## Bloque C: Cierre y Conclusiones Compartidas (Minutos 16:45 a 18:30)

> *(Retoma la palabra Persona 1 tras la Diapositiva 13 de Persona 2)*

### Diapositiva 14 — Conclusiones *(Parte 1: 16:45 – 17:15)*
> `[Avanzar a Diapositiva 14]`
>
> "Para ir cerrando, como conclusiones centrales de la arquitectura e infraestructura podemos destacar que:
> - La virtualización por contenedores Docker y k3d permitió modelar fielmente un entorno multinodo y multicomponente con una fracción mínima de recursos frente a máquinas virtuales completas.
> - El patrón publicación/suscripción sobre Mosquitto nos dio un desacoplamiento total con latencias en torno al milisegundo, ideales para control reactivo en lazo cerrado."
>
> *(Persona 2 completa los puntos de Big Data, k3s y Ansible en la misma Diapositiva 14)*

---

### Diapositiva 15 — Trabajo Futuro y Preguntas *(17:45 – 18:30)*
> `[Avanzar a Diapositiva 15]`
>
> "Finalmente, dejamos abiertas cuatro líneas claras de evolución futura para este laboratorio:
> 1. Incorporar **Apache Kafka** junto a Mosquitto para retención distribuida de eventos a largo plazo (*event sourcing*).
> 2. Desplegar un stack de observabilidad con **Prometheus y Grafana** para visualizar métricas de los pods y sensores en tableros web.
> 3. Evaluar almacenamiento distribuido con **Ceph** sobre **Proxmox VE** en un clúster físico multi-host.
> 4. Y migrar el controlador a microservicios con políticas de *service mesh* en la nube.
>
> Muchísimas gracias por su atención. Quedamos a disposición del tribunal para responder cualquier consulta."

