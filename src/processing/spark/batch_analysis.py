#!/usr/bin/env python3
"""
Job de Procesamiento por Lotes con Apache Spark (PySpark DataFrame API).
Calcula las mismas métricas agregadas por zona que Python baseline y Hadoop
para evaluar rendimiento, escalabilidad y aceleración (Speedup).
"""
import argparse
import json
import os
import sys
import time

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import avg, col, count, round as spark_round, sum as spark_sum
    from pyspark.sql.types import (
        DoubleType,
        IntegerType,
        StringType,
        StructField,
        StructType,
    )
except ImportError:
    print("Error: PySpark no está instalado en el entorno actual.", file=sys.stderr)
    sys.exit(1)


def run_spark_batch(csv_path: str, master_url: str = "local[*]", app_name: str = "HydroponicBatchAnalysis"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset {csv_path} no encontrado.")

    start_init = time.perf_counter()

    spark = (
        SparkSession.builder.appName(app_name)
        .master(master_url)
        .config("spark.driver.memory", "2g")
        .config("spark.executor.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    schema = StructType([
        StructField("timestamp", DoubleType(), True),
        StructField("zone_id", StringType(), True),
        StructField("sensor_id", StringType(), True),
        StructField("ph", DoubleType(), True),
        StructField("ec", DoubleType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("humidity", DoubleType(), True),
        StructField("water_level", DoubleType(), True),
        StructField("is_alert", IntegerType(), True),
    ])

    # Medir tiempo del cómputo puro
    start_compute = time.perf_counter()

    df = spark.read.option("header", "true").schema(schema).csv(csv_path)

    aggregated_df = (
        df.groupBy("zone_id")
        .agg(
            count("*").alias("count"),
            spark_round(avg("ph"), 3).alias("avg_ph"),
            spark_round(avg("ec"), 3).alias("avg_ec"),
            spark_round(avg("temperature"), 2).alias("avg_temp"),
            spark_round(avg("humidity"), 2).alias("avg_hum"),
            spark_round(avg("water_level"), 2).alias("avg_water"),
            spark_sum("is_alert").alias("alerts"),
        )
        .orderBy("zone_id")
    )

    rows = aggregated_df.collect()
    compute_time = time.perf_counter() - start_compute
    total_time = time.perf_counter() - start_init

    summary = []
    total_records = 0
    for r in rows:
        d = r.asDict()
        total_records += d["count"]
        summary.append(d)

    spark.stop()

    result = {
        "engine": "Apache_Spark",
        "master": master_url,
        "dataset": os.path.basename(csv_path),
        "total_records": total_records,
        "compute_time_sec": round(compute_time, 4),
        "total_time_sec": round(total_time, 4),
        "summary": summary,
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Análisis de lotes con PySpark")
    parser.add_argument("--input", default="data/datasets/synthetic_1M.csv", help="Ruta al CSV")
    parser.add_argument("--master", default="local[*]", help="Master URL (local[*], local[1], spark://...)")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args()

    result = run_spark_batch(args.input, master_url=args.master)

    if args.json:
        print(json.dumps(result))
    else:
        print("\n" + "=" * 80)
        print(f" RESULTADO APACHE SPARK | Master: {result['master']} | Dataset: {result['dataset']}")
        print("=" * 80)
        print(f"Tiempo de cómputo   : {result['compute_time_sec']} segundos")
        print(f"Tiempo total (Init) : {result['total_time_sec']} segundos")
        print("-" * 80)
        print(f"{'Zona':<10} | {'Lecturas':<10} | {'pH Prom':<8} | {'CE Prom':<8} | {'Temp Prom':<10} | {'Alertas':<8}")
        print("-" * 80)
        for r in result["summary"]:
            print(f"{r['zone_id']:<10} | {r['count']:<10} | {r['avg_ph']:<8.3f} | {r['avg_ec']:<8.3f} | {r['avg_temp']:<10.2f} | {r['alerts']:<8}")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

