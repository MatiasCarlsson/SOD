#!/usr/bin/env python3
"""
Reducer para Hadoop Streaming.
Recibe pares (zone_id, valores) ordenados por clave, acumula sumas y cuentas,
y emite las medias y totales por zona.
"""
import sys

def main():
    current_zone = None
    count = 0
    sum_ph = 0.0
    sum_ec = 0.0
    sum_temp = 0.0
    sum_hum = 0.0
    sum_water = 0.0
    total_alerts = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            zone_id, val_str = line.split("\t", 1)
            parts = val_str.split(",")
            c = int(parts[0])
            ph = float(parts[1])
            ec = float(parts[2])
            temp = float(parts[3])
            hum = float(parts[4])
            water = float(parts[5])
            alert = int(parts[6])
        except (ValueError, IndexError):
            continue

        if current_zone == zone_id:
            count += c
            sum_ph += ph
            sum_ec += ec
            sum_temp += temp
            sum_hum += hum
            sum_water += water
            total_alerts += alert
        else:
            if current_zone is not None and count > 0:
                emit_zone_stats(current_zone, count, sum_ph, sum_ec, sum_temp, sum_hum, sum_water, total_alerts)

            current_zone = zone_id
            count = c
            sum_ph = ph
            sum_ec = ec
            sum_temp = temp
            sum_hum = hum
            sum_water = water
            total_alerts = alert

    # Emitir la última zona acumulada
    if current_zone is not None and count > 0:
        emit_zone_stats(current_zone, count, sum_ph, sum_ec, sum_temp, sum_hum, sum_water, total_alerts)


def emit_zone_stats(zone, count, sum_ph, sum_ec, sum_temp, sum_hum, sum_water, alerts):
    avg_ph = sum_ph / count
    avg_ec = sum_ec / count
    avg_temp = sum_temp / count
    avg_hum = sum_hum / count
    avg_water = sum_water / count
    print(
        f"{zone}\tcount={count}\tavg_ph={avg_ph:.3f}\tavg_ec={avg_ec:.3f}\t"
        f"avg_temp={avg_temp:.2f}\tavg_hum={avg_hum:.2f}\tavg_water={avg_water:.2f}\talerts={alerts}"
    )


if __name__ == "__main__":
    main()

