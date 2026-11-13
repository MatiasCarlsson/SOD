#!/usr/bin/env python3
"""
Procesamiento analítico en Python monohilo (Línea Base / Baseline).
Calcula métricas agrupadas por zona (media de pH, CE, temperatura, humedad, nivel y conteo de alertas)
para contrastar tiempos y consumo de recursos frente a Hadoop y Spark.
"""
import argparse
import csv
import json
import os
import resource
import sys
import time


def process_baseline(csv_path: str):
    start_time = time.perf_counter()

    if not os.path.exists(csv_path):
        print(f"Error: Archivo {csv_path} no encontrado.", file=sys.stderr)
        sys.exit(1)

    # Estructura acumuladora por zona:
    # zone_id -> { count, sum_ph, sum_ec, sum_temp, sum_hum, sum_water, alerts }
    stats = {}

    total_rows = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            zone = row["zone_id"]
            if zone not in stats:
                stats[zone] = {
                    "count": 0,
                    "sum_ph": 0.0,
                    "sum_ec": 0.0,
                    "sum_temp": 0.0,
                    "sum_hum": 0.0,
                    "sum_water": 0.0,
                    "alerts": 0,
                }

            s = stats[zone]
            s["count"] += 1
            s["sum_ph"] += float(row["ph"])
            s["sum_ec"] += float(row["ec"])
            s["sum_temp"] += float(row["temperature"])
            s["sum_hum"] += float(row["humidity"])
            s["sum_water"] += float(row["water_level"])
            s["alerts"] += int(row["is_alert"])

    elapsed_time = time.perf_counter() - start_time
    # Memoria residente máxima en KB (Linux: ru_maxrss está en KB)
    max_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    max_rss_mb = max_rss_kb / 1024.0

    # Construir resultado consolidado
    results = []
    for zone in sorted(stats.keys()):
        s = stats[zone]
        c = s["count"]
        results.append({
            "zone_id": zone,
            "readings_count": c,
            "avg_ph": round(s["sum_ph"] / c, 4),
            "avg_ec": round(s["sum_ec"] / c, 4),
            "avg_temp": round(s["sum_temp"] / c, 4),
            "avg_humidity": round(s["sum_hum"] / c, 4),
            "avg_water_level": round(s["sum_water"] / c, 4),
            "total_alerts": s["alerts"],
        })

    output = {
        "engine": "Python_Baseline",
        "dataset": os.path.basename(csv_path),
        "total_records": total_rows,
        "execution_time_sec": round(elapsed_time, 4),
        "peak_ram_mb": round(max_rss_mb, 2),
        "summary": results,
    }

    return output


def main():
    parser = argparse.ArgumentParser(description="Procesamiento analítico base en Python")
    parser.add_argument("--input", default="data/datasets/synthetic_1M.csv", help="Ruta al CSV")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON compacto")
    args = parser.parse_args()

    result = process_baseline(args.input)

    if args.json:
        print(json.dumps(result))
    else:
        print("\n" + "=" * 80)
        print(f" RESULTADO LÍNEA BASE PYTHON | Dataset: {result['dataset']} ({result['total_records']:,} filas)")
        print("=" * 80)
        print(f"Tiempo de ejecución : {result['execution_time_sec']} segundos")
        print(f"Consumo RAM pico    : {result['peak_ram_mb']} MB")
        print("-" * 80)
        print(f"{'Zona':<10} | {'Lecturas':<10} | {'pH Prom':<8} | {'CE Prom':<8} | {'Temp Prom':<10} | {'Alertas':<8}")
        print("-" * 80)
        for r in result["summary"]:
            print(f"{r['zone_id']:<10} | {r['readings_count']:<10} | {r['avg_ph']:<8.3f} | {r['avg_ec']:<8.3f} | {r['avg_temp']:<10.2f} | {r['total_alerts']:<8}")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

