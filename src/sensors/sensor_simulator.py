#!/usr/bin/env python3
"""
Simulador de sensores de cultivo hidropónico para sistemas distribuidos.
Genera lecturas sintéticas con ruido gaussiano, deriva temporal y eventos anómalos.
"""
import argparse
import json
import logging
import os
import random
import sys
import time
from datetime import datetime, timezone
import numpy as np
import paho.mqtt.client as mqtt

# Intentar importar configuración compartida
try:
    from src.common.config import (
        MQTT_BROKER_HOST,
        MQTT_BROKER_PORT,
        MQTT_KEEPALIVE,
        TOPIC_TELEMETRY_TEMPLATE,
        THRESHOLDS,
    )
except ImportError:
    # Fallback si se ejecuta dentro de un contenedor aislado
    MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    MQTT_KEEPALIVE = 60
    TOPIC_TELEMETRY_TEMPLATE = "hidroponia/{zona_id}/telemetria"
    THRESHOLDS = {
        "ph": {"min_optimal": 5.5, "max_optimal": 6.5},
        "ec": {"min_optimal": 1.2, "max_optimal": 2.5},
        "temperature": {"min_optimal": 18.0, "max_optimal": 24.0},
        "humidity": {"min_optimal": 60.0, "max_optimal": 80.0},
        "water_level": {"min_optimal": 50.0, "max_optimal": 100.0, "critical_low": 30.0},
    }

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("SensorSimulator")


class HydroponicSensorNode:
    """Modela una estación sensora con múltiples transductores en una zona de cultivo."""

    def __init__(self, zone_id: str, seed: int = 42, anomaly_rate: float = 0.05):
        self.zone_id = zone_id
        self.seed = seed
        self.anomaly_rate = anomaly_rate
        self.rng = np.random.default_rng(seed)

        # Estados iniciales nominales
        self.ph = 6.0
        self.ec = 1.8
        self.temperature = 21.0
        self.humidity = 70.0
        self.water_level = 85.0

        # Parámetros de deriva y ruido (desviación estándar)
        self.noise_std = {
            "ph": 0.03,
            "ec": 0.02,
            "temperature": 0.15,
            "humidity": 0.5,
            "water_level": 0.05,
        }

        # Deriva gradual acumulada
        self.drift_step = 0

    def step(self, force_anomaly: bool = False) -> dict:
        """Avanza un paso de simulación y devuelve las lecturas del nodo."""
        self.drift_step += 1

        # Decidir si se inyecta una anomalía
        is_anomaly = force_anomaly or (self.rng.random() < self.anomaly_rate)
        anomaly_type = None

        if is_anomaly:
            anomaly_types = ["ph_high", "ph_low", "water_low", "temp_high"]
            anomaly_type = self.rng.choice(anomaly_types)

        # 1. pH: deriva lenta hacia arriba o abajo + ruido
        if is_anomaly and anomaly_type == "ph_high":
            self.ph = float(self.rng.uniform(6.65, 7.4))
        elif is_anomaly and anomaly_type == "ph_low":
            self.ph = float(self.rng.uniform(4.8, 5.35))
        else:
            # Oscilación suave con regreso a la media
            ph_drift = 0.002 * np.sin(self.drift_step * 0.05)
            self.ph += ph_drift + self.rng.normal(0, self.noise_std["ph"])
            self.ph = float(np.clip(self.ph, 4.5, 8.5))

        # 2. EC: deriva gradual por consumo de sales
        ec_noise = self.rng.normal(0, self.noise_std["ec"])
        self.ec += ec_noise
        self.ec = float(np.clip(self.ec, 0.5, 3.5))

        # 3. Temperatura: ciclo diurno simulado + ruido
        if is_anomaly and anomaly_type == "temp_high":
            self.temperature = float(self.rng.uniform(25.5, 29.0))
        else:
            temp_wave = 1.5 * np.sin(self.drift_step * 0.02)
            self.temperature = 21.0 + temp_wave + float(self.rng.normal(0, self.noise_std["temperature"]))

        # 4. Humedad relativa: inversamente proporcional a la temperatura
        self.humidity = 70.0 - 1.2 * (self.temperature - 21.0) + float(self.rng.normal(0, self.noise_std["humidity"]))
        self.humidity = float(np.clip(self.humidity, 30.0, 95.0))

        # 5. Nivel de agua: consumo constante (evapotranspiración)
        if is_anomaly and anomaly_type == "water_low":
            self.water_level = float(self.rng.uniform(15.0, 28.0))
        else:
            self.water_level -= float(self.rng.uniform(0.01, 0.04))
            if self.water_level < 35.0:
                # Simular recarga automática natural
                self.water_level = 90.0

        now = datetime.now(timezone.utc)
        reading = {
            "timestamp": now.timestamp(),
            "datetime": now.isoformat(),
            "zone_id": self.zone_id,
            "sensor_id": f"node_{self.zone_id}",
            "ph": round(self.ph, 3),
            "ec": round(self.ec, 3),
            "temperature": round(self.temperature, 2),
            "humidity": round(self.humidity, 2),
            "water_level": round(self.water_level, 2),
            "is_anomaly": bool(is_anomaly),
            "anomaly_type": anomaly_type if is_anomaly else "none",
        }
        return reading


def run_simulator(
    broker_host: str,
    broker_port: int,
    zone_id: str,
    frequency_hz: float,
    seed: int,
    duration_sec: int,
    anomaly_rate: float,
):
    """Bucle de ejecución del cliente MQTT que publica lecturas continuas."""
    logger.info("Iniciando simulador de sensores para zona '%s' -> %s:%d", zone_id, broker_host, broker_port)

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"sim_sensor_{zone_id}_{int(time.time())}",
    )

    def on_connect(cli, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Conectado exitosamente al broker MQTT.")
        else:
            logger.error("Fallo al conectar al broker MQTT. Código: %s", rc)

    client.on_connect = on_connect

    # Reintentos de conexión con backoff
    connected = False
    for attempt in range(1, 15):
        try:
            client.connect(broker_host, broker_port, keepalive=MQTT_KEEPALIVE)
            client.loop_start()
            connected = True
            break
        except Exception as e:
            logger.warning("Intento %d falló al conectar a %s:%d: %s. Reintentando...", attempt, broker_host, broker_port, e)
            time.sleep(2)

    if not connected:
        logger.critical("No fue posible conectar al broker MQTT. Abortando.")
        sys.exit(1)

    node = HydroponicSensorNode(zone_id=zone_id, seed=seed, anomaly_rate=anomaly_rate)
    topic = TOPIC_TELEMETRY_TEMPLATE.format(zona_id=zone_id)

    interval = 1.0 / frequency_hz if frequency_hz > 0 else 1.0
    start_time = time.time()
    count = 0

    try:
        while True:
            if duration_sec > 0 and (time.time() - start_time) >= duration_sec:
                logger.info("Duración máxima de simulación alcanzada (%d s). Finalizando.", duration_sec)
                break

            data = node.step()
            payload = json.dumps(data)

            # Publicación MQTT con QoS 1 para garantizar entrega
            result = client.publish(topic, payload, qos=1)
            result.wait_for_publish(timeout=2.0)

            count += 1
            if count % 10 == 0 or data["is_anomaly"]:
                logger.info(
                    "Zona: %s | pH: %.2f | CE: %.2f | T: %.1f°C | H2O: %.1f%% | Alerta: %s",
                    zone_id,
                    data["ph"],
                    data["ec"],
                    data["temperature"],
                    data["water_level"],
                    data["anomaly_type"],
                )

            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Simulación interrumpida por el usuario.")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Simulador desconectado. Total eventos emitidos: %d", count)


def main():
    parser = argparse.ArgumentParser(description="Simulador de sensores de hidroponía distribuido")
    parser.add_argument("--broker", default=os.getenv("MQTT_BROKER_HOST", MQTT_BROKER_HOST), help="Host del broker MQTT")
    parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_BROKER_PORT", MQTT_BROKER_PORT)), help="Puerto del broker MQTT")
    parser.add_argument("--zone", default=os.getenv("ZONE_ID", "zona_1"), help="Identificador de la zona/bandeja")
    parser.add_argument("--freq", type=float, default=float(os.getenv("SENSOR_FREQ_HZ", "1.0")), help="Frecuencia en Hz (lecturas/segundo)")
    parser.add_argument("--seed", type=int, default=int(os.getenv("RANDOM_SEED", "42")), help="Semilla aleatoria fija")
    parser.add_argument("--duration", type=int, default=int(os.getenv("SIM_DURATION_SEC", "0")), help="Duración en segundos (0 = infinito)")
    parser.add_argument("--anomaly-rate", type=float, default=float(os.getenv("ANOMALY_RATE", "0.08")), help="Probabilidad de forzar lecturas anómalas")

    args = parser.parse_args()
    run_simulator(
        broker_host=args.broker,
        broker_port=args.port,
        zone_id=args.zone,
        frequency_hz=args.freq,
        seed=args.seed,
        duration_sec=args.duration,
        anomaly_rate=args.anomaly_rate,
    )


if __name__ == "__main__":
    main()

