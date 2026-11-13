#!/usr/bin/env python3
"""
Generador de Presentación Académica Fluida (15–20 min) en formato PPTX y PDF.
Incluye 15 diapositivas diseñadas para Persona 1 y Persona 2, con diagramas,
tablas comparativas, gráficos experimentales reales y notas de orador.
"""
import os
import subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
FIG_DIR = os.path.join(ROOT_DIR, "analysis", "figures")
os.makedirs(DOCS_DIR, exist_ok=True)

# Paleta de diseño de ingeniería (Alta legibilidad en proyector y PDF)
C_NAVY = RGBColor(15, 23, 42)        # #0F172A
C_SLATE = RGBColor(30, 41, 59)       # #1E293B
C_TEAL = RGBColor(13, 148, 136)      # #0D9488
C_CYAN = RGBColor(6, 182, 212)       # #06B6D4
C_AMBER = RGBColor(217, 119, 6)      # #D97706
C_BG_LIGHT = RGBColor(248, 250, 252) # #F8FAFC
C_CARD = RGBColor(255, 255, 255)     # #FFFFFF
C_BORDER = RGBColor(203, 213, 225)   # #CBD5E1
C_TEXT = RGBColor(30, 41, 59)        # #1E293B
C_MUTED = RGBColor(100, 116, 139)    # #64748B
C_WHITE = RGBColor(255, 255, 255)
C_SOFT_TEAL = RGBColor(240, 253, 250)
C_SOFT_AMBER = RGBColor(255, 251, 235)

FONT_FAMILY = "DejaVu Sans"


def set_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header(slide, title: str, speaker: str, slide_num: int, total_slides: int = 15):
    set_bg(slide, C_BG_LIGHT)
    # Barra superior
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.95))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_NAVY
    bar.line.fill.background()

    # Franja inferior acento teal
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.95), Inches(13.333), Inches(0.06))
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_TEAL
    accent.line.fill.background()

    # Título
    tb = slide.shapes.add_textbox(Inches(0.55), Inches(0.18), Inches(9.5), Inches(0.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = FONT_FAMILY
    p.font.size = Pt(23)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    # Badge de Orador
    badge_color = C_TEAL if "1" in speaker else C_AMBER
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.3), Inches(0.24), Inches(2.0), Inches(0.45))
    badge.fill.solid()
    badge.fill.fore_color.rgb = badge_color
    badge.line.fill.background()
    btf = badge.text_frame
    btf.vertical_anchor = MSO_ANCHOR.MIDDLE
    bp = btf.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    bp.text = speaker
    bp.font.name = FONT_FAMILY
    bp.font.size = Pt(12)
    bp.font.bold = True
    bp.font.color.rgb = C_WHITE

    # Número de slide
    nb = slide.shapes.add_textbox(Inches(12.35), Inches(0.26), Inches(0.75), Inches(0.4))
    np_p = nb.text_frame.paragraphs[0]
    np_p.alignment = PP_ALIGN.RIGHT
    np_p.text = f"{slide_num}/{total_slides}"
    np_p.font.name = FONT_FAMILY
    np_p.font.size = Pt(12)
    np_p.font.color.rgb = RGBColor(148, 163, 184)

    # Footer
    fb = slide.shapes.add_textbox(Inches(0.55), Inches(7.12), Inches(12.2), Inches(0.3))
    fp = fb.text_frame.paragraphs[0]
    fp.text = "Sistemas Operativos Distribuidos (2026) — TIF AE 4: Cultivo Hidropónico Automatizado Distribuido"
    fp.font.name = FONT_FAMILY
    fp.font.size = Pt(10)
    fp.font.color.rgb = C_MUTED


def add_card(slide, left, top, width, height, title=None, bullets=None, bg=C_CARD, border=C_BORDER, title_color=C_NAVY, font_size=14):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.adjustments[0] = 0.03
    card.fill.solid()
    card.fill.fore_color.rgb = bg
    card.line.color.rgb = border
    card.line.width = Pt(1.2)

    if title or bullets:
        tb = slide.shapes.add_textbox(Inches(left + 0.22), Inches(top + 0.16), Inches(width - 0.44), Inches(height - 0.32))
        tf = tb.text_frame
        tf.word_wrap = True
        first = True
        if title:
            p = tf.paragraphs[0]
            first = False
            p.text = title
            p.font.name = FONT_FAMILY
            p.font.size = Pt(font_size + 2)
            p.font.bold = True
            p.font.color.rgb = title_color
            p.space_after = Pt(8)
        if bullets:
            for item in bullets:
                p = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                p.text = f"• {item}" if not item.startswith("→") and not item.startswith("•") else item
                p.font.name = FONT_FAMILY
                p.font.size = Pt(font_size)
                p.font.color.rgb = C_TEXT
                p.space_after = Pt(6)
    return card


def add_styled_table(slide, left, top, width, height, headers, rows, font_size=12):
    shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(left), Inches(top), Inches(width), Inches(height))
    table = shape.table
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_FAMILY
        p.font.size = Pt(font_size)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    for r_idx, row in enumerate(rows):
        row_bg = C_CARD if r_idx % 2 == 0 else RGBColor(241, 245, 249)
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = row_bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.font.name = FONT_FAMILY
            p.font.size = Pt(font_size - 1)
            p.font.color.rgb = C_TEXT
            if c_idx == 0:
                p.font.bold = True
    return shape


def set_notes(slide, text):
    notes = slide.notes_slide
    notes.notes_text_frame.text = text


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # --------------------------------------------------------------------------
    # SLIDE 1: PORTADA
    # --------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank)
    set_bg(s1, C_NAVY)
    stripe = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.28), Inches(7.5))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = C_TEAL
    stripe.line.fill.background()

    tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.4), Inches(11.3), Inches(1.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "FACULTAD DE INGENIERÍA, TECNOLOGÍA Y ARQUITECTURA — INGENIERÍA EN SISTEMAS"
    p0.font.name = FONT_FAMILY
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.space_after = Pt(18)

    p1 = tf.add_paragraph()
    p1.text = "Modelado y Análisis de un Sistema Automatizado\nde Cultivo Hidropónico Distribuido"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.space_after = Pt(18)

    p2 = tf.add_paragraph()
    p2.text = "Integración de IoT (MQTT), Contenedores (Docker), Orquestación (k3s/k3d),\nProcesamiento Paralelo (Hadoop & Spark) y Automatización Idempotente (Ansible)"
    p2.font.name = FONT_FAMILY
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(203, 213, 225)

    info_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.1), Inches(11.3), Inches(1.45))
    info_box.fill.solid()
    info_box.fill.fore_color.rgb = C_SLATE
    info_box.line.color.rgb = C_TEAL
    itf = info_box.text_frame
    itf.margin_left = Inches(0.35)
    itf.margin_top = Inches(0.25)
    ip1 = itf.paragraphs[0]
    ip1.text = "Cátedra: Sistemas Operativos Distribuidos (Trabajo Integrador Final — AE 4)"
    ip1.font.name = FONT_FAMILY
    ip1.font.size = Pt(16)
    ip1.font.bold = True
    ip1.font.color.rgb = C_WHITE
    ip1.space_after = Pt(8)
    ip2 = itf.add_paragraph()
    ip2.text = "Expositores: Persona 1 & Persona 2   |   Duración estimada: 17–18 minutos (con 2 Demos en Vivo)"
    ip2.font.name = FONT_FAMILY
    ip2.font.size = Pt(14)
    ip2.font.color.rgb = C_CYAN
    set_notes(s1, "[Persona 1 | 0:00 - 0:45] Saludo al tribunal, presentación de integrantes y estructura de la defensa.")

    # --------------------------------------------------------------------------
    # SLIDE 2: EL PROBLEMA Y CASO DE ESTUDIO
    # --------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank)
    add_header(s2, "1. Motivación y Caso de Estudio: Hidroponía Automatizada", "Persona 1", 2)
    add_card(
        s2, 0.55, 1.35, 5.9, 5.45,
        title="¿Por qué la Hidroponía es Crítica en Tiempo Real?",
        bullets=[
            "Sin suelo amortiguador: raíces suspendidas en solución nutritiva recirculante (sistema NFT).",
            "pH fuera de rango (5,5 – 6,5): precipita macro y micronutrientes (Fe, Ca, P) en pocas horas.",
            "Nivel de tanque < 30 %: riesgo de cavitación de bombas y marchitamiento rápido.",
            "Conductividad Eléctrica (1,2 – 2,5 mS/cm) y Temperatura (18 – 24 °C) requieren monitoreo continuo.",
        ],
        bg=C_SOFT_TEAL, border=C_TEAL, font_size=15
    )
    add_card(
        s2, 6.85, 1.35, 5.9, 5.45,
        title="Desafíos de Sistemas Operativos Distribuidos",
        bullets=[
            "Desacoplamiento: sensores y actuadores distribuidos sin conocer IPs punto-a-punto (MQTT Pub/Sub).",
            "Control en Lazo Cerrado: latencia de reacción en milisegundos ante anomalías.",
            "Tolerancia a Fallos: ante caída de un nodo sensor, autorrecuperación transparente (k3s).",
            "Escalabilidad Analítica: procesar millones de lecturas históricas para detectar derivas (Spark vs. Hadoop).",
        ],
        font_size=15
    )
    set_notes(s2, "[Persona 1 | 0:45 - 2:00] Explicar criticidad agronómica del cultivo hidropónico y su mapeo directo a los pilares de SOD.")

    # --------------------------------------------------------------------------
    # SLIDE 3: OBJETIVOS DEL TRABAJO
    # --------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank)
    add_header(s3, "2. Objetivos del Trabajo Integrador", "Persona 1", 3)
    objs = [
        ("1. Comparación Teórica", "Contrastar virtualización completa (Proxmox/KVM) frente a contenedores (Docker/LXC) y MapReduce frente a Spark."),
        ("2. Laboratorio Reproducible", "Desplegar entorno distribuido con Docker Compose y automatización idempotente mediante Ansible."),
        ("3. Simulación IoT Realista", "Modelar sensores multizona (ruido gaussiano + deriva) y controlador automático en lazo cerrado vía MQTT."),
        ("4. Orquestación Resiliente", "Operar un clúster k3s multinodo (k3d) para validar escalado horizontal y tolerancia a fallos (self-healing)."),
        ("5. Campaña Experimental", "Ejecutar 5 experimentos (E1–E5) con repeticiones estadísticas para medir tiempos, Speedup, RAM y latencia."),
    ]
    y_pos = 1.3
    for title_o, desc_o in objs:
        add_card(s3, 0.7, y_pos, 11.9, 1.02, title=title_o, bullets=[desc_o], font_size=13)
        y_pos += 1.14
    set_notes(s3, "[Persona 1 | 2:00 - 3:00] Enumerar los 5 objetivos que articulan la parte teórica, práctica y experimental.")

    # --------------------------------------------------------------------------
    # SLIDE 4: MARCO TEÓRICO I - VIRTUALIZACIÓN
    # --------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank)
    add_header(s4, "3. Marco Teórico I: Proxmox (KVM) vs. Docker (Contenedores)", "Persona 1", 4)
    add_styled_table(
        s4, 0.55, 1.35, 12.2, 4.1,
        headers=["Dimensión", "Virtualización Completa (Proxmox VE / KVM)", "Virtualización de SO (Docker / LXC)"],
        rows=[
            ["Capa de Abstracción", "Hardware emulado mediante Hipervisor Tipo 1", "Kernel Linux compartido del sistema anfitrión"],
            ["Aislamiento", "Kernels independientes + Intel VT-x / AMD-V", "Namespaces (PID, NET, MNT) + cgroups (CPU/RAM)"],
            ["Overhead y RAM", "Alto: duplica SO huésped y reserva RAM estática", "Mínimo: memoria dinámica y capas OverlayFS"],
            ["Tiempo de Arranque", "30 a 90 segundos por máquina virtual", "0,5 a 2 segundos por contenedor"],
            ["Densidad en 16 GB RAM", "Limitada (~4 a 8 VMs completas)", "Decenas de microservicios + clúster k3s de 3 nodos"],
        ],
        font_size=13
    )
    add_card(
        s4, 0.55, 5.65, 12.2, 1.2,
        title="Justificación de Diseño",
        bullets=["Proxmox se analizó teóricamente; en el laboratorio Docker permite emular múltiples nodos, redes aisladas y orquestación k3s sin sobrecarga de hardware."],
        bg=C_SOFT_TEAL, border=C_TEAL, font_size=13
    )
    set_notes(s4, "[Persona 1 | 3:00 - 4:30] Contrastar KVM vs Docker y hacer handoff fluido hacia Persona 2.")

    # --------------------------------------------------------------------------
    # SLIDE 5: MARCO TEÓRICO II - K3S Y MQTT
    # --------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank)
    add_header(s5, "4. Marco Teórico II: Orquestación (k3s) y Mensajería MQTT", "Persona 2", 5)
    add_card(
        s5, 0.55, 1.35, 5.9, 5.4,
        title="Kubernetes Ligero: k3s sobre k3d",
        bullets=[
            "Orquestación declarativa: Pods, Deployments, ReplicaSets y Services.",
            "Reconciliación continua: garantiza que el estado real coincida con el deseado.",
            "k3s reduce el footprint a < 512 MB RAM (reemplaza etcd por SQLite/kine).",
            "k3d ejecuta un clúster multinodo (1 Server + 2 Agents) íntegramente dentro de Docker.",
        ],
        font_size=14
    )
    add_card(
        s5, 6.85, 1.35, 5.9, 5.4,
        title="Protocolo MQTT (Eclipse Mosquitto)",
        bullets=[
            "Patrón Publicación/Suscripción mediado por un Broker central (puerto 1883).",
            "Desacoplamiento espacial, temporal y de sincronización entre nodos IoT.",
            "Cabeceras mínimas frente a HTTP (ideal para telemetría continua a 1 Hz).",
            "QoS 1 (al menos una vez): confirmación PUBACK para no perder alertas críticas.",
        ],
        bg=C_SOFT_AMBER, border=C_AMBER, font_size=14
    )
    set_notes(s5, "[Persona 2 | 4:30 - 6:00] Explicar k3s/k3d y por qué MQTT supera a HTTP en telemetría IoT.")

    # --------------------------------------------------------------------------
    # SLIDE 6: MARCO TEÓRICO III - HADOOP VS SPARK
    # --------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank)
    add_header(s6, "5. Marco Teórico III: Hadoop MapReduce vs. Apache Spark", "Persona 2", 6)
    add_card(
        s6, 0.55, 1.35, 5.9, 4.2,
        title="Apache Hadoop (MapReduce)",
        bullets=[
            "Modelo clásico en fases: Map → Shuffle/Sort → Reduce.",
            "Persiste resultados intermedios en disco entre etapas (penalidad I/O).",
            "Implementado con Hadoop Streaming (mapper.py y reducer.py en Python).",
        ],
        font_size=14
    )
    add_card(
        s6, 6.85, 1.35, 5.9, 4.2,
        title="Apache Spark (In-Memory)",
        bullets=[
            "Procesamiento distribuido en memoria RAM (RDDs / DataFrames).",
            "Optimizador Catalyst y ejecución vectorizada por DAGs.",
            "Soporta Batch y Structured Streaming sobre la carpeta de ingesta.",
        ],
        bg=C_SOFT_TEAL, border=C_TEAL, font_size=14
    )
    add_card(
        s6, 0.55, 5.75, 12.2, 1.05,
        title="Equivalencia Analítica de Comparación",
        bullets=["Los tres motores (Python Baseline, Hadoop Streaming y Spark) ejecutan exactamente la misma agregación: promedios por zona y conteo de alertas."],
        font_size=13
    )
    set_notes(s6, "[Persona 2 | 6:00 - 7:30] Explicar I/O bound de MapReduce vs memoria de Spark y devolver la palabra a Persona 1.")

    # --------------------------------------------------------------------------
    # SLIDE 7: ARQUITECTURA GENERAL DEL SISTEMA
    # --------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank)
    add_header(s7, "6. Arquitectura Distribuida del Laboratorio", "Persona 1", 7)

    # Bloques visuales de arquitectura
    add_card(s7, 0.55, 1.45, 3.1, 2.5, title="1. Capa Generación", bullets=["Sensores en Docker / k3s", "1 Server + 2 Agents", "Escalable 1 → 20 pods"], bg=C_SOFT_TEAL, border=C_TEAL, font_size=12)
    add_card(s7, 4.25, 1.45, 3.1, 2.5, title="2. Broker MQTT", bullets=["Eclipse Mosquitto 2.0", "Puerto TCP 1883", "Tópico: hidroponia/+/telemetria"], bg=C_SOFT_AMBER, border=C_AMBER, font_size=12)
    add_card(s7, 8.0, 1.3, 4.75, 1.35, title="3A. Controlador Lazo Cerrado", bullets=["Evalúa pH / H2O y ordena a actuadores", "Registra latencia en CSV (E5)"], font_size=12)
    add_card(s7, 8.0, 2.85, 4.75, 1.35, title="3B. Servicio Recolector", bullets=["Buffer en RAM → volcado atómico JSON", "Alimentación a /data/raw/"], font_size=12)

    add_card(s7, 0.55, 4.45, 5.9, 2.3, title="4. Procesamiento Distribuido (Big Data)", bullets=[
        "Apache Spark (Batch DataFrames & Structured Streaming).",
        "Hadoop Streaming MapReduce + Línea Base Python.",
        "Datasets deterministas de 1M y 10M de lecturas (semilla=42).",
    ], font_size=13)
    add_card(s7, 6.85, 4.45, 5.9, 2.3, title="5. Infraestructura como Código (Ansible)", bullets=[
        "Playbook declarativo e idempotente (ansible/playbook.yml).",
        "Verifica Docker, k3d, kubectl y estructura de datos.",
        "Segunda ejecución garantiza changed=0.",
    ], font_size=13)
    set_notes(s7, "[Persona 1 | 7:30 - 8:45] Recorrer el flujo de izquierda a derecha: sensores -> Mosquitto -> bifurcación Controlador + Recolector -> Spark/Hadoop + Ansible.")

    # --------------------------------------------------------------------------
    # SLIDE 8: IMPLEMENTACIÓN IOT Y LAZO CERRADO
    # --------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank)
    add_header(s8, "7. Simulación Hidropónica y Control Reactivo", "Persona 1", 8)
    add_card(
        s8, 0.55, 1.35, 5.9, 5.4,
        title="Modelado Realista de Sensores (Python)",
        bullets=[
            "Variables: pH, Conductividad Eléctrica, Temperatura, Humedad y Nivel de Agua.",
            "Ruido gaussiano (σ = 0,03 en pH) + deriva sinusoidal temporal + evaporación.",
            "Semilla aleatoria fija para reproducibilidad científica.",
            "Inyección controlada de anomalías (~8 %) para estresar al controlador.",
        ],
        font_size=14
    )
    add_styled_table(
        s8, 6.85, 1.35, 5.9, 3.6,
        headers=["Condición Detectada", "Tópico / Actuador", "Orden Emitida"],
        rows=[
            ["pH > 6,5", "dosificador_acido", "DOSIFICAR_ACIDO"],
            ["pH < 5,5", "dosificador_base", "DOSIFICAR_BASE"],
            ["Nivel H2O < 30 %", "bomba_agua", "REPONER_AGUA"],
            ["Temp > 24 °C", "chiller_enfriador", "ACTIVAR_ENFRIADOR"],
            ["Temp < 18 °C", "calefactor_agua", "ACTIVAR_CALEFACTOR"],
        ],
        font_size=12
    )
    add_card(
        s8, 6.85, 5.15, 5.9, 1.6,
        title="Cálculo de Latencia Fin-a-Fin",
        bullets=["Δt = t_comando_actuador − t_emision_sensor (registrado en controller_latencies.csv)."],
        bg=C_SOFT_TEAL, border=C_TEAL, font_size=13
    )
    set_notes(s8, "[Persona 1 | 8:45 - 9:45] Detallar variables agronómicas y las reglas exactas del controlador.")

    # --------------------------------------------------------------------------
    # SLIDE 9: DEMO EN VIVO 1
    # --------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank)
    set_bg(s9, C_NAVY)
    add_card(s9, 1.0, 1.0, 11.33, 5.5, title="DEMOSTRACIÓN EN VIVO 1 — Stack IoT y Control en Lazo Cerrado", bullets=[
        "→ Paso 1: Levantar el laboratorio base con `docker compose up -d` (Mosquitto, Sensor, Recolector, Controlador).",
        "→ Paso 2: Verificar estado saludable de contenedores con `docker compose ps`.",
        "→ Paso 3: Observar telemetría en vivo y al controlador disparando `DOSIFICAR_ACIDO` en < 1 ms ante pH > 6,5.",
        "→ Paso 4: Verificar los lotes JSON escritos atómicamente por el recolector en `data/raw/`.",
        "→ Respaldo en video: `docs/videos/01_demo_iot_lazo_cerrado.mp4`",
    ], bg=C_SLATE, border=C_TEAL, title_color=C_CYAN, font_size=16)
    # Recolorear texto de bullets a blanco en fondo oscuro
    for p in s9.shapes[0].text_frame.paragraphs if False else []:
        pass
    # Fix text color inside dark demo card
    for shp in s9.shapes:
        if shp.has_text_frame:
            for idx, p in enumerate(shp.text_frame.paragraphs):
                if idx > 0:
                    p.font.color.rgb = C_WHITE
    badge_d1 = s9.shapes.add_textbox(Inches(1.0), Inches(0.35), Inches(11.33), Inches(0.5))
    bp1 = badge_d1.text_frame.paragraphs[0]
    bp1.text = "PERSONA 1  |  MINUTO 9:45 – 11:30  |  EJECUCIÓN EN TERMINAL"
    bp1.font.name = FONT_FAMILY
    bp1.font.size = Pt(14)
    bp1.font.bold = True
    bp1.font.color.rgb = C_TEAL
    set_notes(s9, "[Persona 1 | 9:45 - 11:30] Ejecutar Bloque 1 de ./scripts/demo_en_vivo.sh. Luego pasar palabra a Persona 2.")

    # --------------------------------------------------------------------------
    # SLIDE 10: RESULTADOS E1 (VOLUMEN DE DATOS)
    # --------------------------------------------------------------------------
    s10 = prs.slides.add_slide(blank)
    add_header(s10, "8. Experimento E1: Rendimiento por Volumen (1M vs. 10M)", "Persona 2", 10)
    fig1 = os.path.join(FIG_DIR, "figura_1_comparacion_volumen.png")
    if os.path.exists(fig1):
        s10.shapes.add_picture(fig1, Inches(0.45), Inches(1.25), width=Inches(7.3))
    add_styled_table(
        s10, 7.9, 1.3, 5.0, 2.7,
        headers=["Motor", "1M Filas (μ ± σ)", "10M Filas (μ ± σ)"],
        rows=[
            ["Python Baseline", "3,28 ± 0,04 s", "34,20 ± 0,39 s"],
            ["Hadoop Streaming", "4,21 ± 0,08 s", "38,09 ± 3,18 s"],
            ["Apache Spark", "5,37 ± 0,12 s", "8,86 ± 0,67 s"],
        ],
        font_size=12
    )
    add_card(
        s10, 7.9, 4.2, 5.0, 2.6,
        title="Análisis del Punto de Inflexión",
        bullets=[
            "En 1M, Python gana porque Spark paga overhead de planificación y JVM.",
            "En 10M, Spark (8,86 s) es 3,86× más rápido que Python y 4,30× más rápido que Hadoop.",
        ],
        bg=C_SOFT_TEAL, border=C_TEAL, font_size=13
    )
    set_notes(s10, "[Persona 2 | 11:30 - 12:45] Explicar Figura 1 con los valores exactos de 3 repeticiones.")

    # --------------------------------------------------------------------------
    # SLIDE 11: RESULTADOS E2 (SPARK SPEEDUP)
    # --------------------------------------------------------------------------
    s11 = prs.slides.add_slide(blank)
    add_header(s11, "9. Experimento E2: Escalabilidad de Spark y Ley de Amdahl", "Persona 2", 11)
    fig2 = os.path.join(FIG_DIR, "figura_2_speedup_spark.png")
    if os.path.exists(fig2):
        s11.shapes.add_picture(fig2, Inches(0.45), Inches(1.25), width=Inches(7.3))
    add_styled_table(
        s11, 7.9, 1.3, 5.0, 2.6,
        headers=["Workers (p)", "Cómputo (μ ± σ)", "Speedup", "Eficiencia"],
        rows=[
            ["1 Worker", "14,78 ± 0,26 s", "1,00×", "100,0 %"],
            ["2 Workers", "11,09 ± 0,05 s", "1,33×", "66,6 %"],
            ["3 Workers", "9,18 ± 0,13 s", "1,61×", "53,6 %"],
        ],
        font_size=12
    )
    add_card(
        s11, 7.9, 4.15, 5.0, 2.65,
        title="Ley de Amdahl en la Práctica",
        bullets=[
            "Aceleración acotada por fracción secuencial (lectura CSV + driver collect + shuffle).",
            "Consistente en 10M filas: eficiencia baja del 100 % al 53,6 % al triplicar workers.",
        ],
        bg=C_SOFT_AMBER, border=C_AMBER, font_size=13
    )
    set_notes(s11, "[Persona 2 | 12:45 - 13:45] Analizar Speedup real vs ideal sobre 10M filas.")

    # --------------------------------------------------------------------------
    # SLIDE 12: DEMO EN VIVO 2 + E3 & E4
    # --------------------------------------------------------------------------
    s12 = prs.slides.add_slide(blank)
    set_bg(s12, C_NAVY)
    add_card(s12, 0.8, 0.95, 11.73, 5.8, title="DEMOSTRACIÓN EN VIVO 2 — Spark, Orquestación k3s (E3/E4) y Ansible", bullets=[
        "→ Paso 1 (Big Data): Ejecutar job PySpark Batch sobre 1M de registros.",
        "→ Paso 2 (k3s E3): Clúster k3d de 3 nodos (`1 server + 2 agents`) → `kubectl scale --replicas=5` (~3 s).",
        "→ Paso 3 (Fallas E4): Eliminar un pod (`kubectl delete pod`) → ReplicaSet regenera el pod en < 2 s (Self-Healing).",
        "→ Paso 4 (IaC): Re-ejecutar `ansible-playbook` demostrando idempotencia estricta (`changed=0`).",
        "→ Respaldos MP4: `docs/videos/02_demo_k3s_escalado_tolerancia.mp4` y `03_demo_spark_hadoop_ansible.mp4`",
    ], bg=C_SLATE, border=C_AMBER, title_color=C_AMBER, font_size=15)
    for shp in s12.shapes:
        if shp.has_text_frame:
            for idx, p in enumerate(shp.text_frame.paragraphs):
                if idx > 0:
                    p.font.color.rgb = C_WHITE
    badge_d2 = s12.shapes.add_textbox(Inches(0.8), Inches(0.32), Inches(11.73), Inches(0.5))
    bp2 = badge_d2.text_frame.paragraphs[0]
    bp2.text = "PERSONA 2  |  MINUTO 13:45 – 15:45  |  EJECUCIÓN EN TERMINAL"
    bp2.font.name = FONT_FAMILY
    bp2.font.size = Pt(14)
    bp2.font.bold = True
    bp2.font.color.rgb = C_AMBER
    set_notes(s12, "[Persona 2 | 13:45 - 15:45] Ejecutar Bloques 2, 3 y 4 de ./scripts/demo_en_vivo.sh.")

    # --------------------------------------------------------------------------
    # SLIDE 13: RESULTADOS E5 (LATENCIA LAZO CERRADO)
    # --------------------------------------------------------------------------
    s13 = prs.slides.add_slide(blank)
    add_header(s13, "10. Experimento E5: Latencia Real de Control en Lazo Cerrado", "Persona 2", 13)
    fig3 = os.path.join(FIG_DIR, "figura_3_latencia_controlador.png")
    if os.path.exists(fig3):
        s13.shapes.add_picture(fig3, Inches(0.45), Inches(1.25), width=Inches(7.3))
    add_styled_table(
        s13, 7.9, 1.3, 5.0, 2.7,
        headers=["Sensores", "Media (μ ± σ)", "P50", "P95"],
        rows=[
            ["1 (n=15)", "0,11 ± 0,22 ms", "0,07 ms", "0,49 ms"],
            ["10 (n=150)", "2,22 ± 1,46 ms", "2,28 ms", "4,56 ms"],
            ["50 (n=750)", "7,56 ± 7,03 ms", "5,16 ms", "19,56 ms"],
        ],
        font_size=12
    )
    add_card(
        s13, 7.9, 4.2, 5.0, 2.6,
        title="Apto para Tiempo Real Blando",
        bullets=[
            "Medición real sobre Mosquitto + contenedor controlador en Docker.",
            "Incluso con 50 sensores en ráfaga concurrente, el 95 % de las reacciones ocurren en < 20 ms.",
        ],
        bg=C_SOFT_TEAL, border=C_TEAL, font_size=13
    )
    set_notes(s13, "[Persona 2 | 15:45 - 16:45] Explicar Figura 3 con las mediciones reales sobre Mosquitto.")

    # --------------------------------------------------------------------------
    # SLIDE 14: CONCLUSIONES
    # --------------------------------------------------------------------------
    s14 = prs.slides.add_slide(blank)
    add_header(s14, "11. Conclusiones y Lecciones Aprendidas", "Persona 1 & 2", 14)
    add_card(
        s14, 0.55, 1.35, 5.9, 5.4,
        title="Infraestructura y Capa IoT (Persona 1)",
        bullets=[
            "Contenedores Docker y k3d permiten modelar clústeres multinodo con sobrecarga mínima frente a VMs completas.",
            "MQTT desacopla productores de consumidores manteniendo latencias de milisegundos en lazo cerrado.",
            "La separación entre control reactivo e ingesta batch garantiza estabilidad ante picos de carga.",
        ],
        bg=C_SOFT_TEAL, border=C_TEAL, font_size=14
    )
    add_card(
        s14, 6.85, 1.35, 5.9, 5.4,
        title="Procesamiento y Resiliencia (Persona 2)",
        bullets=[
            "Spark supera en 3,86× a Python y 4,30× a Hadoop en 10M de registros gracias al procesamiento en memoria.",
            "La escalabilidad paralela sigue la Ley de Amdahl debido al shuffle y coordinación secuencial.",
            "k3s garantiza autorrecuperación en < 2 s y Ansible asegura despliegue reproducible e idempotente (changed=0).",
        ],
        bg=C_SOFT_AMBER, border=C_AMBER, font_size=14
    )
    set_notes(s14, "[Persona 1 y Persona 2 | 16:45 - 17:45] Conclusiones repartidas 30s cada uno.")

    # --------------------------------------------------------------------------
    # SLIDE 15: TRABAJO FUTURO Y CIERRE
    # --------------------------------------------------------------------------
    s15 = prs.slides.add_slide(blank)
    add_header(s15, "12. Líneas de Trabajo Futuro y Preguntas", "Persona 1", 15)
    add_card(s15, 0.55, 1.35, 5.9, 2.5, title="Apache Kafka", bullets=["Reemplazar o complementar Mosquitto para event sourcing y retención distribuida de flujos."], font_size=14)
    add_card(s15, 6.85, 1.35, 5.9, 2.5, title="Prometheus & Grafana", bullets=["Observabilidad en tiempo real de CPU/RAM de pods k3s, workers Spark y métricas de pH."], font_size=14)
    add_card(s15, 0.55, 4.1, 5.9, 2.5, title="Ceph sobre Proxmox VE", bullets=["Evaluar almacenamiento distribuido de objetos en un clúster físico multi-host."], font_size=14)
    add_card(s15, 6.85, 4.1, 5.9, 2.5, title="¡Muchas Gracias!", bullets=["Repositorio listo, informe en formato APA 7 y demostraciones reproducibles.", "Quedamos a disposición del tribunal."], bg=C_SOFT_TEAL, border=C_TEAL, font_size=14)
    set_notes(s15, "[Persona 1 | 17:45 - 18:30] Cierre de la exposición y ronda de preguntas.")

    pptx_path = os.path.join(DOCS_DIR, "Presentacion_TIF_SOD_2026.pptx")
    prs.save(pptx_path)
    print(f"PPTX generado: {pptx_path}")

    # Convertir PPTX a PDF con LibreOffice
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", DOCS_DIR, pptx_path],
        check=True,
    )
    print(f"PDF de presentación generado en: {os.path.join(DOCS_DIR, 'Presentacion_TIF_SOD_2026.pdf')}")


if __name__ == "__main__":
    build_deck()

