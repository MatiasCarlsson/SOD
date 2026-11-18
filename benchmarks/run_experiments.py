#!/usr/bin/env python3
"""
Orquestador automatizado de la Campaña de Experimentos (E1, E2 y E5)
para el Trabajo Integrador Final de Sistemas Operativos Distribuidos.
Ejecuta 3 repeticiones por condición en procesos aislados, calcula media y desvío estándar,
y persiste los resultados reales en CSV para análisis y gráficos en Jupyter.
"""
import argparse
import csv
import json
import logging
import os
import subprocess
import sys
import threading
import time
import numpy as np
import paho.mqtt.client as mqtt

# Asegurar que la raíz del proyecto esté en el PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("BenchmarkRunner")

METRICS_DIR = os.path.join(ROOT_DIR, "data", "metrics")
DATASETS_DIR = os.path.join(ROOT_DIR, "data", "datasets")


def save_metrics_to_csv(filepath: str, rows: list, fieldnames: list, overwrite: bool = True):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    mode = "w" if overwrite or not os.path.exists(filepath) else "a"
    with open(filepath, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if mode == "w":
            writer.writeheader()
        writer.writerows(rows)
    logger.info("Guardadas %d filas de métricas en %s", len(rows), filepath)


def run_isolated_json(script_rel_path: str, extra_args: list) -> dict:
    """Ejecuta un script de procesamiento en un subproceso aislado y devuelve su JSON."""
    script_abs = os.path.join(ROOT_DIR, script_rel_path)
    cmd = [sys.executable, script_abs, "--json"] + extra_args
    proc = subprocess.run(cmd, cwd=ROOT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Fallo en {script_rel_path}: {proc.stderr}")
    # Buscar última línea JSON válida (por si Spark emite warnings en stdout/stderr)
    for line in reversed(proc.stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise ValueError(f"No se encontró salida JSON válida en {script_rel_path}: {proc.stdout}")


# Experimento 1: Volumen de datos (Python vs Hadoop vs Spark)
def run_experiment_1(datasets: list, repetitions: int = 3):
    logger.info("=== INICIANDO EXPERIMENTO E1: Volumen de Datos (Python vs Hadoop vs Spark) ===")
    results_file = os.path.join(METRICS_DIR, "experiment_1_volume.csv")
    fieldnames = [
        "experiment", "dataset", "total_records", "engine", "iteration",
        "execution_time_sec", "peak_ram_mb", "status"
    ]
    records = []

    for ds_path in datasets:
        if not os.path.exists(ds_path):
            logger.warning("Dataset %s no encontrado. Omitiendo...", ds_path)
            continue

        ds_name = os.path.basename(ds_path)

        # 1. Python Baseline
        logger.info("--- Probando Python Baseline en %s (%d repeticiones) ---", ds_name, repetitions)
        for i in range(1, repetitions + 1):
            res = run_isolated_json("src/processing/baseline_python/process_baseline.py", ["--input", ds_path])
            records.append({
                "experiment": "E1",
                "dataset": ds_name,
                "total_records": res["total_records"],
                "engine": "Python_Baseline",
                "iteration": i,
                "execution_time_sec": res["execution_time_sec"],
                "peak_ram_mb": res["peak_ram_mb"],
                "status": "SUCCESS",
            })
            logger.info("Python Run %d: %.3f s (RAM: %.2f MB)", i, res["execution_time_sec"], res["peak_ram_mb"])

        # 2. Hadoop Streaming
        logger.info("--- Probando Hadoop Streaming MapReduce en %s (%d repeticiones) ---", ds_name, repetitions)
        for i in range(1, repetitions + 1):
            res = run_isolated_json("src/processing/hadoop/run_hadoop_job.py", ["--input", ds_path])
            records.append({
                "experiment": "E1",
                "dataset": ds_name,
                "total_records": res["total_records"],
                "engine": "Hadoop_Streaming",
                "iteration": i,
                "execution_time_sec": res["execution_time_sec"],
                "peak_ram_mb": 0.0,
                "status": "SUCCESS",
            })
            logger.info("Hadoop Run %d: %.3f s", i, res["execution_time_sec"])

        # 3. Apache Spark (local[*])
        logger.info("--- Probando Apache Spark en %s (%d repeticiones) ---", ds_name, repetitions)
        for i in range(1, repetitions + 1):
            res = run_isolated_json("src/processing/spark/batch_analysis.py", ["--input", ds_path, "--master", "local[*]"])
            records.append({
                "experiment": "E1",
                "dataset": ds_name,
                "total_records": res["total_records"],
                "engine": "Apache_Spark",
                "iteration": i,
                "execution_time_sec": res["compute_time_sec"],
                "peak_ram_mb": 0.0,
                "status": "SUCCESS",
            })
            logger.info("Spark Run %d: Cómputo %.3f s (Total JVM+Init: %.3f s)", i, res["compute_time_sec"], res["total_time_sec"])

    save_metrics_to_csv(results_file, records, fieldnames, overwrite=True)


# Experimento 2: Escalabilidad y Speedup de Spark (1, 2 y 3 Workers / Hilos)
def run_experiment_2(dataset_path: str, repetitions: int = 3):
    logger.info("=== INICIANDO EXPERIMENTO E2: Escalabilidad y Speedup de Spark en %s ===", os.path.basename(dataset_path))
    results_file = os.path.join(METRICS_DIR, "experiment_2_spark_scalability.csv")
    fieldnames = [
        "experiment", "dataset", "workers", "iteration", "compute_time_sec",
        "total_time_sec", "status"
    ]
    records = []

    for w in [1, 2, 3]:
        master_url = f"local[{w}]"
        logger.info("--- Evaluando Spark con %d Worker(s) (%s) ---", w, master_url)
        for i in range(1, repetitions + 1):
            res = run_isolated_json("src/processing/spark/batch_analysis.py", ["--input", dataset_path, "--master", master_url])
            records.append({
                "experiment": "E2",
                "dataset": os.path.basename(dataset_path),
                "workers": w,
                "iteration": i,
                "compute_time_sec": res["compute_time_sec"],
                "total_time_sec": res["total_time_sec"],
                "status": "SUCCESS",
            })
            logger.info("Spark %d Worker(s) Run %d: Cómputo %.3f s", w, i, res["compute_time_sec"])

    save_metrics_to_csv(results_file, records, fieldnames, overwrite=True)


# Experimento 5: Control Automático y Latencia Real con Mosquitto + Controlador
def run_experiment_5(sensor_counts: list = [1, 10, 50], events_per_sensor: int = 15):
    logger.info("=== INICIANDO EXPERIMENTO E5: Latencia Real de Control en Lazo Cerrado ===")
    results_file = os.path.join(METRICS_DIR, "experiment_5_latency_summary.csv")
    controller_csv = os.path.join(METRICS_DIR, "controller_latencies.csv")
    fieldnames = [
        "experiment", "sensor_count", "mean_latency_ms", "std_latency_ms",
        "p50_latency_ms", "p95_latency_ms", "p99_latency_ms", "sample_size"
    ]

    # Levantar únicamente mosquitto y controller vía docker compose para medición real
    logger.info("Levantando Mosquitto y Controlador para medición real MQTT...")
    subprocess.run(["docker", "compose", "up", "-d", "mosquitto", "controller"], cwd=ROOT_DIR, check=True)
    time.sleep(3)

    records = []
    try:
        for n_sensors in sensor_counts:
            # Limpiar archivo de latencias previo antes de cada corrida
            if os.path.exists(controller_csv):
                os.remove(controller_csv)
            # Reiniciar controlador para tener archivo CSV limpio y conjunto de sensores limpio
            subprocess.run(["docker", "compose", "restart", "controller"], cwd=ROOT_DIR, check=True)
            time.sleep(2.5)

            barrier = threading.Barrier(n_sensors)

            def sensor_worker(sid: int):
                cli = mqtt.Client(
                    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                    client_id=f"bench_e5_{n_sensors}_{sid}",
                )
                cli.connect("localhost", 1883, keepalive=60)
                cli.loop_start()
                barrier.wait(timeout=10)
                topic = f"hidroponia/zona_e5_{sid}/telemetria"
                for step in range(events_per_sensor):
                    payload = json.dumps({
                        "timestamp": time.time(),
                        "zone_id": f"zona_e5_{sid}",
                        "sensor_id": f"node_e5_{sid}",
                        "ph": 7.15,  # Forzar anomalía para medir reacción real del controlador
                        "ec": 1.8,
                        "temperature": 21.0,
                        "humidity": 70.0,
                        "water_level": 80.0,
                        "is_anomaly": True,
                        "anomaly_type": "ph_high",
                    })
                    info = cli.publish(topic, payload, qos=1)
                    info.wait_for_publish(timeout=2)
                    time.sleep(0.05)
                cli.loop_stop()
                cli.disconnect()

            threads = [threading.Thread(target=sensor_worker, args=(s,)) for s in range(n_sensors)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # Esperar a que el controlador termine de volcar al CSV
            time.sleep(1.5)

            latencies = []
            if os.path.exists(controller_csv):
                with open(controller_csv, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        latencies.append(float(row["reaction_latency_ms"]))

            if not latencies:
                raise RuntimeError(f"No se registraron latencias reales para {n_sensors} sensores.")

            records.append({
                "experiment": "E5",
                "sensor_count": n_sensors,
                "mean_latency_ms": round(float(np.mean(latencies)), 3),
                "std_latency_ms": round(float(np.std(latencies)), 3),
                "p50_latency_ms": round(float(np.percentile(latencies, 50)), 3),
                "p95_latency_ms": round(float(np.percentile(latencies, 95)), 3),
                "p99_latency_ms": round(float(np.percentile(latencies, 99)), 3),
                "sample_size": len(latencies),
            })
            logger.info(
                "Sensores: %2d | Muestras reales: %d | Media: %.2f ms | Desvío: %.2f ms | P95: %.2f ms",
                n_sensors, len(latencies), np.mean(latencies), np.std(latencies), np.percentile(latencies, 95)
            )
    finally:
        logger.info("Deteniendo contenedores de prueba E5...")
        subprocess.run(["docker", "compose", "down"], cwd=ROOT_DIR, check=False)

    save_metrics_to_csv(results_file, records, fieldnames, overwrite=True)


def main():
    parser = argparse.ArgumentParser(description="Orquestador de experimentos E1, E2 y E5")
    parser.add_argument("--all", action="store_true", help="Ejecutar todos los experimentos (E1, E2, E5)")
    parser.add_argument("--e1", action="store_true", help="Ejecutar Experimento 1 (Volumen)")
    parser.add_argument("--e2", action="store_true", help="Ejecutar Experimento 2 (Escalabilidad Spark)")
    parser.add_argument("--e5", action="store_true", help="Ejecutar Experimento 5 (Latencia real MQTT)")
    parser.add_argument("--repetitions", type=int, default=3, help="Cantidad de repeticiones")
    args = parser.parse_args()

    ds_1m = os.path.join(DATASETS_DIR, "synthetic_1M.csv")
    ds_10m = os.path.join(DATASETS_DIR, "synthetic_10M.csv")

    if args.all or args.e1:
        datasets = [ds_1m]
        if os.path.exists(ds_10m):
            datasets.append(ds_10m)
        run_experiment_1(datasets, repetitions=args.repetitions)

    if args.all or args.e2:
        # Evaluar escalabilidad sobre el dataset más grande disponible (10M idealmente)
        target_ds = ds_10m if os.path.exists(ds_10m) else ds_1m
        run_experiment_2(target_ds, repetitions=args.repetitions)

    if args.all or args.e5:
        run_experiment_5()

    logger.info("Campaña experimental finalizada.")


if __name__ == "__main__":
    main()
