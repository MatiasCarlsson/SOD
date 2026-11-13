#!/usr/bin/env python3
"""
Procesamiento en tiempo real con Apache Spark Structured Streaming.
Monitorea la carpeta de ingesta del recolector (/data/raw/) y calcula
agregaciones continuas en ventanas de tiempo con manejo de marcas de agua.
"""
import argparse
import os
import sys
import time

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import (
        avg,
        col,
        count,
        from_unixtime,
        round as spark_round,
        sum as spark_sum,
        to_timestamp,
        window,
    )
    from pyspark.sql.types import (
        BooleanType,
        DoubleType,
        StringType,
        StructField,
        StructType,
    )
except ImportError:
    print("Error: PySpark no está disponible.", file=sys.stderr)
    sys.exit(1)


def run_streaming(input_dir: str, master_url: str = "local[2]"):
    os.makedirs(input_dir, exist_ok=True)

    spark = (
        SparkSession.builder.appName("HydroponicStructuredStreaming")
        .master(master_url)
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    # Esquema de los eventos JSON emitidos por el recolector
    schema = StructType([
        StructField("timestamp", DoubleType(), True),
        StructField("datetime", StringType(), True),
        StructField("zone_id", StringType(), True),
        StructField("sensor_id", StringType(), True),
        StructField("ph", DoubleType(), True),
        StructField("ec", DoubleType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("humidity", DoubleType(), True),
        StructField("water_level", DoubleType(), True),
        StructField("is_anomaly", BooleanType(), True),
        StructField("anomaly_type", StringType(), True),
    ])

    print(f"Iniciando Spark Structured Streaming sobre {input_dir}...")

    # Fuente en streaming: monitor de archivos JSON
    stream_df = (
        spark.readStream.schema(schema)
        .option("maxFilesPerTrigger", 5)
        .json(input_dir)
    )

    # Conversión de timestamp epoch a TimestampType para soporte de ventanas
    with_ts = stream_df.withColumn("event_time", to_timestamp(from_unixtime(col("timestamp"))))

    # Agregación en ventanas de 30 segundos
    windowed_agg = (
        with_ts.withWatermark("event_time", "1 minute")
        .groupBy(
            window(col("event_time"), "30 seconds", "10 seconds"),
            col("zone_id"),
        )
        .agg(
            count("*").alias("lecturas"),
            spark_round(avg("ph"), 2).alias("avg_ph"),
            spark_round(avg("ec"), 2).alias("avg_ec"),
            spark_round(avg("temperature"), 1).alias("avg_temp"),
            spark_round(avg("water_level"), 1).alias("avg_water"),
            spark_sum(col("is_anomaly").cast("int")).alias("anomalias"),
        )
    )

    query = (
        windowed_agg.writeStream.outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .start()
    )

    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("\nDeteniendo Structured Streaming...")
        query.stop()
        spark.stop()


def main():
    parser = argparse.ArgumentParser(description="Spark Structured Streaming para sensores hidropónicos")
    parser.add_argument("--input-dir", default="data/raw", help="Directorio con archivos JSON")
    parser.add_argument("--master", default="local[2]", help="URL de Spark Master")
    args = parser.parse_args()

    run_streaming(args.input_dir, args.master)


if __name__ == "__main__":
    main()

