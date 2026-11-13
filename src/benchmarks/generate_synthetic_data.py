#!/usr/bin/env python3
"""
Generador de datasets sintéticos masivos con semilla fija.
Genera volúmenes de 1M, 10M y 100M de registros en bloques (chunks)
para evaluar el rendimiento de Python, Hadoop y Spark sin desbordar la memoria RAM.
"""
import argparse
import csv
import logging
import os
import sys
import time
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("DataGenerator")


def generate_dataset(
    output_path: str,
    total_records: int,
    seed: int = 42,
    num_zones: int = 5,
    chunk_size: int = 100_000,
):
    """Genera un archivo CSV particionado en chunks con datos sintéticos deterministas."""
    logger.info("Iniciando generación de %s registros en %s (Semilla: %d)", f"{total_records:,}", output_path, seed)
    start_time = time.time()

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    rng = np.random.default_rng(seed)

    base_timestamp = 1773000000.0  # Marca temporal de referencia
    zones = [f"zona_{i+1}" for i in range(num_zones)]

    headers = [
        "timestamp",
        "zone_id",
        "sensor_id",
        "ph",
        "ec",
        "temperature",
        "humidity",
        "water_level",
        "is_alert",
    ]

    records_written = 0
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        while records_written < total_records:
            current_chunk = min(chunk_size, total_records - records_written)

            # Generación vectorizada de variables con NumPy
            timestamps = base_timestamp + records_written + np.arange(current_chunk)
            zone_indices = rng.integers(0, num_zones, size=current_chunk)
            selected_zones = [zones[idx] for idx in zone_indices]
            sensor_ids = [f"node_{z}" for z in selected_zones]

            # Distribuciones agronómicas
            ph_values = np.round(rng.normal(6.0, 0.35, size=current_chunk), 3)
            ec_values = np.round(rng.normal(1.8, 0.25, size=current_chunk), 3)
            temp_values = np.round(rng.normal(21.0, 2.0, size=current_chunk), 2)
            hum_values = np.round(rng.normal(70.0, 5.0, size=current_chunk), 2)
            water_values = np.round(rng.uniform(35.0, 95.0, size=current_chunk), 2)

            # Inyectar ~8% de alertas deterministas
            is_alert = (
                (ph_values < 5.5) | (ph_values > 6.5) |
                (water_values < 30.0) |
                (temp_values > 24.0) | (temp_values < 18.0)
            ).astype(int)

            # Forzar valores anómalos en ~5% de los casos
            anomaly_mask = rng.random(size=current_chunk) < 0.05
            ph_values[anomaly_mask] = np.round(rng.uniform(6.8, 7.8, size=np.sum(anomaly_mask)), 3)
            is_alert[anomaly_mask] = 1

            rows = zip(
                timestamps,
                selected_zones,
                sensor_ids,
                ph_values,
                ec_values,
                temp_values,
                hum_values,
                water_values,
                is_alert,
            )
            writer.writerows(rows)
            records_written += current_chunk

            if records_written % (chunk_size * 5) == 0 or records_written == total_records:
                pct = (records_written / total_records) * 100.0
                elapsed = time.time() - start_time
                logger.info("Progreso: %d/%d (%.1f%%) en %.1fs", records_written, total_records, pct, elapsed)

    total_time = time.time() - start_time
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    logger.info(
        "Generación completa: %d registros guardados en %.2fs (Tamaño: %.2f MB)",
        records_written, total_time, file_size_mb
    )


def main():
    parser = argparse.ArgumentParser(description="Generador masivo de datos de sensores para benchmarks")
    parser.add_argument("--count", type=int, default=1_000_000, help="Total de registros a generar (ej: 1000000, 10000000)")
    parser.add_argument("--output", default="data/datasets/synthetic_1M.csv", help="Ruta de destino del CSV")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria fija")
    parser.add_argument("--zones", type=int, default=5, help="Cantidad de zonas")
    parser.add_argument("--chunk-size", type=int, default=100_000, help="Tamaño de bloque en memoria")

    args = parser.parse_args()
    generate_dataset(
        output_path=args.output,
        total_records=args.count,
        seed=args.seed,
        num_zones=args.zones,
        chunk_size=args.chunk_size,
    )


if __name__ == "__main__":
    main()

