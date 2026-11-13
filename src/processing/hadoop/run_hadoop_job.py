#!/usr/bin/env python3
"""
Ejecutor y benchmark del pipeline MapReduce (Hadoop Streaming).
Permite ejecutar el job tanto en un entorno Hadoop real/contenedor
como mediante la emulación del flujo de pipes de streaming de Hadoop.
"""
import argparse
import json
import os
import subprocess
import time


def run_hadoop_streaming_local(csv_path: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mapper_path = os.path.join(base_dir, "mapper.py")
    reducer_path = os.path.join(base_dir, "reducer.py")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset {csv_path} no encontrado.")

    start_time = time.perf_counter()

    # Comando que emula exactamente la fase Map -> Shuffle/Sort -> Reduce de Hadoop Streaming
    cmd = f"python3 '{mapper_path}' < '{csv_path}' | sort -k1,1 | python3 '{reducer_path}'"

    proc = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    elapsed_time = time.perf_counter() - start_time

    if proc.returncode != 0:
        raise RuntimeError(f"Error ejecutando MapReduce: {proc.stderr}")

    lines = proc.stdout.strip().split("\n")
    summary = []
    total_records = 0

    for line in lines:
        if not line:
            continue
        parts = line.split("\t")
        zone = parts[0]
        data_dict = {"zone_id": zone}
        for item in parts[1:]:
            k, v = item.split("=")
            data_dict[k] = float(v) if "." in v else int(v)
        summary.append(data_dict)
        total_records += data_dict.get("count", 0)

    result = {
        "engine": "Hadoop_Streaming_MapReduce",
        "dataset": os.path.basename(csv_path),
        "total_records": total_records,
        "execution_time_sec": round(elapsed_time, 4),
        "summary": summary,
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Ejecutor MapReduce / Hadoop Streaming")
    parser.add_argument("--input", default="data/datasets/synthetic_1M.csv", help="Ruta al CSV")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args()

    result = run_hadoop_streaming_local(args.input)

    if args.json:
        print(json.dumps(result))
    else:
        print("\n" + "=" * 80)
        print(f" RESULTADO HADOOP STREAMING (MapReduce) | Dataset: {result['dataset']}")
        print("=" * 80)
        print(f"Tiempo de ejecución : {result['execution_time_sec']} segundos")
        print("-" * 80)
        print(f"{'Zona':<10} | {'Lecturas':<10} | {'pH Prom':<8} | {'CE Prom':<8} | {'Temp Prom':<10} | {'Alertas':<8}")
        print("-" * 80)
        for r in result["summary"]:
            print(f"{r['zone_id']:<10} | {r.get('count', 0):<10} | {r.get('avg_ph', 0):<8.3f} | {r.get('avg_ec', 0):<8.3f} | {r.get('avg_temp', 0):<10.2f} | {r.get('alerts', 0):<8}")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

