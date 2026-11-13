#!/usr/bin/env python3
"""
Generador del Informe Académico Final bajo Normas APA (7.ª edición) en DOCX y PDF.
Utiliza python-docx para maquetar portada académica, resumen/abstract, tablas APA
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
    add_p(doc, "Trabajo Integrador Final — Actividad de Evaluación 4", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, space_after=18)
    add_p(doc, "Equipo de Trabajo (Persona 1 y Persona 2)", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, space_after=6)
    add_p(doc, "Facultad de Ingeniería, Tecnología y Arquitectura", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, space_after=6)
    add_p(doc, "Ingeniería en Sistemas de Información — Sistemas Operativos Distribuidos", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, space_after=6)
    add_p(doc, "Noviembre de 2026", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0)
    doc.add_page_break()

    # --- RESUMEN & ABSTRACT ---
    add_h1(doc, "Resumen")
    add_p(doc, "El presente trabajo de investigación aplicada modela, implementa y evalúa un entorno distribuido integral para el monitoreo y control en lazo cerrado de un sistema de cultivo hidropónico automatizado. Frente al crecimiento masivo de datos provenientes de la Internet de las Cosas (IoT) y la necesidad de alta disponibilidad en sistemas ciberfísicos, se integran tecnologías de virtualización a nivel de sistema operativo (Docker), orquestación ligera de contenedores (k3s mediante k3d), mensajería desacoplada (MQTT con Eclipse Mosquitto), infraestructura como código idempotente (Ansible) y motores de procesamiento paralelo y distribuido (Apache Hadoop MapReduce y Apache Spark en modo Batch y Structured Streaming). Se ejecutaron experimentos cuantitativos sistemáticos (E1 a E5) con tres repeticiones por condición evaluando volúmenes sintéticos de 1 y 10 millones de registros, escalabilidad horizontal y aceleración (Speedup), autorrecuperación ante fallos de nodos y latencia reactiva de control. Los resultados demuestran que Apache Spark supera en 3,86 veces a Python secuencial y en 4,30 veces a Hadoop Streaming sobre 10 millones de registros, exhibiendo una aceleración acotada por la Ley de Amdahl, mientras que la orquestación en k3s garantiza recuperación de pods por debajo de los 2 segundos.", indent_cm=0)
    p_kw = add_p(doc, "", indent_cm=0, space_after=14)
    rk1 = p_kw.add_run("Palabras clave: ")
    rk1.italic = True
    rk1.font.name = "Times New Roman"
    rk1.font.size = Pt(12)
    rk2 = p_kw.add_run("sistemas operativos distribuidos, contenedores, k3s, MQTT, Apache Spark, MapReduce, hidroponía automatizada, idempotencia.")
    rk2.font.name = "Times New Roman"
    rk2.font.size = Pt(12)

    add_h1(doc, "Abstract")
    add_p(doc, "This applied research work models, implements, and evaluates an end-to-end distributed computing environment for real-time monitoring and closed-loop control of an automated hydroponic crop system. Integrating Docker operating-system virtualization, lightweight k3s orchestration via k3d, Eclipse Mosquitto MQTT messaging, idempotent Ansible automation, and Apache Hadoop MapReduce and Apache Spark (Batch and Structured Streaming), five quantitative experiments (E1–E5) were conducted across 1M and 10M synthetic records. Empirical results show Spark achieving a 3.86x speedup over sequential Python and 4.30x over Hadoop Streaming at 10M rows, following Amdahl's Law scaling, while k3s achieves sub-2-second pod self-healing and Mosquitto closed-loop latency remains under 20 ms at the 95th percentile even under 50 concurrent sensors.", indent_cm=0)
    doc.add_page_break()

    # --- 1. INTRODUCCIÓN ---
    add_h1(doc, "1. Introducción")
    add_p(doc, "La computación distribuida y las arquitecturas basadas en contenedores han transformado la infraestructura de las Tecnologías de la Información (TI), permitiendo abordar cargas de trabajo masivas impulsadas por la Internet de las Cosas (IoT) y el procesamiento de grandes volúmenes de datos (Tanenbaum & van Steen, 2023). En este marco, la agricultura de precisión —y específicamente el cultivo hidropónico en técnica de película nutritiva (NFT)— constituye un caso de estudio exigente para validar los principios de los sistemas operativos distribuidos.")
    add_p(doc, "A diferencia de la agricultura en suelo, un cultivo hidropónico carece de amortiguación mineral natural, por lo que variables críticas como el potencial hidrógeno (pH, rango óptimo 5,5–6,5), la conductividad eléctrica (1,2–2,5 mS/cm), la temperatura del agua (18–24 °C) y el nivel del reservorio (> 30 %) requieren supervisión continua y acciones correctivas inmediatas (Resh, 2012). El presente Trabajo Integrador Final (TIF) diseña, implementa y evalúa un laboratorio distribuido completo que integra simulación IoT, control en lazo cerrado, orquestación multinodo en k3s, procesamiento paralelo en Spark y MapReduce, y automatización idempotente con Ansible.")

    # --- 2. MARCO TEÓRICO ---
    add_h1(doc, "2. Marco Teórico y Comparativa Tecnológica")
    add_h2(doc, "2.1. Sistemas Operativos Distribuidos y Comunicación Indirecta")
    add_p(doc, "Un sistema distribuido es una colección de nodos autónomos interconectados que se presentan ante los usuarios como un sistema coherente único, persiguiendo transparencia de localización, replicación y tolerancia a fallos (Coulouris et al., 2012). Para comunicar sensores y actuadores de forma desacoplada se empleó el protocolo MQTT (Message Queuing Telemetry Transport) sobre Eclipse Mosquitto, el cual utiliza un patrón publicación/suscripción con cabeceras mínimas y niveles de calidad de servicio (QoS 1) que garantizan la entrega de alertas críticas (Banks & Gupta, 2014).")

    add_h2(doc, "2.2. Virtualización Completa (Proxmox VE / KVM) frente a Contenedores (Docker)")
    add_p(doc, "La selección de la capa de virtualización determina la densidad de servicios, el aislamiento y la sobrecarga del laboratorio. Mientras Proxmox VE combina hipervisores Tipo 1 (KVM) con contenedores LXC, Docker provee virtualización a nivel de sistema operativo compartiendo el kernel Linux anfitrión mediante namespaces y cgroups (Merkel, 2014). La Tabla 1 resume la comparación arquitectónica entre ambos paradigmas.")

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
            ["Aplicación en TIF", "Estudio teórico comparativo", "Base de nodos, broker, Spark y k3d"],
        ],
        note_text="Elaboración propia basada en Merkel (2014) y Tanenbaum y van Steen (2023)."
    )

    add_h2(doc, "2.3. Orquestación Ligera con k3s y Procesamiento Distribuido (Hadoop vs. Spark)")
    add_p(doc, "Kubernetes automatiza el despliegue, escalado y autorrecuperación de aplicaciones contenedorizadas mediante controladores de reconciliación continua (Burns et al., 2016). Utilizando k3s a través de k3d se desplegó un clúster de tres nodos (1 control-plane y 2 agentes) dentro de Docker con mínimo consumo de memoria. En la capa analítica se contrastó el modelo clásico MapReduce (Dean & Ghemawat, 2008; Shvachko et al., 2010), penalizado por el I/O entre etapas, frente a Apache Spark (Zaharia et al., 2016), que mantiene DataFrames en memoria RAM distribuida y habilita procesamiento en flujo mediante Structured Streaming. Finalmente, la infraestructura se automatizó declarativamente con Ansible garantizando idempotencia (Red Hat, 2023).")

    # --- 3. MATERIALES Y MÉTODOS ---
    add_h1(doc, "3. Materiales y Métodos: Arquitectura del Laboratorio")
    add_p(doc, "El sistema implementado se compone de: (a) simuladores de sensores en Python con semilla determinista (seed=42), ruido gaussiano y deriva temporal; (b) broker Eclipse Mosquitto 2.0 en puerto TCP 1883; (c) controlador automático en lazo cerrado que mide la latencia fin-a-fin entre detección de anomalías y orden a actuadores; (d) servicio recolector que escribe lotes JSON atómicos en volumen compartido; (e) clúster k3s de tres nodos con escalado horizontal y autoscaling; y (f) generador de datasets sintéticos de 1M (61,49 MB) y 10M (614,93 MB) registros evaluados por Python Baseline, Hadoop Streaming y PySpark.")

    # --- 4. RESULTADOS EXPERIMENTALES ---
    add_h1(doc, "4. Resultados Experimentales")
    add_p(doc, "Todas las mediciones se ejecutaron en una estación Linux x86_64 (CachyOS, 16 GB RAM, SSD NVMe) aislando cada corrida en subprocesos independientes con tres repeticiones por condición experimental.")

    add_h2(doc, "4.1. Experimento E1: Rendimiento según Volumen de Datos")
    add_apa_table(
        doc,
        "Tabla 2",
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
        "Tabla 3",
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
    add_p(doc, "Al desplegar el simulador de sensores sobre el clúster k3s de tres nodos en k3d, el escalado horizontal de 1 a 5 réplicas mediante kubectl scale se completó con los 5 pods en estado Running en aproximadamente 3 segundos. Al inyectar una falla crítica eliminando deliberadamente un pod (kubectl delete pod), el controlador ReplicaSet detectó la discrepancia respecto al estado deseado e instanció un pod sustituto operativo en menos de 2 segundos, verificando transparencia y recuperación automática ante fallos.")

    add_h2(doc, "4.4. Experimento E5: Latencia Real de Control en Lazo Cerrado")
    add_apa_table(
        doc,
        "Tabla 4",
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
    add_h1(doc, "5. Discusión, Conclusiones y Trabajo Futuro")
    add_p(doc, "Los resultados experimentales confirman que la combinación de contenedores Docker y k3d permite modelar clústeres distribuidos multinodo con una sobrecarga mínima frente a la virtualización completa por hipervisores. En el plano analítico, los frameworks distribuidos como Apache Spark presentan un punto de inflexión claro: para lotes reducidos (1M filas) Python monohilo resulta más ágil al evitar la inicialización de la JVM, pero a partir de 10M de registros Spark supera en 3,86× a Python y en 4,30× a Hadoop Streaming gracias a su ejecución paralela en memoria.")
    add_p(doc, "Asimismo, el playbook de Ansible demostró idempotencia estricta (changed=0 en segunda corrida) garantizando la reproducibilidad completa del laboratorio. Como líneas de trabajo futuro se propone integrar Apache Kafka para persistencia distribuida de flujos, Prometheus y Grafana para observabilidad en tiempo real, y almacenamiento distribuido Ceph sobre un clúster físico Proxmox VE.")

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

