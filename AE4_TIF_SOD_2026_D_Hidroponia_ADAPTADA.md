**Facultad de Ingeniería, Tecnología y Arquitectura**

**Ingeniería en Sistemas de Información**

**Sistemas Operativos Distribuidos**

**Trabajo Integrador Final:** 

**Modelar y analizar un sistema automatizado de cultivo hidropónico**

*Versión adaptada – propuesta de simplificación para validación del equipo docente*

**Objetivos del Trabajo**

El trabajo deberá realizarse en grupos de un mínimo de dos (2) y un máximo de tres (3) integrantes, promoviendo el trabajo colaborativo y la integración de saberes de la cátedra de Sistemas Operativos Distribuidos.

**Objetivo general:** Desarrollar un entorno distribuido de simulación que integre contenedores, orquestación, procesamiento paralelo e Internet de las Cosas (IoT), con el fin de modelar y analizar un sistema automatizado de cultivo hidropónico (sensores, recolección de datos y control automático de actuadores), aplicando herramientas como Docker, k3s (mediante k3d), Mosquitto (MQTT), Hadoop, Spark y Ansible para evaluar su desempeño, escalabilidad y eficiencia en la gestión de datos en tiempo real.

**1\. Requisitos del Trabajo**

* **Formato:** Informe en formato APA (7.ª edición).

* **Contenido:** El trabajo debe incluir una investigación teórica de fuentes confiables y científicas y un componente práctico de implementación, simulación y medición.

* **Referencias:** Utilizar el formato APA para todas las citas, referencias y bibliografía.

* **Contenido del Informe:**

  * Introducción a los sistemas operativos distribuidos y su relevancia en la computación actual y las Tecnologías de la Información.

  * Investigación y análisis de las herramientas seleccionadas (Docker, k3s/Kubernetes, Mosquitto/MQTT, Hadoop, Spark, Ansible) y comparación teórica con Proxmox y la virtualización completa.

  * Implementación práctica de un laboratorio básico de procesamiento distribuido, con evidencias (capturas, fragmentos de configuración y enlace al repositorio).

  * Análisis de resultados y conclusiones.

* **Exposición y presentación:**

  * Demostración en vivo: levantar el laboratorio con docker compose up; sensores simulados publicando datos y el controlador reaccionando ante una lectura fuera de rango; ejecución del procesamiento en Spark; escalado del simulador en k3s (kubectl scale) y eliminación de un pod para observar la recuperación.

  * Defensa del documento escrito elegido.

**2\. Introducción**

* Breve explicación de los sistemas operativos distribuidos, su historia y su papel en la infraestructura de TI.

* Ventajas y desafíos de la virtualización (completa y por contenedores) y del procesamiento distribuido.

* Relevancia de herramientas como Docker, Kubernetes, Hadoop y Spark en entornos distribuidos, y del IoT como fuente de datos continua y masiva.

* La hidroponía y la agricultura de precisión como caso de estudio: monitoreo de pH, conductividad eléctrica, temperatura y nivel de agua, y control en lazo cerrado.

**3\. Objetivos del Trabajo**

* Investigar y comparar las principales herramientas de virtualización y orquestación para sistemas distribuidos (Proxmox/KVM, Docker, Kubernetes/k3s).

* Desarrollar habilidades prácticas en la configuración y administración de un entorno distribuido basado en contenedores, con configuración automatizada.

* Modelar un sistema hidropónico simple (sensores simulados y control automático por reglas) que sirva como fuente de datos del entorno distribuido.

* Aplicar conceptos teóricos de sistemas operativos distribuidos mediante la implementación y el análisis de un entorno de laboratorio.

* Medir y analizar la escalabilidad y el desempeño al variar el volumen de datos, la cantidad de workers y la cantidad de réplicas.

**4\. Investigación Teórica**

* **Virtualización y Proxmox:** arquitectura de Proxmox (KVM y contenedores LXC), virtualización completa frente a virtualización a nivel de sistema operativo y gestión de recursos. Se estudia de forma teórica y comparativa; no se instala en el laboratorio.

* **Docker:** contenedores, imágenes, redes y volúmenes; Docker Compose. Comparación de contenedores frente a máquinas virtuales.

* **Kubernetes y k3s:** orquestación de contenedores, nodos, pods, Deployments, Services, escalado y autorrecuperación. k3s como distribución ligera de Kubernetes y k3d como forma de ejecutarlo dentro de Docker.

* **Hadoop:** HDFS y MapReduce; su papel en el procesamiento de grandes volúmenes de datos, almacenamiento distribuido y procesamiento paralelo por lotes.

* **Spark:** procesamiento de datos en memoria, DataFrames y Structured Streaming; ventajas sobre Hadoop MapReduce y aplicaciones prácticas.

* **IoT y MQTT:** modelo de publicación/suscripción, broker, tópicos y niveles de calidad de servicio (QoS); comunicación indirecta en sistemas distribuidos.

* **Ansible:** gestión de configuración automatizada, inventarios, playbooks e idempotencia.

* **Fundamentos de hidroponía:** variables relevantes (pH, conductividad eléctrica, temperatura, humedad, nivel de agua) y sus rangos típicos, a partir de una fuente agronómica confiable.

* **Otros:** Kafka (transmisión de datos en tiempo real) y Ceph (almacenamiento distribuido en Proxmox), solo a nivel teórico y de forma optativa.

**5\. Materiales y Métodos**

* **Materiales de Software sugerido:**

  * Docker y Docker Compose: virtualización a nivel de sistema operativo; los «nodos» del laboratorio son contenedores.

  * k3d y kubectl: clúster k3s multinodo (1 servidor y 2 agentes) ejecutado dentro de Docker.

  * Eclipse Mosquitto como broker MQTT.

  * Python (paho-mqtt, numpy, pandas, PySpark) para el simulador de sensores, el controlador y el análisis.

  * Apache Spark en modo standalone (1 master y hasta 3 workers) con imágenes oficiales.

  * Hadoop en modo pseudo-distribuido en un contenedor, para ejecutar un único trabajo MapReduce (Hadoop Streaming con Python). Si los recursos del equipo no lo permiten, la comparación se hace entre Spark y Python simple, y Hadoop se desarrolla en la parte teórica.

  * Ansible para automatizar la instalación y preparación del entorno.

  * Git para el control de versiones; Jupyter y matplotlib para el análisis y los gráficos.

* **Requisitos de hardware:** computadora con al menos 16 GB de RAM y virtualización habilitada en la BIOS; Linux, o Windows 11 con WSL2 y Docker.

* **Datos de prueba:** lecturas sintéticas generadas con una semilla fija (pH, conductividad eléctrica, temperatura, humedad, nivel de agua, zona o bandeja y marca de tiempo), en volúmenes de 1 M y 10 M de registros y, si la memoria lo permite, 100 M. No se utilizan datos reales.

* **Arquitectura de referencia (mínima):**

| Componente | Función | Concepto de SOD que pone en juego |
| :---- | :---- | :---- |
| Simulador de sensores (réplicas) | Publica lecturas de pH, CE, temperatura, humedad y nivel de agua | Escalabilidad, transparencia de replicación |
| Mosquitto (broker MQTT) | Recibe las lecturas y las distribuye por tópicos | Comunicación indirecta, desacoplamiento |
| Recolector | Se suscribe al broker y guarda las lecturas en un volumen compartido | Almacenamiento compartido |
| Controlador automático | Aplica reglas sobre las lecturas y publica órdenes a actuadores simulados | Control en lazo cerrado, tiempo real |
| k3s (k3d) | Ejecuta el simulador con réplicas, balanceo y reinicio automático | Orquestación, escalado, tolerancia a fallos |
| Spark (master y workers) | Procesa las lecturas en paralelo, por lotes y en flujo | Paralelismo, tolerancia a fallos |
| Hadoop (un trabajo MapReduce) | Ejecuta el mismo cálculo para comparar con Spark | Procesamiento por lotes |
| Ansible | Instala y prepara el entorno de forma repetible | Configuración automatizada e idempotente |

* **Procedimiento de Implementación:**

  * Desarrollo local con Docker Compose de la simulación IoT, incorporación de k3s para la orquestación, procesamiento con Spark y Hadoop, automatización con Ansible y, finalmente, campaña de mediciones.

**6\. Implementación Práctica**

* **Paso 1: Configuración del entorno de virtualización con Docker**

  * Instalar Docker y Docker Compose y verificar el funcionamiento (docker run hello-world). Crear el repositorio Git del laboratorio.

  * Optativo: comparar el tiempo de arranque y el consumo de memoria de un contenedor frente a una máquina virtual (VirtualBox o KVM), para sustentar la comparación entre virtualización completa y por contenedores.

* **Paso 2: Simulación del sistema hidropónico (IoT)**

  * Programar el simulador de sensores (una lectura por segundo por sensor, con ruido y deriva) y levantar Mosquitto, el recolector y el controlador con Docker Compose.

  * Implementar reglas simples en el controlador, por ejemplo: si el pH supera 6,5, publicar la orden «dosificar ácido»; si el nivel de agua baja de un umbral, publicar «reponer agua».

* **Paso 3: Orquestación con k3s (k3d)**

  * Crear un clúster de 3 nodos (1 servidor y 2 agentes) y desplegar el simulador de sensores mediante un Deployment y un Service.

  * Escalar con kubectl scale (1, 5 y 20 réplicas), eliminar un pod y observar cómo se reprograma. Optativo: configurar un HorizontalPodAutoscaler.

* **Paso 4: Despliegue del clúster de datos con Hadoop y Spark**

  * Levantar Spark standalone con un master y workers; ejecutar un trabajo en PySpark que calcule promedios por zona y por ventana de tiempo y cuente alertas por valores fuera de rango.

  * Ejecutar el procesamiento en tiempo real con Structured Streaming sobre la carpeta donde el recolector deja las lecturas.

  * Ejecutar el mismo cálculo como trabajo MapReduce en Hadoop y comparar los tiempos con Spark.

* **Paso 5: Automatización con Ansible**

  * Escribir un playbook que instale y prepare Docker, k3d y kubectl y clone el repositorio. Ejecutarlo dos veces y demostrar que la segunda ejecución no produce cambios (idempotencia).

* **Paso 6: Experimentos y mediciones**

  * Repetir cada experimento al menos 3 veces e informar media y desvío estándar. El uso de CPU y RAM se registra con docker stats o kubectl top.

| Experimento | Qué se varía | Qué se mide |
| :---- | :---- | :---- |
| E1. Volumen de datos | 1 M, 10 M y 100 M de lecturas; Python simple, Hadoop y Spark | Tiempo de ejecución, CPU y RAM |
| E2. Escalabilidad de Spark | 1, 2 y 3 workers | Tiempo de ejecución y aceleración (speedup) |
| E3. Escalado en k3s | 1, 5 y 20 réplicas del simulador | Lecturas por segundo y tiempo hasta que cada pod está listo |
| E4. Tolerancia a fallos | Eliminar un pod; detener un worker de Spark | Tiempo de recuperación y datos perdidos |
| E5. Control automático | Cantidad de sensores | Latencia entre una lectura fuera de rango y la orden al actuador |

**7\. Análisis de Resultados y Discusión**

* **Desempeño y Comparación:**

  * Comparación de tiempos de respuesta entre Python simple, Hadoop y Spark para distintos volúmenes de datos, y aceleración de Spark al agregar workers.

  * Evaluación del rendimiento de la infraestructura: costo de ejecutar el simulador en contenedores y en k3s, y comparación con una máquina virtual si se realizó el contraste del Paso 1\.

  * Efecto del escalado de réplicas sobre el caudal de lecturas procesadas.

* **Consumo de Recursos:** Análisis del uso de CPU, RAM y almacenamiento en las distintas herramientas implementadas.

* **Tolerancia a fallos:** tiempo de recuperación ante la caída de un pod o de un worker, y datos perdidos.

* **Ventajas y Desafíos:**

  * Describir los desafíos enfrentados al integrar múltiples herramientas y sus posibles soluciones.

  * Identificar oportunidades de optimización en el entorno distribuido.

**8\. Conclusión**

* Resumen de hallazgos y aprendizajes clave sobre la administración de sistemas distribuidos.

* Reflexión sobre las posibilidades de expansión y optimización del entorno distribuido.

* Propuestas para futuros trabajos prácticos, como la integración de Kafka para la transmisión de datos, la virtualización con Proxmox, tableros de monitoreo con Prometheus y Grafana, o la implementación de microservicios.

**9\. Entregables y Cronograma Sugerido**

| Semana | Actividades principales | Entregable |
| :---- | :---- | :---- |
| 1 | Entorno con Docker y Compose, simulador de sensores, Mosquitto, recolector y controlador; investigación teórica inicial | Repositorio con el laboratorio base funcionando y borrador del marco teórico |
| 2 | Clúster k3s con k3d, Spark standalone y trabajo MapReduce en Hadoop; playbook de Ansible | Procesamientos ejecutándose y primeras mediciones |
| 3 | Experimentos E1 a E5, gráficos, redacción final del informe y preparación de la defensa | Informe APA (PDF), repositorio final y presentación de apoyo |

* Repositorio Git con un archivo README.md que permita a un tercero reproducir el entorno paso a paso.

* Informe final en formato APA y presentación de apoyo para la defensa.

**10\. Bibliografía**

* Formato APA: citar toda la literatura utilizada para la investigación y configuración de las herramientas.

* Bibliografía sugerida de partida (el grupo debe verificar cada referencia y ampliarla con fuentes propias):

  * Banks, A., & Gupta, R. (Eds.). (2014). MQTT version 3.1.1 (OASIS Standard). OASIS. http\://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html

  * Burns, B., Grant, B., Oppenheimer, D., Brewer, E., & Wilkes, J. (2016). Borg, Omega, and Kubernetes. ACM Queue, 14(1), 70–93. https\://doi.org/10.1145/2898442.2898444

  * Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2012). Distributed systems: Concepts and design (5.ª ed.). Addison-Wesley.

  * Dean, J., & Ghemawat, S. (2008). MapReduce: Simplified data processing on large clusters. Communications of the ACM, 51(1), 107–113. https\://doi.org/10.1145/1327452.1327492

  * Merkel, D. (2014). Docker: Lightweight Linux containers for consistent development and deployment. Linux Journal, 2014(239), Artículo 2\.

  * Resh, H. M. (2012). Hydroponic food production (7.ª ed.). CRC Press.

  * Shvachko, K., Kuang, H., Radia, S., & Chansler, R. (2010). The Hadoop distributed file system. En 2010 IEEE 26th Symposium on Mass Storage Systems and Technologies (MSST) (pp. 1–10). IEEE. https\://doi.org/10.1109/MSST.2010.5496972

  * Tanenbaum, A. S., & van Steen, M. (2023). Distributed systems (4.ª ed.). distributed-systems.net.

  * Zaharia, M., Xin, R. S., Wendell, P., Das, T., Armbrust, M., Dave, A., Meng, X., Rosen, J., Venkataraman, S., Franklin, M. J., Ghodsi, A., Gonzalez, J., Shenker, S., & Stoica, I. (2016). Apache Spark: A unified engine for big data processing. Communications of the ACM, 59(11), 56–65. https\://doi.org/10.1145/2934664

**Anexo. Resumen de las adecuaciones respecto de la consigna original**

| Elemento | Consigna original | Adecuación propuesta |
| :---- | :---- | :---- |
| Virtualización | Proxmox con múltiples máquinas virtuales | Docker como virtualización a nivel de sistema operativo sobre Linux o WSL2. Proxmox se estudia en la teoría y, de forma optativa, se contrasta con una máquina virtual. |
| Kubernetes | Clúster Kubernetes | k3s mediante k3d: clúster de 3 nodos dentro de Docker, con los mismos conceptos (pods, Deployments, Services, escalado). |
| Hadoop | Clúster Hadoop en modo clúster | Hadoop pseudo-distribuido en un contenedor, con un único trabajo MapReduce para comparar con Spark. |
| Spark | Integrar Spark y comparar con Hadoop | Spark standalone con 1 a 3 workers; se mantiene la comparación con Hadoop. |
| Ansible | Automatizar nodos en Proxmox, Docker y Kubernetes | Un playbook idempotente que instala y prepara Docker, k3d y kubectl. |
| IoT e hidroponía | Mencionados en el objetivo, sin pasos concretos | Simulador de sensores, broker MQTT y controlador automático por reglas, que generan los datos a procesar. |
| Ceph y Kafka | Introducir como herramientas complementarias | Solo investigación teórica, de forma optativa. |
| Análisis | Comparación de tiempos y consumo de recursos | Se mantiene, con cinco experimentos definidos (E1 a E5). |
| Cronograma | No especificado | Tres semanas sugeridas, con entregables por semana. |

**Puntos a validar con el equipo docente:**

* Si Docker (con una máquina virtual optativa de contraste) reemplaza a Proxmox en la parte de virtualización.

* Si k3s ejecutado con k3d se acepta como Kubernetes.

* Si un único trabajo MapReduce en Hadoop pseudo-distribuido alcanza para la comparación con Spark.

* Si el simulador de sensores con MQTT y control automático cubre la parte de IoT e hidroponía.