#!/usr/bin/env python3
"""
Mapper para Hadoop Streaming.
Lee líneas CSV desde stdin y emite (zone_id, valores_metricas).
"""
import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("timestamp"):
            continue  # Saltear cabecera o líneas vacías

        parts = line.split(",")
        if len(parts) < 9:
            continue

        # Esquema: timestamp, zone_id, sensor_id, ph, ec, temperature, humidity, water_level, is_alert
        zone_id = parts[1]
        try:
            ph = parts[3]
            ec = parts[4]
            temp = parts[5]
            hum = parts[6]
            water = parts[7]
            alert = parts[8]
            # Emisión: clave \t 1,ph,ec,temp,hum,water,alert
            print(f"{zone_id}\t1,{ph},{ec},{temp},{hum},{water},{alert}")
        except (ValueError, IndexError):
            continue

if __name__ == "__main__":
    main()

