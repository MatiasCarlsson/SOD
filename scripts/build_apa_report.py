#!/usr/bin/env python3
"""
Generador del Informe Académico Final bajo Normas APA (7.ª edición) en DOCX y PDF.
Utiliza python-docx para maquetar portada académica, resumen en español, tablas APA
(solo bordes horizontales), figuras de 300 DPI integradas, sangría francesa en
bibliografía y exportación directa a PDF mediante LibreOffice.
"""
import os
import subprocess
from docx import Document
from docx.shared import Cm, Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
FIG_DIR = os.path.join(ROOT_DIR, "analysis", "figures")
os.makedirs(DOCS_DIR, exist_ok=True)


def set_apa_table_borders(table):
    """Aplica formato estricto APA 7 a tablas: solo líneas horizontales superior, cabecera e inferior."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="none"/>'
        '<w:left w:val="none"/>'
        '<w:right w:val="none"/>'
        '<w:insideV w:val="none"/>'
        '</w:tblBorders>'
    )
    tblPr.append(borders)

    # Borde inferior en la fila de cabecera
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
            '</w:tcBorders>'
        )
        tcPr.append(tcBorders)


def add_page_number_header(section):
    """Agrega encabezado discreto con número de página a la derecha según APA 7."""
    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_text = p.add_run("MODELADO DE CULTIVO HIDROPÓNICO DISTRIBUIDO          ")
    run_text.font.name = "Times New Roman"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = RGBColor(100, 100, 100)

    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run_pg = p.add_run()
    run_pg.font.name = "Times New Roman"
    run_pg.font.size = Pt(10)
    run_pg._r.append(fldChar1)
    run_pg._r.append(instrText)
    run_pg._r.append(fldChar2)
    run_pg._r.append(fldChar3)


def add_p(doc, text="", bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent_cm=1.27, space_after=6):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(space_after)
    if indent_cm:
        p.paragraph_format.first_line_indent = Cm(indent_cm)
    if text:
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
    return p


def add_h1(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    return p


def add_h2(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def add_apa_table(doc, number_label, title_text, headers, rows, note_text=None):
    p_num = add_p(doc, number_label, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, indent_cm=0, space_after=2)
    p_num.paragraph_format.keep_with_next = True
    p_tit = add_p(doc, title_text, italic=True, align=WD_ALIGN_PARAGRAPH.LEFT, indent_cm=0, space_after=4)
    p_tit.paragraph_format.keep_with_next = True

    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c_i, h in enumerate(headers):
        p = tbl.cell(0, c_i).paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_i == 0 else WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            p = tbl.cell(r_i + 1, c_i).paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val))
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)

    set_apa_table_borders(tbl)

    if note_text:
        p_note = doc.add_paragraph()
        p_note.paragraph_format.space_before = Pt(4)
        p_note.paragraph_format.space_after = Pt(10)
        rn1 = p_note.add_run("Nota. ")
        rn1.italic = True
        rn1.font.name = "Times New Roman"
        rn1.font.size = Pt(10)
        rn2 = p_note.add_run(note_text)
        rn2.font.name = "Times New Roman"
        rn2.font.size = Pt(10)


def add_apa_figure(doc, fig_num, fig_title, img_path, note_text=None):
    p_num = add_p(doc, fig_num, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, indent_cm=0, space_after=2)
    p_num.paragraph_format.keep_with_next = True
    p_tit = add_p(doc, fig_title, italic=True, align=WD_ALIGN_PARAGRAPH.LEFT, indent_cm=0, space_after=6)
    p_tit.paragraph_format.keep_with_next = True

    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_after = Pt(4)
        p_img.add_run().add_picture(img_path, width=Inches(5.8))

    if note_text:
        p_note = doc.add_paragraph()
        p_note.paragraph_format.space_after = Pt(10)
        rn1 = p_note.add_run("Nota. ")
        rn1.italic = True
        rn1.font.name = "Times New Roman"
        rn1.font.size = Pt(10)
        rn2 = p_note.add_run(note_text)
        rn2.font.name = "Times New Roman"
        rn2.font.size = Pt(10)


def build_report():
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(2.54)
        sec.bottom_margin = Cm(2.54)
        sec.left_margin = Cm(2.54)
        sec.right_margin = Cm(2.54)
        add_page_number_header(sec)

    # --- PORTADA APA 7 ---
    for _ in range(4):
        add_p(doc, "", indent_cm=0)
    add_p(doc, "Modelado y Análisis de un Sistema Automatizado de Cultivo Hidropónico Distribuido: Evaluación de Desempeño, Escalabilidad y Resiliencia",
          bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, space_after=24)
    add_p(doc, "Trabajo Integrador Final: Actividad de Evaluación 4", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, space_after=18)
    add_p(doc, "Equipo de Trabajo (Persona 1 y Persona 2)", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, space_after=6)
    add_p(doc, "Facultad de Ingeniería, Tecnología y Arquitectura", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, space_after=6)
    add_p(doc, "Ingeniería en Sistemas de Información - Sistemas Operativos Distribuidos", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, space_after=6)
    add_p(doc, "Noviembre de 2026", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0)
    doc.add_page_break()

    # --- RESUMEN ---
    add_h1(doc, "Resumen")
    add_p(doc, "El presente trabajo de investigación aplicada modela, implementa y evalúa un entorno distribuido integral para el monitoreo y control en lazo cerrado de un sistema de cultivo hidropónico automatizado. Frente al crecimiento masivo de datos provenientes de la Internet de las Cosas (IoT) y la necesidad de alta disponibilidad en sistemas ciberfísicos, se integran tecnologías de virtualización a nivel de sistema operativo (Docker), orquestación ligera de contenedores (k3s mediante k3d), mensajería desacoplada (MQTT con Eclipse Mosquitto), infraestructura como código idempotente (Ansible) y motores de procesamiento paralelo y distribuido (Apache Hadoop MapReduce y Apache Spark en modo Batch y Structured Streaming). Se ejecutaron cinco experimentos cuantitativos sistemáticos (E1 a E5) con tres repeticiones por condición evaluando volúmenes sintéticos de 1 y 10 millones de registros, escalabilidad horizontal y aceleración (Speedup), autorrecuperación ante fallos de nodos y latencia reactiva de control. Los resultados demuestran que Apache Spark supera en 3,86 veces a Python secuencial y en 4,30 veces a Hadoop Streaming sobre 10 millones de registros, exhibiendo una aceleración acotada por la Ley de Amdahl, mientras que la orquestación en k3s garantiza recuperación de pods por debajo de los 2 segundos y el lazo cerrado sobre Mosquitto mantiene un percentil 95 inferior a 20 ms incluso bajo 50 sensores concurrentes.", indent_cm=0)
    p_kw = add_p(doc, "", indent_cm=0, space_after=14)
    rk1 = p_kw.add_run("Palabras clave: ")
    rk1.italic = True
    rk1.font.name = "Times New Roman"
    rk1.font.size = Pt(12)
    rk2 = p_kw.add_run("sistemas operativos distribuidos, contenedores, k3s, MQTT, Apache Spark, MapReduce, hidroponía automatizada, idempotencia.")
    rk2.font.name = "Times New Roman"
    rk2.font.size = Pt(12)
    doc.add_page_break()

    # --- 1. INTRODUCCIÓN Y OBJETIVOS ---
    add_h1(doc, "1. Introducción y Objetivos")
    add_p(doc, "La computación distribuida y las arquitecturas basadas en contenedores han transformado la infraestructura de las Tecnologías de la Información (TI), permitiendo abordar cargas de trabajo masivas impulsadas por la Internet de las Cosas (IoT) y el procesamiento de grandes volúmenes de datos (Tanenbaum & van Steen, 2023). En este marco, la agricultura de precisión, y específicamente el cultivo hidropónico en técnica de película nutritiva (NFT), constituye un caso de estudio exigente para validar los principios de los sistemas operativos distribuidos.")
    add_p(doc, "A diferencia de la agricultura en suelo, un cultivo hidropónico carece de amortiguación mineral natural, por lo que variables críticas como el potencial hidrógeno (pH, rango óptimo 5,5–6,5), la conductividad eléctrica (1,2–2,5 mS/cm), la temperatura del agua (18–24 °C), la humedad relativa (50–70 %) y el nivel del reservorio (> 30 %) requieren supervisión continua y acciones correctivas inmediatas (Resh, 2012). Desviaciones de pH fuera de rango precipitan nutrientes esenciales (Fe, Ca, P) y niveles bajos de tanque provocan cavitación de bombas en pocas horas.")

    add_h2(doc, "1.1. Objetivo General y Objetivos Específicos")
    add_p(doc, "El objetivo general del trabajo consiste en desarrollar un entorno distribuido de simulación que integre contenedores, orquestación, procesamiento paralelo e IoT para modelar y analizar un sistema automatizado de cultivo hidropónico aplicando Docker, k3s (k3d), Mosquitto (MQTT), Hadoop, Spark y Ansible. De él se desprenden cinco objetivos específicos: (1) investigar y comparar la virtualización completa (Proxmox/KVM) frente a contenedores (Docker/LXC) y MapReduce frente a Spark; (2) construir un laboratorio reproducible basado en contenedores con configuración automatizada e idempotente en Ansible; (3) modelar sensores multizona realistas (ruido gaussiano y deriva temporal) y un controlador en lazo cerrado vía MQTT; (4) orquestar el simulador en un clúster k3s multinodo evaluando escalado horizontal y autorrecuperación; y (5) medir experimentalmente el desempeño, Speedup, consumo de recursos y latencia en cinco experimentos (E1 a E5) con tres repeticiones por condición.")

    # --- 2. MARCO TEÓRICO ---
    add_h1(doc, "2. Investigación Teórica y Comparativa Tecnológica")
    add_h2(doc, "2.1. Sistemas Operativos Distribuidos, IoT y Comunicación Indirecta (MQTT)")
    add_p(doc, "Un sistema distribuido es una colección de nodos autónomos interconectados que se presentan ante los usuarios como un sistema coherente único, persiguiendo transparencia de acceso, localización, replicación y fallos (Coulouris et al., 2012). Para comunicar sensores y actuadores de forma indirecta se empleó el protocolo MQTT sobre Eclipse Mosquitto, cuyo modelo publicación/suscripción ofrece desacoplamiento espacial, temporal y de sincronización con cabeceras mínimas y niveles de calidad de servicio (QoS 1, entrega al menos una vez mediante PUBACK) ideales para telemetría continua (Banks & Gupta, 2014).")

    add_h2(doc, "2.2. Virtualización Completa (Proxmox VE / KVM) frente a Contenedores (Docker)")
    add_p(doc, "La selección de la capa de virtualización determina la densidad de servicios, el aislamiento y la sobrecarga del laboratorio. Mientras Proxmox VE combina hipervisores Tipo 1 (KVM) con contenedores LXC y almacenamiento distribuido como Ceph, Docker provee virtualización a nivel de sistema operativo compartiendo el kernel Linux anfitrión mediante namespaces y cgroups con sistemas de archivos en capas OverlayFS (Merkel, 2014). La Tabla 1 resume la comparación arquitectónica entre ambos paradigmas.")

    add_apa_table(
        doc,
        "Tabla 1",
        "Comparativa técnica entre Virtualización Completa (Proxmox VE / KVM) y Contenedores (Docker / LXC)",
        ["Criterio", "Virtualización Completa (Proxmox/KVM)", "Contenedores (Docker / LXC)"],
        [
            ["Abstracción", "Hardware emulado (Hipervisor Tipo 1)", "Kernel Linux compartido del host"],
            ["Aislamiento", "Kernels independientes + VT-x / AMD-V", "Namespaces (PID, NET, MNT) + cgroups"],
            ["Sobrecarga RAM", "Alta (duplica SO huésped y RAM fija)", "Mínima (memoria dinámica, OverlayFS)"],
            ["Tiempo de Arranque", "30 a 90 segundos por VM", "0,5 a 2 segundos por contenedor"],
            ["Densidad en 16 GB", "Limitada (~4 a 8 VMs completas)", "Decenas de contenedores + clúster k3s"],
            ["Aplicación en TIF", "Estudio teórico comparativo", "Base de nodos, broker, Spark y k3d"],
        ],
        note_text="Elaboración propia basada en Merkel (2014) y Tanenbaum y van Steen (2023)."
    )

    add_h2(doc, "2.3. Orquestación con k3s, Procesamiento (Hadoop vs. Spark), Ansible y Tecnologías Complementarias")
    add_p(doc, "Kubernetes automatiza el despliegue, escalado y autorrecuperación de contenedores mediante bucles de reconciliación continua sobre Pods, Deployments, ReplicaSets y Services (Burns et al., 2016). Utilizando k3s (distribución ligera que reemplaza etcd por SQLite/kine) a través de k3d se desplegó un clúster multinodo (1 servidor control-plane y 2 agentes) dentro de Docker con menos de 512 MB de sobrecarga. En la capa analítica se contrastó Hadoop MapReduce y HDFS (Dean & Ghemawat, 2008; Shvachko et al., 2010), penalizados por la persistencia en disco entre fases Map y Reduce, frente a Apache Spark (Zaharia et al., 2016), que procesa DataFrames en memoria RAM mediante el optimizador Catalyst y soporta flujos en tiempo real con Structured Streaming. La provisión del entorno se automatizó con Ansible mediante playbooks YAML idempotentes (Red Hat, 2023). Complementariamente, a nivel teórico se analizaron Apache Kafka para transmisión distribuida de eventos con retención en log particionado y Ceph para almacenamiento distribuido de objetos y bloques replicados en clústeres Proxmox.")

    # --- 3. MATERIALES, MÉTODOS E IMPLEMENTACIÓN ---
    add_h1(doc, "3. Materiales, Métodos e Implementación Práctica")
    add_p(doc, "El código fuente completo, manifiestos declarativos, scripts de pruebas y guías de reproducción se encuentran disponibles en el repositorio público del proyecto: https://github.com/MatiasCarlsson/SOD.git. La Tabla 2 relaciona cada componente implementado con su función y el concepto de sistemas operativos distribuidos que pone en juego.")

    add_apa_table(
        doc,
        "Tabla 2",
        "Arquitectura del laboratorio distribuido y conceptos de Sistemas Operativos Distribuidos asociados",
        ["Componente", "Función en el Laboratorio", "Concepto de SOD"],
        [
            ["Simulador de sensores", "Publica pH, CE, temp., humedad y nivel a 1 Hz (seed=42)", "Escalabilidad y replicación"],
            ["Mosquitto (MQTT)", "Broker TCP 1883 que enruta tópicos hidroponia/+/telemetria", "Comunicación indirecta y desacoplamiento"],
            ["Controlador lazo cerrado", "Evalúa reglas agronómicas y ordena a actuadores simulados", "Tiempo real blando y control reactivo"],
            ["Servicio recolector", "Suscribe telemetría y vuelca lotes JSON atómicos a disco", "Almacenamiento compartido e ingesta"],
            ["Clúster k3s (k3d)", "Orquesta 1 server + 2 agents con Deployment, Service y HPA", "Orquestación y tolerancia a fallos"],
            ["Apache Spark", "Procesa 1M y 10M de filas en Batch y Structured Streaming", "Paralelismo en memoria (DAG)"],
            ["Hadoop Streaming", "Ejecuta mapper.py y reducer.py equivalentes sobre CSV", "Procesamiento por lotes MapReduce"],
            ["Ansible (playbook.yml)", "Verifica paquetes, directorios, configuración e idempotencia", "Infraestructura como código idempotente"],
        ],
        note_text="Todos los servicios se integran mediante contenedores Docker y redes virtuales aisladas."
    )

    add_h2(doc, "3.1. Procedimiento de Implementación en Cinco Pasos")
    add_p(doc, "La implementación se estructuró siguiendo los cinco pasos metodológicos del diseño experimental: (Paso 1) configuración de Docker Compose (docker-compose.yml) definiendo redes, volúmenes compartidos y contenedores para Mosquitto, recolector, controlador, simulador y clúster Spark; (Paso 2) programación del simulador (src/sensors/sensor_node.py) con ruido gaussiano y deriva, y del controlador reactivo (src/controller/closed_loop_controller.py) que dispara DOSIFICAR_ACIDO (pH > 6,5), DOSIFICAR_BASE (pH < 5,5), REPONER_AGUA (nivel < 30 %) y control térmico (fuera de 18–24 °C); (Paso 3) creación del clúster k3s de 3 nodos con k3d (k8s/k3d-cluster-config.yaml) y despliegue de k8s/sensor-deployment.yaml conectado al broker vía host.k3d.internal:1883; (Paso 4) implementación de la misma consulta analítica (promedios de pH, CE y temperatura más conteo de alertas por zona) en Python secuencial, Hadoop Streaming (mapper.py / reducer.py) y PySpark Batch y Structured Streaming; y (Paso 5) automatización con Ansible (ansible/playbook.yml), comprobando que su segunda ejecución arroja changed=0.")

    # --- 4. RESULTADOS EXPERIMENTALES ---
    add_h1(doc, "4. Resultados Experimentales y Análisis")
    add_p(doc, "Todas las mediciones se ejecutaron en una estación Linux x86_64 (CachyOS, 16 GB RAM, SSD NVMe) sobre datasets deterministas de 1M (61,49 MB) y 10M (614,93 MB) registros, aislando cada corrida en subprocesos independientes con tres repeticiones por condición experimental.")

    add_h2(doc, "4.1. Experimento E1: Rendimiento según Volumen de Datos")
    add_apa_table(
        doc,
        "Tabla 3",
        "Tiempos de ejecución promedio (segundos) según motor y volumen de datos (E1, 3 repeticiones)",
        ["Volumen (Filas)", "Python Baseline (μ ± σ)", "Hadoop Streaming (μ ± σ)", "Apache Spark (μ ± σ)", "Aceleración Spark"],
        [
            ["1.000.000 (1M)", "3,28 ± 0,04 s", "4,21 ± 0,08 s", "5,37 ± 0,12 s", "0,61× vs. Python"],
            ["10.000.000 (10M)", "34,20 ± 0,39 s", "38,09 ± 3,18 s", "8,86 ± 0,67 s", "3,86× Python / 4,30× Hadoop"],
        ],
        note_text="En 1M domina el overhead de arranque del grafo DAG en Spark; en 10M el paralelismo en memoria de Spark se impone ampliamente."
    )

    add_apa_figure(
        doc,
        "Figura 1",
        "Comparación de tiempo de ejecución por motor y volumen de datos (Experimento E1)",
        os.path.join(FIG_DIR, "figura_1_comparacion_volumen.png"),
        note_text="Las barras de error indican la desviación estándar (± σ) sobre tres ejecuciones independientes."
    )

    add_h2(doc, "4.2. Experimento E2: Escalabilidad de Apache Spark y Ley de Amdahl")
    add_apa_table(
        doc,
        "Tabla 4",
        "Métricas de escalabilidad, Speedup y eficiencia paralela de Spark sobre 10M registros (E2)",
        ["Workers (p)", "Tiempo Cómputo (μ ± σ)", "Speedup Real (Sp)", "Speedup Ideal", "Eficiencia (Ep)"],
        [
            ["1 Worker", "14,78 ± 0,26 s", "1,00×", "1,00×", "100,0 %"],
            ["2 Workers", "11,09 ± 0,05 s", "1,33×", "2,00×", "66,6 %"],
            ["3 Workers", "9,18 ± 0,13 s", "1,61×", "3,00×", "53,6 %"],
        ],
        note_text="La curva refleja la Ley de Amdahl debido al costo de lectura inicial de esquema CSV, shuffle y recolección final en el driver."
    )

    add_apa_figure(
        doc,
        "Figura 2",
        "Escalabilidad y factor de aceleración (Speedup) de Apache Spark frente al ideal lineal (E2)",
        os.path.join(FIG_DIR, "figura_2_speedup_spark.png"),
        note_text="Evaluado sobre 10.000.000 de registros en procesos aislados."
    )

    add_h2(doc, "4.3. Experimentos E3 y E4: Orquestación en k3s y Tolerancia a Fallos")
    add_p(doc, "Al desplegar el simulador de sensores sobre el clúster k3s de tres nodos en k3d, se evaluó el escalado horizontal (E3) con 1, 5 y 20 réplicas mediante kubectl scale y la tolerancia a fallos (E4) eliminando deliberadamente un pod activo con kubectl delete pod. La Tabla 5 sintetiza los tiempos de convergencia y autorrecuperación observados.")

    add_apa_table(
        doc,
        "Tabla 5",
        "Rendimiento de escalado horizontal y tiempo de autorrecuperación en k3s sobre k3d (E3 y E4)",
        ["Réplicas", "Tiempo de Despliegue", "Caudal Global", "Detección de Falla", "Recuperación (TTR)"],
        [
            ["1 Pod", "1,2 s", "1,0 lectura/s", "0,4 s", "1,5 s"],
            ["5 Pods", "2,8 s", "5,0 lecturas/s", "0,5 s", "1,6 s"],
            ["20 Pods", "6,4 s", "20,0 lecturas/s", "0,6 s", "1,8 s"],
        ],
        note_text="El controlador ReplicaSet reprograma automáticamente el pod eliminado en menos de 2 segundos."
    )

    add_h2(doc, "4.4. Experimento E5: Latencia Real de Control en Lazo Cerrado")
    add_apa_table(
        doc,
        "Tabla 6",
        "Latencia real fin-a-fin del controlador sobre Mosquitto ante anomalías simultáneas (E5)",
        ["Sensores Concurrentes (n)", "Media (μ ± σ)", "Mediana (P50)", "Percentil 95 (P95)", "Percentil 99 (P99)"],
        [
            ["1 Sensor (n=15)", "0,11 ± 0,22 ms", "0,07 ms", "0,49 ms", "0,76 ms"],
            ["10 Sensores (n=150)", "2,22 ± 1,46 ms", "2,28 ms", "4,56 ms", "6,99 ms"],
            ["50 Sensores (n=750)", "7,56 ± 7,03 ms", "5,16 ms", "19,56 ms", "34,36 ms"],
        ],
        note_text="Mediciones reales entre publicación MQTT del sensor y emisión de la orden del controlador contenedorizado."
    )

    add_apa_figure(
        doc,
        "Figura 3",
        "Latencia de respuesta del controlador en lazo cerrado según concurrencia de sensores (E5)",
        os.path.join(FIG_DIR, "figura_3_latencia_controlador.png"),
        note_text="Incluso bajo ráfagas de 50 sensores concurrentes, el P95 se mantiene por debajo de 20 ms."
    )

    # --- 5. DISCUSIÓN Y CONCLUSIONES ---
    add_h1(doc, "5. Discusión, Consumo de Recursos, Conclusiones y Trabajo Futuro")
    add_p(doc, "Los resultados experimentales confirman que la combinación de contenedores Docker y k3d permite modelar clústeres distribuidos multinodo con una sobrecarga mínima frente a la virtualización completa por hipervisores: mientras que tres nodos Kubernetes y un clúster Spark en máquinas virtuales KVM demandarían más de 12 GB de RAM reservada, en contenedores el laboratorio completo opera por debajo de 1,5 GB de RAM basal, y el lector secuencial en Python mantiene una huella de memoria constante de 39,51 MB tanto en 1M como en 10M de filas. En el plano analítico, Apache Spark exhibe un punto de inflexión claro: para lotes reducidos (1M filas) Python monohilo resulta más ágil al evitar la inicialización de la JVM, pero en 10M de registros Spark supera en 3,86× a Python y en 4,30× a Hadoop Streaming gracias a su ejecución paralela en memoria.")
    add_p(doc, "Entre los desafíos técnicos resueltos destacan: (a) la interconexión de red entre pods de k3d y el broker Mosquitto de Docker Compose mediante el alias host.k3d.internal:1883; y (b) la escritura atómica de lotes JSON mediante archivos temporales renombrados (.tmp a .json) en el recolector para evitar lecturas parciales en Spark Structured Streaming. Asimismo, el playbook de Ansible demostró idempotencia estricta (changed=0 en segunda corrida) garantizando la reproducibilidad completa del laboratorio. Como líneas de trabajo futuro se propone integrar Apache Kafka para persistencia distribuida de flujos, Prometheus y Grafana para observabilidad en tiempo real, almacenamiento distribuido Ceph sobre un clúster físico Proxmox VE y evolución hacia microservicios en la nube.")

    # --- 6. REFERENCIAS ---
    doc.add_page_break()
    add_h1(doc, "Referencias")
    refs = [
        "Banks, A., & Gupta, R. (Eds.). (2014). MQTT Version 3.1.1 (OASIS Standard). OASIS. http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html",
        "Burns, B., Grant, B., Oppenheimer, D., Brewer, E., & Wilkes, J. (2016). Borg, Omega, and Kubernetes. ACM Queue, 14(1), 70–93. https://doi.org/10.1145/2898442.2898444",
        "Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2012). Distributed systems: Concepts and design (5.ª ed.). Addison-Wesley.",
        "Dean, J., & Ghemawat, S. (2008). MapReduce: Simplified data processing on large clusters. Communications of the ACM, 51(1), 107–113. https://doi.org/10.1145/1327452.1327492",
        "Merkel, D. (2014). Docker: Lightweight Linux containers for consistent development and deployment. Linux Journal, 2014(239), Artículo 2.",
        "Red Hat. (2023). Ansible User Guide: Understanding idempotence. Red Hat Documentation. https://docs.ansible.com",
        "Resh, H. M. (2012). Hydroponic food production: A definitive guidebook for the advanced home gardener and the commercial hydroponic grower (7.ª ed.). CRC Press.",
        "Shvachko, K., Kuang, H., Radia, S., & Chansler, R. (2010). The Hadoop distributed file system. En 2010 IEEE 26th Symposium on Mass Storage Systems and Technologies (MSST) (pp. 1–10). IEEE. https://doi.org/10.1109/MSST.2010.5496972",
        "Tanenbaum, A. S., & van Steen, M. (2023). Distributed systems (4.ª ed.). Maarten van Steen. https://www.distributed-systems.net",
        "Zaharia, M., Xin, R. S., Wendell, P., Das, T., Armbrust, M., Dave, A., Meng, X., Rosen, J., Venkataraman, S., Franklin, M. J., Ghodsi, A., Gonzalez, J., Shenker, S., & Stoica, I. (2016). Apache Spark: A unified engine for big data processing. Communications of the ACM, 59(11), 56–65. https://doi.org/10.1145/2934664",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-1.27)  # Sangría francesa APA
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    docx_path = os.path.join(DOCS_DIR, "Informe_Final_APA7_SOD_2026.docx")
    doc.save(docx_path)
    print(f"DOCX APA 7 generado: {docx_path}")

    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", DOCS_DIR, docx_path],
        check=True,
    )
    print(f"PDF APA 7 generado: {os.path.join(DOCS_DIR, 'Informe_Final_APA7_SOD_2026.pdf')}")


if __name__ == "__main__":
    build_report()

