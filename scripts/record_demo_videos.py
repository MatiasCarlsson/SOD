#!/usr/bin/env python3
"""
Generador de Videos MP4 de Respaldo a partir de Ejecuciones Reales del Laboratorio.
Ejecuta los comandos reales de la demostración en el sistema, captura su salida
exacta línea por línea y renderiza videos HD (1920x1080) estilo terminal con ffmpeg.
"""
import os
import subprocess
import sys
import textwrap
import time
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VIDEOS_DIR = os.path.join(ROOT_DIR, "docs", "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

FONT_REGULAR = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
if not os.path.exists(FONT_REGULAR):
    FONT_REGULAR = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
    FONT_BOLD = FONT_REGULAR


def run_step(cmd: str, timeout: int = 120) -> list[tuple[str, str]]:
    """Ejecuta un comando real y devuelve líneas coloreadas según origen."""
    lines = [("prompt", f"matias@sod-lab:~/AE4$ {cmd}")]
    proc = subprocess.run(
        cmd,
        shell=True,
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )
    for raw in proc.stdout.splitlines():
        if "ACCION REPORTE" in raw or "changed=0" in raw or "Running" in raw or "Ready" in raw:
            style = "highlight"
        elif "ERROR" in raw or "deleted" in raw:
            style = "warn"
        elif "INFO" in raw or "✔" in raw:
            style = "info"
        else:
            style = "normal"
        lines.append((style, raw))
    lines.append(("normal", ""))
    return lines


def render_terminal_video(title: str, styled_lines: list[tuple[str, str]], output_mp4: str, fps: int = 15):
    """Renderiza una secuencia de líneas de terminal en un video MP4 1080p vía ffmpeg."""
    W, H = 1920, 1080
    font = ImageFont.truetype(FONT_REGULAR, 22)
    font_bold = ImageFont.truetype(FONT_BOLD, 24)
    line_height = 30
    margin_x = 55
    top_bar_h = 60
    content_top = 80
    max_visible_lines = (H - content_top - 40) // line_height
    max_chars = 135

    # Expandir líneas largas con wrap
    wrapped = []
    for style, text in styled_lines:
        if not text:
            wrapped.append((style, ""))
        else:
            for part in textwrap.wrap(text, width=max_chars, replace_whitespace=False) or [""]:
                wrapped.append((style, part))

    colors = {
        "prompt": (80, 250, 123),      # Verde brillante
        "highlight": (255, 184, 108),  # Naranja dorado
        "warn": (255, 85, 85),         # Rojo suave
        "info": (139, 233, 253),       # Cian
        "normal": (248, 248, 242),     # Blanco terminal
    }

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "22",
        "-preset", "fast",
        output_mp4,
    ]
    ff = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def draw_frame(visible_slice):
        img = Image.new("RGB", (W, H), (22, 24, 33))  # Fondo Dracula/Dark
        draw = ImageDraw.Draw(img)
        # Barra superior de ventana
        draw.rectangle([0, 0, W, top_bar_h], fill=(38, 42, 56))
        # Botones de ventana
        draw.ellipse([24, 20, 42, 38], fill=(255, 95, 86))
        draw.ellipse([54, 20, 72, 38], fill=(255, 189, 46))
        draw.ellipse([84, 20, 102, 38], fill=(39, 201, 63))
        draw.text((130, 17), title, font=font_bold, fill=(220, 224, 235))

        y = content_top
        for st, txt in visible_slice:
            draw.text((margin_x, y), txt, font=font, fill=colors.get(st, colors["normal"]))
            y += line_height
        return img.tobytes()

    buffer_lines = []
    for idx, item in enumerate(wrapped):
        buffer_lines.append(item)
        visible = buffer_lines[-max_visible_lines:]
        frame_bytes = draw_frame(visible)
        # Pausa más larga en comandos (prompts) y resultados destacados
        repeat = 8 if item[0] == "prompt" else (4 if item[0] == "highlight" else 2)
        for _ in range(repeat):
            ff.stdin.write(frame_bytes)

    # Mantener frame final 3 segundos para lectura cómoda
    if wrapped:
        last_bytes = draw_frame(buffer_lines[-max_visible_lines:])
        for _ in range(fps * 3):
            ff.stdin.write(last_bytes)

    ff.stdin.close()
    ff.wait()
    print(f"Video generado: {output_mp4}")


def record_demo_1():
    print(">>> Grabando Demo 1: IoT + Mosquitto + Lazo Cerrado...")
    lines = []
    lines += run_step("docker compose up -d mosquitto collector controller sensor-simulator && sleep 8")
    lines += run_step("docker compose ps")
    lines += run_step("docker compose logs sensor-simulator --tail=8")
    lines += run_step("docker compose logs controller --tail=8")
    lines += run_step("ls -lh data/raw/ | tail -n 6")
    lines += run_step("docker compose down")
    render_terminal_video(
        "Demo 1 — Stack IoT (Mosquitto + Sensor + Recolector + Controlador Lazo Cerrado)",
        lines,
        os.path.join(VIDEOS_DIR, "01_demo_iot_lazo_cerrado.mp4"),
    )


def record_demo_2():
    print(">>> Grabando Demo 2: k3s (k3d) Escalado y Self-Healing...")
    lines = []
    lines += run_step("make k3s-up", timeout=180)
    lines += run_step("kubectl get nodes -o wide")
    lines += run_step("make k3s-deploy && sleep 5", timeout=120)
    lines += run_step("kubectl get pods -l app=sensor-simulator -o wide")
    lines += run_step("kubectl scale deployment sensor-simulator --replicas=5 && sleep 4")
    lines += run_step("kubectl get pods -l app=sensor-simulator -o wide")
    lines += run_step("POD=$(kubectl get pods -l app=sensor-simulator -o jsonpath='{.items[0].metadata.name}') && kubectl delete pod $POD --now && sleep 3")
    lines += run_step("kubectl get pods -l app=sensor-simulator -o wide")
    lines += run_step("make k3s-down", timeout=60)
    render_terminal_video(
        "Demo 2 — Orquestación k3s (k3d): Clúster 3 Nodos, Escalado y Autorrecuperación",
        lines,
        os.path.join(VIDEOS_DIR, "02_demo_k3s_escalado_tolerancia.mp4"),
    )


def record_demo_3():
    print(">>> Grabando Demo 3: Spark vs Hadoop + Ansible Idempotencia...")
    lines = []
    lines += run_step(".venv/bin/python src/processing/spark/batch_analysis.py --input data/datasets/synthetic_1M.csv --master 'local[2]'")
    lines += run_step(".venv/bin/python src/processing/hadoop/run_hadoop_job.py --input data/datasets/synthetic_1M.csv")
    lines += run_step("ansible-playbook -i ansible/inventory.ini ansible/playbook.yml")
    render_terminal_video(
        "Demo 3 — Apache Spark vs Hadoop Streaming + Idempotencia en Ansible",
        lines,
        os.path.join(VIDEOS_DIR, "03_demo_spark_hadoop_ansible.mp4"),
    )


if __name__ == "__main__":
    record_demo_1()
    record_demo_2()
    record_demo_3()

