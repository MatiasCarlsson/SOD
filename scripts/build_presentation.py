#!/usr/bin/env python3
"""
Generador de la presentación de defensa (TIF SOD 2026) — estilo "Textmode Overlay".

Estética de terminal / TUI: fondo fósforo oscuro con scanlines, tipografía
monoespaciada (Courier New), paneles con etiqueta superpuesta sobre el borde
("┤ ETIQUETA ├"), prompts `$`, barras de progreso ASCII entre secciones,
gráficos nativos de PowerPoint con los valores reales medidos y los 3 videos
MP4 de demostración embebidos. Transición "fade" en todas las diapositivas.

Salida: docs/Presentacion_TIF_SOD_2026.pptx y docs/Presentacion_TIF_SOD_2026.pdf
"""
import os
import subprocess
import tempfile

from lxml import etree
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
VID_DIR = os.path.join(DOCS_DIR, "videos")
os.makedirs(DOCS_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# Paleta "fósforo" (verde hidroponía + ámbar de alerta)
# ------------------------------------------------------------------------------
HEX_BG = "070B08"
C_BG = RGBColor(0x07, 0x0B, 0x08)
C_PANEL = RGBColor(0x0D, 0x15, 0x10)
C_PANEL_2 = RGBColor(0x12, 0x1D, 0x16)
C_GREEN = RGBColor(0x3D, 0xDC, 0x84)     # dominante
C_GREEN_DIM = RGBColor(0x1E, 0x6B, 0x45)
C_AMBER = RGBColor(0xFF, 0xB0, 0x00)     # acento
C_RED = RGBColor(0xFF, 0x5F, 0x56)
C_TEXT = RGBColor(0xDD, 0xF5, 0xE6)
C_MUTED = RGBColor(0x7F, 0xA8, 0x90)
C_FAINT = RGBColor(0x2C, 0x45, 0x36)

MONO = "Courier New"
SLIDE_W, SLIDE_H = 13.333, 7.5
TOTAL = 24


# ------------------------------------------------------------------------------
# Recursos gráficos generados (fondo con scanlines, pósters de video)
# ------------------------------------------------------------------------------
def make_background(path: str) -> str:
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), (7, 11, 8))
    d = ImageDraw.Draw(img)
    # Scanlines horizontales
    for y in range(0, h, 4):
        d.line([(0, y), (w, y)], fill=(10, 16, 12))
    # Grilla de puntos tenue (celdas de modo texto)
    for y in range(18, h, 36):
        for x in range(12, w, 24):
            d.point((x, y), fill=(22, 38, 28))
    # Viñeta suave en bordes
    vign = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vign)
    for i in range(60):
        a = int(110 * (1 - i / 60))
        vd.rectangle([i * 3, i * 2, w - i * 3, h - i * 2], outline=a)
    dark = Image.new("RGB", (w, h), (2, 4, 3))
    img = Image.composite(dark, img, vign.point(lambda v: int(v * 0.55)))
    img.save(path, "PNG")
    return path


def create_video_poster(video_path: str, out_png: str, timestamp_sec: float) -> str:
    """Extrae un fotograma del MP4 con ffmpeg y superpone un botón Play estilo terminal."""
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{timestamp_sec:.2f}", "-i", video_path,
         "-frames:v", "1", "-q:v", "2", out_png],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    with Image.open(out_png).convert("RGBA") as img:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        for y in range(0, img.height, 4):
            d.line([(0, y), (img.width, y)], fill=(0, 0, 0, 38))
        cx, cy, r = img.width // 2, img.height // 2, 70
        d.rectangle((cx - r, cy - r, cx + r, cy + r), fill=(7, 11, 8, 200),
                    outline=(61, 220, 132, 255), width=5)
        d.polygon([(cx - 22, cy - 34), (cx - 22, cy + 34), (cx + 36, cy)], fill=(61, 220, 132, 255))
        Image.alpha_composite(img, overlay).convert("RGB").save(out_png, "PNG")
    return out_png


# ------------------------------------------------------------------------------
# Primitivas de texto y forma
# ------------------------------------------------------------------------------
def txt(slide, x, y, w, h, runs, size=14, color=C_TEXT, bold=False, align=PP_ALIGN.LEFT,
        anchor=MSO_ANCHOR.TOP, fill=None, margin=0.0, spacing_after=0):
    """Caja de texto. `runs` puede ser str, lista de párrafos (str) o lista de listas de (texto, color, bold, size)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(margin))
    if fill is not None:
        tb.fill.solid()
        tb.fill.fore_color.rgb = fill
    paragraphs = [runs] if isinstance(runs, str) else runs
    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(spacing_after)
        segs = [(para, color, bold, size)] if isinstance(para, str) else para
        for seg in segs:
            t, c, b, s = (list(seg) + [color, bold, size][len(seg) - 1:])[:4]
            r = p.add_run()
            r.text = t
            r.font.name = MONO
            r.font.size = Pt(s)
            r.font.bold = b
            r.font.color.rgb = c
    return tb


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1.25):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    return shp


def panel(slide, x, y, w, h, label=None, accent=C_GREEN, fill=C_PANEL):
    """Panel TUI: rectángulo con borde completo y etiqueta superpuesta sobre el borde superior."""
    rect(slide, x, y, w, h, fill=fill, line=accent)
    if label:
        lw = min(w - 0.4, 0.118 * (len(label) + 4) + 0.1)
        lb = txt(slide, x + 0.22, y - 0.16, lw, 0.32, f"┤ {label} ├", size=12, color=accent, bold=True,
                 fill=C_BG, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        lb.text_frame.word_wrap = False


def lines_block(slide, x, y, w, h, items, size=14, prefix="▸ ", prefix_color=C_GREEN, color=C_TEXT, gap=7):
    paras = []
    for it in items:
        if isinstance(it, tuple):  # (prefijo personalizado, texto)
            paras.append([(it[0], prefix_color, True, size), (it[1], color, False, size)])
        else:
            paras.append([(prefix, prefix_color, True, size), (it, color, False, size)])
    return txt(slide, x, y, w, h, paras, size=size, spacing_after=gap)


def chrome(slide, path, speaker, num):
    """Línea de prompt superior + línea de estado inferior (solo texto, sin barras de color)."""
    txt(slide, 0.5, 0.22, 9.0, 0.3,
        [[("matias@hidroponia", C_GREEN, True, 11), (":", C_MUTED, False, 11),
          (f"~/tif-sod/{path}", C_MUTED, False, 11), ("$", C_MUTED, False, 11)]])
    sp_color = C_GREEN if "1" in speaker and "2" not in speaker else C_AMBER
    if "1" in speaker and "2" in speaker:
        sp_color = C_TEXT
    txt(slide, 9.3, 0.22, 3.53, 0.3,
        [[(f"[ {speaker} ]", sp_color, True, 11), (f"  {num:02d}/{TOTAL}", C_MUTED, False, 11)]],
        align=PP_ALIGN.RIGHT)
    txt(slide, 0.5, 7.08, 12.33, 0.26,
        [[("SOD·2026 ", C_GREEN_DIM, True, 9),
          ("── TIF AE4 · Cultivo hidropónico distribuido ── ", C_FAINT, False, 9),
          ("MQTT · Docker · k3s · Hadoop · Spark · Ansible", C_FAINT, False, 9)]])


def title(slide, text, sub=None, y=0.62):
    txt(slide, 0.5, y, 12.33, 0.75,
        [[("> ", C_GREEN, True, 30), (text, C_TEXT, True, 30), (" █", C_AMBER, False, 26)]])
    if sub:
        txt(slide, 0.5, y + 0.72, 12.33, 0.35, [[("# ", C_GREEN_DIM, True, 13), (sub, C_MUTED, False, 13)]])


def big_stat(slide, x, y, w, value, label, color=C_GREEN, size=44):
    txt(slide, x, y, w, 0.85, value, size=size, color=color, bold=True)
    txt(slide, x, y + 0.85, w, 0.55, label, size=12, color=C_MUTED)


def tui_table(slide, x, y, w, h, headers, rows, size=12, col_widths=None, accent=C_GREEN):
    shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(x), Inches(y), Inches(w), Inches(h))
    tbl = shape.table
    # Quitar estilo por defecto con bandas
    tblPr = shape._element.graphic.graphicData.tbl.tblPr
    tblPr.set("firstRow", "0")
    tblPr.set("bandRow", "0")
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Inches(cw)
    for r in range(len(rows) + 1):
        for c in range(len(headers)):
            cell = tbl.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_GREEN_DIM if r == 0 else (C_PANEL if r % 2 else C_PANEL_2)
            cell.margin_left = cell.margin_right = Inches(0.1)
            cell.margin_top = cell.margin_bottom = Inches(0.05)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = headers[c] if r == 0 else rows[r - 1][c]
            run.font.name = MONO
            run.font.size = Pt(size)
            run.font.bold = r == 0 or c == 0
            run.font.color.rgb = (C_TEXT if r == 0 else (accent if c == 0 else C_TEXT))
    return shape


def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# ------------------------------------------------------------------------------
# Gráficos nativos
# ------------------------------------------------------------------------------
def _no_fill_spPr(parent_el, insert_before_tags):
    spPr = etree.SubElement(parent_el, qn("c:spPr"))
    etree.SubElement(spPr, qn("a:noFill"))
    ln = etree.SubElement(spPr, qn("a:ln"))
    etree.SubElement(ln, qn("a:noFill"))
    # Reubicar según el orden del esquema
    for tag in insert_before_tags:
        ref = parent_el.find(qn(tag))
        if ref is not None:
            ref.addprevious(spPr)
            break


def style_chart(chart, legend=True):
    chart.font.name = MONO
    chart.font.size = Pt(11)
    chart.font.color.rgb = C_TEXT
    cs = chart._chartSpace
    _no_fill_spPr(cs, ["c:txPr", "c:externalData", "c:printSettings", "c:userShapes", "c:extLst"])
    plot_area = cs.find(qn("c:chart")).find(qn("c:plotArea"))
    _no_fill_spPr(plot_area, ["c:extLst"])
    chart.has_legend = legend
    if legend:
        chart.legend.position = XL_LEGEND_POSITION.TOP
        chart.legend.include_in_layout = False
        chart.legend.font.color.rgb = C_TEXT
        chart.legend.font.size = Pt(11)
    va = chart.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = C_FAINT
    va.major_gridlines.format.line.width = Pt(0.75)
    va.format.line.fill.background()
    va.tick_labels.font.color.rgb = C_MUTED
    va.tick_labels.font.size = Pt(10)
    ca = chart.category_axis
    ca.format.line.color.rgb = C_GREEN_DIM
    ca.tick_labels.font.color.rgb = C_TEXT
    ca.tick_labels.font.size = Pt(11)
    ca.has_major_gridlines = False


def column_chart(slide, x, y, w, h, categories, series, colors, number_format="0.00"):
    cd = CategoryChartData()
    cd.categories = categories
    for name, values in series:
        cd.add_series(name, values)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    style_chart(ch, legend=len(series) > 1)
    plot = ch.plots[0]
    plot.gap_width = 70
    plot.overlap = -10
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = number_format
    dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(10)
    dl.font.color.rgb = C_TEXT
    for s, col in zip(plot.series, colors):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = col
        s.format.line.fill.background()
    return ch


def line_chart(slide, x, y, w, h, categories, series, colors, dashed=()):
    cd = CategoryChartData()
    cd.categories = categories
    for name, values in series:
        cd.add_series(name, values)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    style_chart(ch, legend=True)
    plot = ch.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = '0.00"×"'
    dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.ABOVE
    dl.font.size = Pt(10)
    dl.font.color.rgb = C_TEXT
    for i, (s, col) in enumerate(zip(plot.series, colors)):
        s.smooth = False
        s.format.line.color.rgb = col
        s.format.line.width = Pt(2.5)
        if i in dashed:
            s.format.line.dash_style = 4  # MSO_LINE_DASH_STYLE.DASH
        s.marker.style = XL_MARKER_STYLE.SQUARE
        s.marker.size = 9
        s.marker.format.fill.solid()
        s.marker.format.fill.fore_color.rgb = col
        s.marker.format.line.color.rgb = col
    return ch


# ------------------------------------------------------------------------------
# Constructor de diapositivas
# ------------------------------------------------------------------------------
class Deck:
    def __init__(self, tmpdir):
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_W)
        self.prs.slide_height = Inches(SLIDE_H)
        self.blank = self.prs.slide_layouts[6]
        self.tmp = tmpdir
        self.bg = make_background(os.path.join(tmpdir, "bg_textmode.png"))
        self.n = 0

    def slide(self, notes):
        s = self.prs.slides.add_slide(self.blank)
        bg = s.background.fill
        bg.solid()
        bg.fore_color.rgb = C_BG
        s.shapes.add_picture(self.bg, 0, 0, self.prs.slide_width, self.prs.slide_height)
        set_notes(s, notes)
        self.n += 1
        return s

    def divider(self, idx, name, cmd, speaker, progress, notes):
        s = self.slide(notes)
        chrome(s, f"0{idx}_{name.lower().replace(' ', '_')}", speaker, self.n)
        txt(s, 0.5, 1.0, 5.0, 2.6, f"0{idx}", size=150, color=C_GREEN_DIM, bold=True)
        txt(s, 0.55, 3.75, 12.2, 0.9,
            [[("// ", C_GREEN, True, 40), (name.upper(), C_TEXT, True, 40), (" █", C_AMBER, False, 34)]])
        txt(s, 0.55, 4.7, 12.2, 0.4, [[("$ ", C_GREEN, True, 16), (cmd, C_MUTED, False, 16)]])
        filled = int(round(progress * 40))
        bar = "█" * filled + "░" * (40 - filled)
        txt(s, 0.55, 5.75, 12.2, 0.4,
            [[("progreso [", C_MUTED, False, 14), (bar, C_GREEN, False, 14),
              (f"] {int(progress * 100):3d}%", C_MUTED, False, 14)]])
        txt(s, 0.55, 6.25, 12.2, 0.35, [[("expone → ", C_MUTED, False, 13),
                                          (speaker, C_AMBER if "2" in speaker else C_GREEN, True, 13)]])
        return s

    def demo(self, num, speaker, title_text, sub, steps, video, ts, caption, notes):
        s = self.slide(notes)
        chrome(s, f"demos/{os.path.splitext(video)[0]}", speaker, num)
        title(s, title_text, sub)
        accent = C_AMBER if "2" in speaker else C_GREEN
        panel(s, 0.5, 1.95, 3.95, 4.85, label="PASOS", accent=accent)
        lines_block(s, 0.72, 2.3, 3.55, 4.4, steps, size=14, prefix="$ ", prefix_color=accent, gap=14)
        # Marco del video: la etiqueta queda en una franja superior, sin tapar la imagen
        panel(s, 4.78, 1.95, 8.05, 4.85, label=f"► {video}", accent=accent, fill=C_BG)
        vw, vh = 7.4, 7.4 * 9 / 16
        vx, vy = 4.78 + (8.05 - vw) / 2, 2.25
        poster = create_video_poster(os.path.join(VID_DIR, video),
                                     os.path.join(self.tmp, f"poster_{num}.png"), ts)
        s.shapes.add_movie(os.path.join(VID_DIR, video), Inches(vx), Inches(vy), Inches(vw), Inches(vh),
                           poster_frame_image=poster, mime_type="video/mp4")
        txt(s, vx, vy + vh + 0.08, vw, 0.3,
            [[("● REC ", C_RED, True, 11), (caption, C_MUTED, False, 11)]])
        return s

    def finish(self):
        # Transición fade en todas las diapositivas (fluidez), insertada antes de <p:timing>
        for s in self.prs.slides:
            el = etree.fromstring(
                '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'spd="med"><p:fade/></p:transition>')
            sld = s._element
            timing = sld.find(qn("p:timing"))
            if timing is not None:
                timing.addprevious(el)
            else:
                anchor = sld.find(qn("p:clrMapOvr"))
                (anchor if anchor is not None else sld.find(qn("p:cSld"))).addnext(el)


# ------------------------------------------------------------------------------
# Contenido
# ------------------------------------------------------------------------------
def build(d: Deck):
    # ---------------------------------------------------------------- 01 PORTADA
    s = d.slide("[Persona 1 | 0:00 - 0:40] Saludo al tribunal, presentación de integrantes y del tema. "
                "Mencionar que todo lo que verán (métricas, videos) proviene de mediciones reales del laboratorio.")
    txt(s, 0.5, 0.22, 12.3, 0.3, [[("matias@hidroponia", C_GREEN, True, 11), (":~/tif-sod$ ./defensa --start", C_MUTED, False, 11)]])
    boot = [
        ("[  OK  ] ", "broker mosquitto escuchando en :1883"),
        ("[  OK  ] ", "clúster k3d listo (1 server + 2 agents)"),
        ("[  OK  ] ", "spark master + workers registrados"),
        ("[  OK  ] ", "ansible-playbook → changed=0"),
    ]
    txt(s, 0.5, 0.75, 8.0, 1.4, [[(a, C_GREEN, True, 12), (b, C_MUTED, False, 12)] for a, b in boot], spacing_after=2)
    txt(s, 0.5, 2.35, 12.3, 2.1,
        [[("Sistema automatizado de cultivo", C_TEXT, True, 40)],
         [("hidropónico ", C_TEXT, True, 40), ("distribuido", C_GREEN, True, 40), (" █", C_AMBER, False, 36)]])
    txt(s, 0.5, 4.45, 12.3, 0.8,
        "IoT (MQTT) · Contenedores (Docker) · Orquestación (k3s/k3d) ·\nProcesamiento paralelo (Hadoop & Spark) · IaC idempotente (Ansible)",
        size=15, color=C_MUTED)
    panel(s, 0.5, 5.6, 12.33, 1.2, label="TIF · AE 4", accent=C_GREEN_DIM)
    txt(s, 0.75, 5.82, 11.9, 0.9,
        [[("Cátedra   ", C_GREEN, True, 14), ("Sistemas Operativos Distribuidos — 2026", C_TEXT, False, 14)],
         [("Exponen   ", C_GREEN, True, 14), ("Persona 1 & Persona 2  ", C_TEXT, False, 14),
          ("·  ~18 min  ·  3 demos en video", C_MUTED, False, 14)]], spacing_after=4)

    # ---------------------------------------------------------------- 02 AGENDA
    s = d.slide("[Persona 1 | 0:40 - 1:10] Recorrer la agenda rápidamente: problema, teoría, arquitectura con demo, "
                "resultados con demos y cierre. Indicar quién expone cada bloque.")
    chrome(s, "", "Persona 1", d.n)
    title(s, "ls -la ./defensa", "Recorrido de la exposición (~18 min)")
    agenda = [
        ("01", "contexto/", "Problema, desafíos y objetivos", "P1", "0:40"),
        ("02", "teoria/", "KVM vs. Docker · k3s · MQTT · Hadoop vs. Spark", "P1→P2", "3:30"),
        ("03", "arquitectura/", "Laboratorio, sensores, controlador + Demo 1", "P1", "7:20"),
        ("04", "resultados/", "E1 · E2 · Demo 2 (k3s) · Demo 3 (Spark/Ansible) · E5", "P2", "11:00"),
        ("05", "cierre/", "Conclusiones, trabajo futuro y preguntas", "P1+P2", "16:50"),
    ]
    y = 2.0
    for num, folder, desc, who, t in agenda:
        col = C_AMBER if who == "P2" else C_GREEN
        txt(s, 0.5, y, 0.9, 0.5, num, size=26, color=C_GREEN_DIM, bold=True)
        txt(s, 1.45, y + 0.04, 3.0, 0.45, folder, size=18, color=col, bold=True)
        txt(s, 4.45, y + 0.08, 6.4, 0.45, desc, size=14, color=C_TEXT)
        txt(s, 10.95, y + 0.08, 1.0, 0.45, who, size=13, color=col, bold=True)
        txt(s, 11.95, y + 0.08, 0.9, 0.45, t, size=13, color=C_MUTED, align=PP_ALIGN.RIGHT)
        y += 0.9
    txt(s, 0.5, 6.55, 12.3, 0.35, "drwxr-xr-x  5 directorios · 24 diapositivas · 3 videos embebidos", size=11, color=C_FAINT)

    # ---------------------------------------------------------------- 03 MOTIVACIÓN
    s = d.slide("[Persona 1 | 1:10 - 2:00] La hidroponía NFT no tiene suelo que amortigüe errores: las raíces dependen "
                "100% de la solución. Una desviación de pH bloquea nutrientes en horas; un tanque bajo quema bombas. "
                "Por eso necesitamos monitoreo continuo y reacción automática.")
    chrome(s, "01_contexto/motivacion.md", "Persona 1", d.n)
    title(s, "Hidroponía: sin margen de error", "Sistema NFT — las raíces dependen 100 % de la solución recirculante")
    stats = [
        ("5,5–6,5", "rango de pH seguro:\nsi no, precipita Fe·Ca·P", C_GREEN),
        ("< 30 %", "nivel de tanque crítico:\ncavitación de bombas", C_AMBER),
        ("18–24 °C", "temperatura ideal\nde la solución", C_GREEN),
        ("1,2–2,5", "conductividad (mS/cm):\nnutrientes disueltos", C_GREEN),
    ]
    x = 0.5
    for v, l, c in stats:
        panel(s, x, 2.05, 2.88, 2.55, accent=c if c == C_AMBER else C_GREEN_DIM)
        txt(s, x + 0.2, 2.35, 2.6, 0.85, v, size=32, color=c, bold=True)
        txt(s, x + 0.2, 3.4, 2.6, 1.1, l, size=13, color=C_MUTED)
        x += 3.15
    panel(s, 0.5, 5.0, 12.33, 1.75, label="CONSECUENCIA", accent=C_AMBER)
    txt(s, 0.75, 5.3, 11.9, 1.3,
        [[("Una desviación no detectada se convierte en pérdida de cultivo en ", C_TEXT, False, 16),
          ("horas", C_AMBER, True, 16), (".", C_TEXT, False, 16)],
         [("→ ", C_GREEN, True, 16), ("Necesitamos medir continuamente y reaccionar ", C_TEXT, False, 16),
          ("sin intervención humana", C_GREEN, True, 16), (".", C_TEXT, False, 16)]], spacing_after=8)

    # ---------------------------------------------------------------- 04 DESAFÍOS SOD
    s = d.slide("[Persona 1 | 2:00 - 2:45] Cada necesidad agronómica se traduce en un problema clásico de sistemas "
                "distribuidos: desacoplamiento, tiempo real, tolerancia a fallos y escalabilidad analítica.")
    chrome(s, "01_contexto/desafios.md", "Persona 1", d.n)
    title(s, "Del cultivo a los Sistemas Distribuidos", "Cada necesidad agronómica se mapea a un pilar de SOD")
    cells = [
        ("DESACOPLAMIENTO", "Sensores y actuadores sin conocerse punto a punto.", "MQTT Pub/Sub"),
        ("TIEMPO REAL", "Reaccionar en milisegundos ante una anomalía.", "Lazo cerrado"),
        ("TOLERANCIA A FALLOS", "Si cae un nodo sensor, se recupera solo.", "k3s self-healing"),
        ("ESCALABILIDAD", "Analizar millones de lecturas históricas.", "Spark vs. Hadoop"),
    ]
    pos = [(0.5, 2.05), (6.75, 2.05), (0.5, 4.5), (6.75, 4.5)]
    for (lab, desc, tech), (px, py) in zip(cells, pos):
        panel(s, px, py, 6.08, 2.15, label=lab)
        txt(s, px + 0.25, py + 0.35, 5.6, 0.9, desc, size=15, color=C_TEXT)
        txt(s, px + 0.25, py + 1.4, 5.6, 0.5, [[("→ ", C_AMBER, True, 17), (tech, C_AMBER, True, 17)]])

    # ---------------------------------------------------------------- 05 OBJETIVOS
    s = d.slide("[Persona 1 | 2:45 - 3:30] Enumerar los 5 objetivos: comparación teórica, laboratorio reproducible, "
                "simulación IoT, orquestación resiliente y campaña experimental E1–E5.")
    chrome(s, "01_contexto/objetivos.md", "Persona 1", d.n)
    title(s, "Objetivos del trabajo", "Teoría → laboratorio → experimentación")
    objs = [
        ("Comparar", "virtualización completa (KVM) vs. contenedores, y MapReduce vs. Spark."),
        ("Desplegar", "un laboratorio reproducible con Docker Compose + Ansible idempotente."),
        ("Simular", "sensores multizona realistas y un controlador en lazo cerrado vía MQTT."),
        ("Orquestar", "un clúster k3s multinodo: escalado horizontal y self-healing."),
        ("Medir", "5 experimentos (E1–E5) con repeticiones: tiempo, speedup y latencia."),
    ]
    y = 2.0
    for i, (verb, rest) in enumerate(objs, 1):
        txt(s, 0.5, y, 0.8, 0.6, f"[{i}]", size=20, color=C_GREEN_DIM, bold=True)
        txt(s, 1.35, y + 0.04, 11.4, 0.6, [[(verb + " ", C_GREEN, True, 18), (rest, C_TEXT, False, 16)]])
        y += 0.9

    # ---------------------------------------------------------------- 06 DIVIDER TEORÍA
    d.divider(2, "Marco teórico", "cat teoria/*.md | less", "Persona 1 → Persona 2", 0.20,
              "[Persona 1 | 3:30 - 3:40] Transición: 'Antes de la implementación, repasemos las bases teóricas.'")

    # ---------------------------------------------------------------- 07 KVM VS DOCKER
    s = d.slide("[Persona 1 | 3:40 - 4:40] Contrastar hipervisor tipo 1 (kernels independientes) vs. contenedores "
                "(kernel compartido, namespaces + cgroups). Justificar Docker para emular nodos. Luego handoff a Persona 2.")
    chrome(s, "02_teoria/virtualizacion.md", "Persona 1", d.n)
    title(s, "KVM (Proxmox) vs. Docker", "Virtualización completa frente a virtualización a nivel de SO")
    tui_table(s, 0.5, 1.95, 12.33, 3.3,
              ["Dimensión", "Proxmox VE / KVM", "Docker / LXC"],
              [["Abstracción", "Hardware emulado (hipervisor tipo 1)", "Kernel del host compartido"],
               ["Aislamiento", "Kernels independientes + VT-x/AMD-V", "Namespaces + cgroups"],
               ["Overhead", "Alto: SO huésped + RAM reservada", "Mínimo: OverlayFS, RAM dinámica"],
               ["Arranque", "30 – 90 s por VM", "0,5 – 2 s por contenedor"],
               ["Densidad 16 GB", "~4 a 8 VMs completas", "Decenas de servicios + k3s"]],
              size=13, col_widths=[2.6, 4.9, 4.83])
    panel(s, 0.5, 5.6, 12.33, 1.2, label="DECISIÓN DE DISEÑO", accent=C_AMBER)
    txt(s, 0.75, 5.85, 11.9, 0.85,
        "Proxmox se analiza en teoría; en el laboratorio Docker emula múltiples nodos, redes aisladas y un clúster k3s sin costo de hardware.",
        size=14, color=C_TEXT)

    # ---------------------------------------------------------------- 08 K3S
    s = d.slide("[Persona 2 | 4:40 - 5:30] Kubernetes es declarativo: describimos el estado deseado y el plano de control "
                "reconcilia continuamente. k3s lo reduce a un binario liviano; k3d lo corre dentro de Docker.")
    chrome(s, "02_teoria/k3s.md", "Persona 2", d.n)
    title(s, "Orquestación con k3s sobre k3d", "Kubernetes liviano: estado deseado + reconciliación continua")
    panel(s, 0.5, 1.95, 6.0, 4.85, label="CONCEPTOS", accent=C_AMBER)
    lines_block(s, 0.75, 2.3, 5.6, 4.4, [
        "Declarativo: Deployments, ReplicaSets, Pods y Services.",
        "Bucle de reconciliación: real → deseado, siempre.",
        "k3s: < 512 MB RAM, SQLite/kine en lugar de etcd.",
        "k3d: clúster multinodo dentro de contenedores Docker.",
    ], size=15, prefix_color=C_AMBER, gap=18)
    panel(s, 6.83, 1.95, 6.0, 4.85, label="TOPOLOGÍA DEL LAB", accent=C_GREEN)
    # Nodo server
    rect(s, 8.03, 2.4, 3.6, 0.95, fill=C_PANEL_2, line=C_GREEN)
    txt(s, 8.03, 2.45, 3.6, 0.45, "server-0", size=15, color=C_GREEN, bold=True, align=PP_ALIGN.CENTER)
    txt(s, 8.03, 2.85, 3.6, 0.4, "control plane", size=12, color=C_MUTED, align=PP_ALIGN.CENTER)
    # Conectores en "árbol"
    rect(s, 9.82, 3.35, 0.02, 0.4, fill=C_GREEN_DIM)
    rect(s, 8.33, 3.75, 3.0, 0.02, fill=C_GREEN_DIM)
    rect(s, 8.33, 3.75, 0.02, 0.4, fill=C_GREEN_DIM)
    rect(s, 11.31, 3.75, 0.02, 0.4, fill=C_GREEN_DIM)
    for ax_, name in ((7.13, "agent-0"), (10.13, "agent-1")):
        rect(s, ax_, 4.15, 2.4, 1.2, fill=C_PANEL_2, line=C_AMBER)
        txt(s, ax_, 4.22, 2.4, 0.42, name, size=15, color=C_AMBER, bold=True, align=PP_ALIGN.CENTER)
        txt(s, ax_, 4.66, 2.4, 0.5, "pods ▪ ▪ ▪", size=13, color=C_MUTED, align=PP_ALIGN.CENTER)
    txt(s, 7.13, 5.75, 5.5, 0.9, [[("sensor-simulator", C_GREEN, True, 13), (" → MQTT vía", C_MUTED, False, 13)],
                                  [("host.k3d.internal:1883", C_MUTED, False, 13)]])

    # ---------------------------------------------------------------- 09 MQTT
    s = d.slide("[Persona 2 | 5:30 - 6:15] MQTT desacopla en espacio, tiempo y sincronización. Cabecera mínima, "
                "ideal para telemetría a 1 Hz. QoS 1 garantiza que las alertas críticas lleguen al menos una vez.")
    chrome(s, "02_teoria/mqtt.md", "Persona 2", d.n)
    title(s, "Mensajería MQTT (Mosquitto)", "Publicación / suscripción mediada por un broker")
    flow_y = 2.2
    boxes = [(0.5, "SENSORES", "publish"), (4.9, "MOSQUITTO", ":1883"), (9.3, "SUSCRIPTORES", "subscribe")]
    for bx, lab, sub in boxes:
        panel(s, bx, flow_y, 3.53, 1.5, accent=C_AMBER if lab == "MOSQUITTO" else C_GREEN)
        txt(s, bx, flow_y + 0.3, 3.53, 0.5, lab, size=20, bold=True, align=PP_ALIGN.CENTER,
            color=C_AMBER if lab == "MOSQUITTO" else C_GREEN)
        txt(s, bx, flow_y + 0.85, 3.53, 0.4, sub, size=13, color=C_MUTED, align=PP_ALIGN.CENTER)
    for ax in (4.03, 8.43):
        txt(s, ax, flow_y + 0.5, 0.87, 0.5, "──►", size=20, color=C_GREEN, align=PP_ALIGN.CENTER)
    txt(s, 0.5, 3.95, 12.33, 0.4, [[("topic: ", C_MUTED, False, 13), ("hidroponia/+/telemetria", C_GREEN, True, 13),
                                     ("   →   controlador · recolector", C_MUTED, False, 13)]], align=PP_ALIGN.CENTER)
    props = [("ESPACIO", "Nadie conoce las IPs de los demás."), ("TIEMPO", "Emisor y receptor no necesitan coincidir."),
             ("LIVIANO", "Cabecera mínima: ideal a 1 Hz."), ("QoS 1", "PUBACK: ninguna alerta se pierde.")]
    x = 0.5
    for lab, desc in props:
        panel(s, x, 4.85, 2.88, 1.95, label=lab, accent=C_GREEN_DIM)
        txt(s, x + 0.2, 5.2, 2.55, 1.5, desc, size=15, color=C_TEXT)
        x += 3.15

    # ---------------------------------------------------------------- 10 HADOOP VS SPARK
    s = d.slide("[Persona 2 | 6:15 - 7:20] MapReduce persiste en disco entre fases (I/O bound); Spark mantiene los datos "
                "en memoria y optimiza con Catalyst. Los tres motores ejecutan la MISMA agregación para que la comparación "
                "sea justa. Devolver la palabra a Persona 1.")
    chrome(s, "02_teoria/bigdata.md", "Persona 2", d.n)
    title(s, "Hadoop MapReduce vs. Apache Spark", "Disco entre fases frente a procesamiento en memoria")
    panel(s, 0.5, 1.95, 6.0, 3.3, label="HADOOP STREAMING", accent=C_GREEN_DIM)
    txt(s, 0.75, 2.3, 5.6, 0.5, [[("Map ", C_TEXT, True, 15), ("─► ", C_MUTED, False, 15), ("[disco]", C_RED, True, 15),
                                  (" ─► Shuffle ─► ", C_MUTED, False, 15), ("Reduce", C_TEXT, True, 15)]])
    lines_block(s, 0.75, 3.0, 5.6, 2.2, [
        "Resultados intermedios en disco.",
        "Penalidad de I/O en cada etapa.",
        "mapper.py + reducer.py en Python.",
    ], size=14, prefix_color=C_MUTED)
    panel(s, 6.83, 1.95, 6.0, 3.3, label="APACHE SPARK", accent=C_GREEN)
    txt(s, 7.08, 2.3, 5.6, 0.5, [[("DAG ", C_TEXT, True, 15), ("─► ", C_MUTED, False, 15), ("[RAM]", C_GREEN, True, 15),
                                  (" ─► Catalyst ─► ", C_MUTED, False, 15), ("Acción", C_TEXT, True, 15)]])
    lines_block(s, 7.08, 3.0, 5.6, 2.2, [
        "DataFrames distribuidos en memoria.",
        "Optimizador Catalyst + plan DAG.",
        "Batch y Structured Streaming.",
    ], size=14)
    panel(s, 0.5, 5.6, 12.33, 1.2, label="COMPARACIÓN JUSTA", accent=C_AMBER)
    txt(s, 0.75, 5.85, 11.9, 0.85,
        "Python secuencial, Hadoop Streaming y Spark ejecutan la misma agregación: promedios por zona + conteo de alertas.",
        size=14, color=C_TEXT)

    # ---------------------------------------------------------------- 11 DIVIDER ARQUITECTURA
    d.divider(3, "Arquitectura", "docker compose up -d && make k3s-deploy", "Persona 1", 0.40,
              "[Persona 1 | 7:20 - 7:30] Transición: 'Con la teoría clara, veamos cómo lo construimos.'")

    # ---------------------------------------------------------------- 12 ARQUITECTURA
    s = d.slide("[Persona 1 | 7:30 - 8:40] Recorrer el flujo de izquierda a derecha: sensores (Docker/k3s) → Mosquitto → "
                "bifurcación: controlador (reacción inmediata) y recolector (lotes JSON) → procesamiento Spark/Hadoop. "
                "Ansible verifica todo el entorno de forma idempotente.")
    chrome(s, "03_arquitectura/diagrama.txt", "Persona 1", d.n)
    title(s, "Arquitectura del laboratorio", "Flujo de datos: generación → mensajería → control / ingesta → análisis")
    # Fila de flujo
    panel(s, 0.5, 2.1, 2.75, 2.2, label="1 · SENSORES")
    txt(s, 0.7, 2.45, 2.4, 1.8, ["Docker / k3s", "1 → 20 pods", "pH · CE · T · H2O"], size=12, color=C_TEXT, spacing_after=4)
    txt(s, 3.25, 2.95, 0.7, 0.45, "─►", size=18, color=C_GREEN, align=PP_ALIGN.CENTER)
    panel(s, 3.95, 2.1, 2.75, 2.2, label="2 · BROKER", accent=C_AMBER)
    txt(s, 4.15, 2.45, 2.4, 1.8, ["Mosquitto 2.0", "TCP 1883", "QoS 1"], size=12, color=C_TEXT, spacing_after=4)
    txt(s, 6.7, 2.45, 0.7, 0.45, "─►", size=18, color=C_GREEN, align=PP_ALIGN.CENTER)
    txt(s, 6.7, 3.5, 0.7, 0.45, "─►", size=18, color=C_GREEN, align=PP_ALIGN.CENTER)
    panel(s, 7.4, 1.95, 5.43, 1.05, label="3A · CONTROLADOR")
    txt(s, 7.6, 2.2, 5.1, 0.7, "Reglas pH / H2O / T → actuadores · latencia → CSV", size=12, color=C_TEXT)
    panel(s, 7.4, 3.3, 5.43, 1.05, label="3B · RECOLECTOR")
    txt(s, 7.6, 3.55, 5.1, 0.7, "Buffer RAM → lotes JSON atómicos en data/raw/", size=12, color=C_TEXT)
    # Fila inferior
    txt(s, 9.6, 4.4, 1.0, 0.4, "│▼", size=16, color=C_GREEN, align=PP_ALIGN.CENTER)
    panel(s, 0.5, 4.95, 6.0, 1.85, label="4 · PROCESAMIENTO DISTRIBUIDO")
    lines_block(s, 0.75, 5.25, 5.6, 1.5, ["Spark: batch + structured streaming", "Hadoop Streaming + baseline Python",
                                          "Datasets 1M / 10M (seed = 42)"], size=12, gap=4)
    panel(s, 6.83, 4.95, 6.0, 1.85, label="5 · IaC ANSIBLE", accent=C_AMBER)
    lines_block(s, 7.08, 5.25, 5.6, 1.5, ["playbook.yml declarativo", "Verifica Docker, k3d, kubectl, datos",
                                          "2.ª ejecución → changed=0"], size=12, prefix_color=C_AMBER, gap=4)

    # ---------------------------------------------------------------- 13 SENSORES + CONTROLADOR
    s = d.slide("[Persona 1 | 8:40 - 9:40] Sensores con ruido gaussiano, deriva temporal y ~8% de anomalías inyectadas "
                "para estresar al controlador. Explicar la tabla de reglas y cómo se mide la latencia fin a fin.")
    chrome(s, "03_arquitectura/controlador.py", "Persona 1", d.n)
    title(s, "Simulación y control reactivo", "Sensores realistas + reglas agronómicas en lazo cerrado")
    panel(s, 0.5, 1.95, 4.6, 4.85, label="SENSOR SIMULADO")
    lines_block(s, 0.72, 2.3, 4.2, 4.4, [
        "5 variables: pH, CE, T, humedad, nivel H2O.",
        "Ruido gaussiano (σ pH = 0,03).",
        "Deriva sinusoidal + evaporación.",
        "~8 % de anomalías inyectadas.",
        "Semilla fija → reproducible.",
    ], size=13, gap=9)
    tui_table(s, 5.45, 1.95, 7.38, 3.0,
              ["Condición", "Actuador", "Orden"],
              [["pH > 6,5", "dosificador_acido", "DOSIFICAR_ACIDO"],
               ["pH < 5,5", "dosificador_base", "DOSIFICAR_BASE"],
               ["H2O < 30 %", "bomba_agua", "REPONER_AGUA"],
               ["T > 24 °C", "enfriador", "ACTIVAR_ENFRIADOR"],
               ["T < 18 °C", "calefactor", "ACTIVAR_CALEFACTOR"]],
              size=12, col_widths=[1.8, 2.6, 2.98])
    panel(s, 5.45, 5.35, 7.38, 1.45, label="LATENCIA FIN A FIN", accent=C_AMBER)
    txt(s, 5.7, 5.65, 6.9, 1.0,
        [[("Δt = ", C_AMBER, True, 15), ("t_comando − t_emisión_sensor", C_TEXT, False, 15)],
         [("→ data/metrics/controller_latencies.csv", C_MUTED, False, 12)]], spacing_after=4)

    # ---------------------------------------------------------------- 14 DEMO 1
    d.demo(d.n + 1, "Persona 1", "Demo 1 · Lazo cerrado IoT", "Stack Docker completo: broker, sensor, controlador y recolector",
           ["docker compose up -d", "docker compose ps → 4 servicios Up", "logs sensor + controller → conectados a MQTT",
            "ls data/raw/ → lotes JSON atómicos"],
           "01_demo_iot_lazo_cerrado.mp4", 10.5, "grabación real del stack · ~16 s · clic para reproducir",
           "[Persona 1 | 9:40 - 11:00] Reproducir el video (clic sobre él) o ejecutar el Bloque 1 de "
           "./scripts/demo_en_vivo.sh. En vivo, señalar en los logs del controlador la orden DOSIFICAR_ACIDO "
           "cuando llega un pH > 6,5. Luego handoff a Persona 2.")

    # ---------------------------------------------------------------- 15 DIVIDER RESULTADOS
    d.divider(4, "Resultados", "make benchmark && make analyze", "Persona 2", 0.60,
              "[Persona 2 | 11:00 - 11:10] Transición: 'Todo lo que sigue son mediciones reales con 3 repeticiones.'")

    # ---------------------------------------------------------------- 16 E1
    s = d.slide("[Persona 2 | 11:10 - 12:20] Con 1M filas gana Python: Spark paga el arranque de la JVM y la planificación. "
                "Con 10M el overhead se amortiza: Spark tarda 8,86 s, 3,86× más rápido que Python y 4,30× que Hadoop.")
    chrome(s, "04_resultados/e1_volumen.csv", "Persona 2", d.n)
    title(s, "E1 · Rendimiento según volumen", "Tiempo de cómputo medio (s), 3 repeticiones — menor es mejor")
    panel(s, 0.5, 1.95, 8.2, 4.85, label="TIEMPO (s)", accent=C_GREEN_DIM, fill=C_BG)
    column_chart(s, 0.65, 2.15, 7.9, 4.55, ["Python", "Hadoop", "Spark"],
                 [("1M filas", (3.28, 4.21, 5.37)), ("10M filas", (34.20, 38.09, 8.86))],
                 [C_GREEN_DIM, C_GREEN])
    big_stat(s, 9.05, 1.95, 3.8, "3,86×", "Spark vs. Python en 10M filas", C_GREEN, 48)
    big_stat(s, 9.05, 3.45, 3.8, "4,30×", "Spark vs. Hadoop en 10M filas", C_GREEN, 48)
    panel(s, 9.05, 5.15, 3.78, 1.65, label="PUNTO DE INFLEXIÓN", accent=C_AMBER)
    txt(s, 9.25, 5.45, 3.45, 1.3, ["En 1M gana Python: Spark paga JVM y planificación.",
                                   "En 10M el overhead se amortiza."], size=12, color=C_TEXT, spacing_after=6)

    # ---------------------------------------------------------------- 17 E2
    s = d.slide("[Persona 2 | 12:20 - 13:20] Sobre 10M filas: 1 worker 14,78 s, 2 workers 11,09 s (1,33×), 3 workers 9,18 s "
                "(1,61×). La eficiencia cae de 100% a 53,6%: la fracción secuencial (lectura CSV, collect, shuffle) "
                "limita la aceleración, como predice la Ley de Amdahl.")
    chrome(s, "04_resultados/e2_speedup.csv", "Persona 2", d.n)
    title(s, "E2 · Escalabilidad de Spark", "Speedup real vs. ideal sobre 10M filas — Ley de Amdahl")
    panel(s, 0.5, 1.95, 6.6, 4.85, label="SPEEDUP", accent=C_GREEN_DIM, fill=C_BG)
    line_chart(s, 0.65, 2.15, 6.3, 4.55, ["1 worker", "2 workers", "3 workers"],
               [("Real", (1.00, 1.33, 1.61)), ("Ideal", (1.0, 2.0, 3.0))], [C_GREEN, C_MUTED], dashed=(1,))
    tui_table(s, 7.45, 1.95, 5.38, 2.0,
              ["Workers", "Cómputo", "Speedup", "Efic."],
              [["1", "14,78 ± 0,26 s", "1,00×", "100 %"],
               ["2", "11,09 ± 0,05 s", "1,33×", "66,6 %"],
               ["3", "9,18 ± 0,13 s", "1,61×", "53,6 %"]],
              size=12, col_widths=[1.05, 2.03, 1.15, 1.15])
    panel(s, 7.45, 4.35, 5.38, 2.45, label="LEY DE AMDAHL", accent=C_AMBER)
    txt(s, 7.7, 4.65, 4.95, 0.5, [[("S(p) = 1 / ((1−f) + f/p)", C_AMBER, True, 14)]])
    txt(s, 7.7, 5.2, 4.95, 1.5,
        "La parte secuencial (lectura CSV, collect del driver, shuffle) acota la aceleración.",
        size=12, color=C_TEXT)

    # ---------------------------------------------------------------- 18 DEMO 2
    d.demo(d.n + 1, "Persona 2", "Demo 2 · k3s: escalado y self-healing", "Experimentos E3 (escalado) y E4 (tolerancia a fallos)",
           ["k3d cluster: 1 server + 2 agents", "kubectl scale --replicas=5  (~3 s)",
            "kubectl delete pod → ReplicaSet lo recrea en < 2 s", "kubectl get pods -o wide"],
           "02_demo_k3s_escalado_tolerancia.mp4", 18.0, "grabación real en k3d/k3s · ~23 s · clic para reproducir",
           "[Persona 2 | 13:20 - 14:30] Reproducir el video o ejecutar el Bloque 3 de ./scripts/demo_en_vivo.sh. "
           "Remarcar que nadie recrea el pod a mano: lo hace el bucle de reconciliación.")

    # ---------------------------------------------------------------- 19 DEMO 3
    d.demo(d.n + 1, "Persona 2", "Demo 3 · Spark e idempotencia", "Job batch sobre 1M de lecturas + segunda corrida de Ansible",
           ["spark batch_analysis.py (1M) → 5,39 s", "run_hadoop_job.py (1M) → 4,09 s",
            "ansible-playbook playbook.yml", "PLAY RECAP → changed=0"],
           "03_demo_spark_hadoop_ansible.mp4", 5.5, "grabación real Spark + Ansible · ~20 s · clic para reproducir",
           "[Persona 2 | 14:30 - 15:30] Reproducir el video o ejecutar los Bloques 2 y 4 de ./scripts/demo_en_vivo.sh. "
           "Mostrar changed=0 como prueba de idempotencia.")

    # ---------------------------------------------------------------- 20 E5
    s = d.slide("[Persona 2 | 15:30 - 16:20] Latencias reales sobre Mosquitto + controlador en Docker. Con 1 sensor 0,11 ms; "
                "con 50 sensores en ráfaga la media es 7,56 ms y el P95 19,56 ms: apto para tiempo real blando.")
    chrome(s, "04_resultados/e5_latencia.csv", "Persona 2", d.n)
    title(s, "E5 · Latencia del lazo cerrado", "Mosquitto + controlador reales — media y P95 en milisegundos")
    panel(s, 0.5, 1.95, 7.6, 4.85, label="LATENCIA (ms)", accent=C_GREEN_DIM, fill=C_BG)
    column_chart(s, 0.65, 2.15, 7.3, 4.55, ["1 sensor", "10 sensores", "50 sensores"],
                 [("Media", (0.11, 2.22, 7.56)), ("P95", (0.49, 4.56, 19.56))],
                 [C_GREEN, C_AMBER])
    big_stat(s, 8.45, 1.95, 4.4, "19,56 ms", "P95 con 50 sensores concurrentes", C_AMBER, 44)
    tui_table(s, 8.45, 3.6, 4.38, 1.6,
              ["Sensores", "μ ± σ (ms)", "P95"],
              [["1", "0,11 ± 0,22", "0,49"], ["10", "2,22 ± 1,46", "4,56"], ["50", "7,56 ± 7,03", "19,56"]],
              size=11, col_widths=[1.2, 2.0, 1.18])
    panel(s, 8.45, 5.55, 4.38, 1.25, label="VEREDICTO", accent=C_GREEN)
    txt(s, 8.65, 5.82, 4.0, 0.9, "95 % de reacciones en < 20 ms → tiempo real blando.", size=12, color=C_TEXT)

    # ---------------------------------------------------------------- 21 RESUMEN
    s = d.slide("[Persona 2 | 16:20 - 16:50] Resumen de un vistazo: cada número responde a un pilar de SOD. "
                "Luego dar paso a las conclusiones compartidas.")
    chrome(s, "04_resultados/resumen.log", "Persona 2", d.n)
    title(s, "tail -f resultados.log", "Cinco experimentos, cinco respuestas")
    tiles = [
        ("E1", "3,86×", "Spark vs. Python\n(10M filas)", C_GREEN),
        ("E2", "1,61×", "speedup con 3 workers\n(eficiencia 53,6 %)", C_GREEN),
        ("E3", "~3 s", "escalar a 5 réplicas\nen k3s", C_AMBER),
        ("E4", "< 2 s", "recrear un pod\neliminado", C_AMBER),
        ("E5", "19,56 ms", "P95 con 50 sensores\nconcurrentes", C_GREEN),
        ("IaC", "changed=0", "segunda corrida\nde Ansible", C_AMBER),
    ]
    for i, (tag, val, lab, col) in enumerate(tiles):
        px = 0.5 + (i % 3) * 4.18
        py = 1.95 + (i // 3) * 2.5
        panel(s, px, py, 3.98, 2.25, label=tag, accent=col)
        txt(s, px + 0.25, py + 0.3, 3.5, 0.8, val, size=34, color=col, bold=True)
        txt(s, px + 0.25, py + 1.2, 3.5, 0.9, lab, size=12, color=C_MUTED)

    # ---------------------------------------------------------------- 22 CONCLUSIONES
    d.divider(5, "Cierre", "git log --oneline | head -1", "Persona 1 + Persona 2", 0.90,
              "[Persona 1 | 16:50 - 16:55] Transición breve hacia las conclusiones.")
    s = d.slide("[Persona 1 y Persona 2 | 16:55 - 17:50] Conclusiones repartidas ~30 s cada uno: Persona 1 la "
                "infraestructura e IoT; Persona 2 el procesamiento y la resiliencia.")
    chrome(s, "05_cierre/conclusiones.md", "Persona 1 + 2", d.n)
    title(s, "Conclusiones", "Lo que demostró el laboratorio")
    panel(s, 0.5, 1.95, 6.0, 3.55, label="INFRA + IoT · P1", accent=C_GREEN)
    lines_block(s, 0.75, 2.3, 5.6, 3.1, [
        "Docker + k3d modelan clústeres multinodo con sobrecarga mínima frente a VMs.",
        "MQTT desacopla productores y consumidores con latencias de milisegundos.",
        "Separar control reactivo e ingesta batch da estabilidad ante picos.",
    ], size=14, gap=12)
    panel(s, 6.83, 1.95, 6.0, 3.55, label="DATOS + RESILIENCIA · P2", accent=C_AMBER)
    lines_block(s, 7.08, 2.3, 5.6, 3.1, [
        "Spark supera 3,86× a Python y 4,30× a Hadoop en 10M filas.",
        "La escalabilidad sigue la Ley de Amdahl (shuffle + driver).",
        "k3s se autorrecupera en < 2 s; Ansible garantiza despliegues idempotentes.",
    ], size=14, prefix_color=C_AMBER, gap=12)
    panel(s, 0.5, 5.85, 12.33, 0.95, accent=C_GREEN_DIM)
    txt(s, 0.75, 5.85, 11.9, 0.95,
        [[("$ echo $TESIS  ", C_GREEN, True, 14),
          ("un diseño distribuido convierte un cultivo frágil en un sistema autónomo, medible y resiliente.", C_TEXT, False, 14)]],
        anchor=MSO_ANCHOR.MIDDLE)

    # ---------------------------------------------------------------- 23 FUTURO + GRACIAS
    s = d.slide("[Persona 1 | 17:50 - 18:30] Mencionar las líneas de trabajo futuro, agradecer y abrir la ronda de preguntas.")
    chrome(s, "05_cierre/roadmap.md", "Persona 1", d.n)
    title(s, "Trabajo futuro", "Próximos pasos naturales del laboratorio")
    fut = [("KAFKA", "Event sourcing y retención distribuida de flujos."),
           ("PROMETHEUS + GRAFANA", "Observabilidad de pods, workers y métricas de pH."),
           ("CEPH / PROXMOX", "Almacenamiento distribuido en clúster físico.")]
    x = 0.5
    for lab, desc in fut:
        panel(s, x, 1.95, 3.98, 1.75, label=lab, accent=C_GREEN_DIM)
        txt(s, x + 0.25, 2.3, 3.5, 1.3, desc, size=14, color=C_TEXT)
        x += 4.18
    txt(s, 0.5, 4.35, 12.33, 1.1,
        [[("¡Gracias! ", C_GREEN, True, 48), ("¿Preguntas?", C_TEXT, True, 48), (" █", C_AMBER, False, 42)]],
        align=PP_ALIGN.CENTER)
    txt(s, 0.5, 5.65, 12.33, 0.4, [[("$ git clone ", C_MUTED, False, 14),
                                     ("https://github.com/MatiasCarlsson/SOD.git", C_GREEN, True, 14)]],
        align=PP_ALIGN.CENTER)
    txt(s, 0.5, 6.15, 12.33, 0.4, "informe APA 7 · código · datasets reproducibles · videos de demo",
        size=12, color=C_MUTED, align=PP_ALIGN.CENTER)


def build_deck():
    with tempfile.TemporaryDirectory() as tmp:
        deck = Deck(tmp)
        build(deck)
        assert deck.n == TOTAL, f"Se generaron {deck.n} diapositivas, se esperaban {TOTAL}"
        deck.finish()
        pptx_path = os.path.join(DOCS_DIR, "Presentacion_TIF_SOD_2026.pptx")
        deck.prs.save(pptx_path)
        print(f"PPTX generado: {pptx_path}")
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", DOCS_DIR, pptx_path], check=True)
    print(f"PDF generado: {os.path.join(DOCS_DIR, 'Presentacion_TIF_SOD_2026.pdf')}")


if __name__ == "__main__":
    build_deck()
