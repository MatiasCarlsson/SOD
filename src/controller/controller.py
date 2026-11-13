#!/usr/bin/env python3
"""
Controlador Automático en Lazo Cerrado para Cultivo Hidropónico.
Evalúa lecturas en tiempo real, aplica lógica de control reactivo sobre actuadores
y mide con precisión la latencia de respuesta para el Experimento E5.
"""
import argparse
import csv
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

try:
    from src.common.config import (
        MQTT_BROKER_HOST,
        MQTT_BROKER_PORT,
        MQTT_KEEPALIVE,
        METRICS_DATA_DIR,
        TOPIC_BASE,
        TOPIC_TELEMETRY,
        TOPIC_ACTUATORS_TEMPLATE,
        THRESHOLDS,
        ACTUATOR_ACTIONS,
    )
except ImportError:
    MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    MQTT_KEEPALIVE = 60
    METRICS_DATA_DIR = os.getenv("METRICS_DATA_DIR", "/data/metrics")
    TOPIC_BASE = "hidroponia"
    TOPIC_TELEMETRY = "hidroponia/+/telemetria"
    TOPIC_ACTUATORS_TEMPLATE = "hidroponia/{zona_id}/actuadores/{actuador}"
    THRESHOLDS = {
        "ph": {"min_optimal": 5.5, "max_optimal": 6.5},
        "ec": {"min_optimal": 1.2, "max_optimal": 2.5},
        "temperature": {"min_optimal": 18.0, "max_optimal": 24.0},
        "water_level": {"critical_low": 30.0},
    }
    ACTUATOR_ACTIONS = {
        "ph_high": {"actuator": "dosificador_acido", "action": "DOSIFICAR_ACIDO"},
        "ph_low": {"actuator": "dosificador_base", "action": "DOSIFICAR_BASE"},
        "water_low": {"actuator": "bomba_agua", "action": "REPONER_AGUA"},
        "temp_high": {"actuator": "chiller_enfriador", "action": "ACTIVAR_ENFRIADOR"},
        "temp_low": {"actuator": "calefactor_agua", "action": "ACTIVAR_CALEFACTOR"},
    }

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("ClosedLoopController")


class HydroponicController:
    def __init__(
        self,
        broker_host: str,
        broker_port: int,
        metrics_dir: str,
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.metrics_dir = metrics_dir
        os.makedirs(self.metrics_dir, exist_ok=True)

        self.latency_log_path = os.path.join(self.metrics_dir, "controller_latencies.csv")
        self._init_csv()

        self.running = True
        self.total_processed = 0
        self.total_actions = 0
        self.active_sensors = set()

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"controller_{int(time.time())}",
        )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def _init_csv(self):
        if not os.path.exists(self.latency_log_path):
            with open(self.latency_log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "datetime",
                    "zone_id",
                    "sensor_id",
                    "variable",
                    "value",
                    "trigger_rule",
                    "action_executed",
                    "reaction_latency_ms",
                    "active_sensors_count",
                ])

    def log_latency(self, zone_id, sensor_id, variable, val, rule, action, latency_ms):
        now = datetime.now(timezone.utc)
        with open(self.latency_log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                now.timestamp(),
                now.isoformat(),
                zone_id,
                sensor_id,
                variable,
                val,
                rule,
                action,
                round(latency_ms, 3),
                len(self.active_sensors),
            ])

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Controlador conectado al broker MQTT. Escuchando telemetría en '%s'...", TOPIC_TELEMETRY)
            client.subscribe(TOPIC_TELEMETRY, qos=1)
        else:
            logger.error("Error al conectar controlador al broker: %s", rc)

    def on_message(self, client, userdata, msg):
        received_time = time.time()
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            zone_id = payload.get("zone_id", "zona_desconocida")
            sensor_id = payload.get("sensor_id", "sensor_default")
            self.active_sensors.add(sensor_id)
            self.total_processed += 1

            sensor_ts = payload.get("timestamp", received_time)

            ph = payload.get("ph")
            water_level = payload.get("water_level")
            temp = payload.get("temperature")

            # Regla 1: Control de pH alto (> 6.5) -> Dosificar Ácido
            if ph is not None and ph > THRESHOLDS["ph"]["max_optimal"]:
                self._dispatch_action(
                    zone_id, sensor_id, "ph", ph, "ph_high", "dosificador_acido",
                    "DOSIFICAR_ACIDO", 5, sensor_ts, received_time
                )

            # Regla 2: Control de pH bajo (< 5.5) -> Dosificar Base
            elif ph is not None and ph < THRESHOLDS["ph"]["min_optimal"]:
                self._dispatch_action(
                    zone_id, sensor_id, "ph", ph, "ph_low", "dosificador_base",
                    "DOSIFICAR_BASE", 5, sensor_ts, received_time
                )

            # Regla 3: Control de nivel crítico de agua (< 30%) -> Reponer Agua
            if water_level is not None and water_level < THRESHOLDS["water_level"]["critical_low"]:
                self._dispatch_action(
                    zone_id, sensor_id, "water_level", water_level, "water_low", "bomba_agua",
                    "REPONER_AGUA", 15, sensor_ts, received_time
                )

            # Regla 4: Control de temperatura de solución nutritiva
            if temp is not None and temp > THRESHOLDS["temperature"]["max_optimal"]:
                self._dispatch_action(
                    zone_id, sensor_id, "temperature", temp, "temp_high", "chiller_enfriador",
                    "ACTIVAR_ENFRIADOR", 30, sensor_ts, received_time
                )
            elif temp is not None and temp < THRESHOLDS["temperature"]["min_optimal"]:
                self._dispatch_action(
                    zone_id, sensor_id, "temperature", temp, "temp_low", "calefactor_agua",
                    "ACTIVAR_CALEFACTOR", 30, sensor_ts, received_time
                )

        except Exception as e:
            logger.error("Error evaluando mensaje de control: %s", e)

    def _dispatch_action(
        self, zone_id, sensor_id, variable, val, rule, actuator_name, action, duration_sec, sensor_ts, received_time
    ):
        now = time.time()
        # Latencia total desde emisión del sensor hasta la orden al actuador
        reaction_latency_ms = (now - sensor_ts) * 1000.0

        actuator_topic = TOPIC_ACTUATORS_TEMPLATE.format(zona_id=zone_id, actuador=actuator_name)
        command_payload = {
            "action": action,
            "actuator": actuator_name,
            "zone_id": zone_id,
            "trigger_variable": variable,
            "trigger_value": val,
            "duration_seconds": duration_sec,
            "sensor_timestamp": sensor_ts,
            "command_timestamp": now,
            "reaction_latency_ms": round(reaction_latency_ms, 3),
        }

        self.client.publish(actuator_topic, json.dumps(command_payload), qos=1)
        self.total_actions += 1

        self.log_latency(zone_id, sensor_id, variable, val, rule, action, reaction_latency_ms)

        logger.warning(
            "ACCION REPORTE -> Zona: %s | Sensor: %s | %s=%.2f | Orden: %s (%s) | Latencia: %.2f ms",
            zone_id, sensor_id, variable, val, action, actuator_name, reaction_latency_ms
        )

    def start(self):
        logger.info("Iniciando controlador en lazo cerrado en %s:%d", self.broker_host, self.broker_port)
        for attempt in range(1, 15):
            try:
                self.client.connect(self.broker_host, self.broker_port, keepalive=MQTT_KEEPALIVE)
                self.client.loop_start()
                break
            except Exception as e:
                logger.warning("Intento %d de conexión falló: %s. Reintentando...", attempt, e)
                time.sleep(2)

        try:
            while self.running:
                time.sleep(1.0)
        finally:
            self.stop()

    def stop(self):
        logger.info("Deteniendo controlador...")
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Controlador detenido. Total evaluados: %d, Acciones: %d", self.total_processed, self.total_actions)


def main():
    parser = argparse.ArgumentParser(description="Controlador automático de hidroponía")
    parser.add_argument("--broker", default=os.getenv("MQTT_BROKER_HOST", MQTT_BROKER_HOST))
    parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_BROKER_PORT", MQTT_BROKER_PORT)))
    parser.add_argument("--metrics-dir", default=os.getenv("METRICS_DATA_DIR", METRICS_DATA_DIR))

    args = parser.parse_args()

    controller = HydroponicController(
        broker_host=args.broker,
        broker_port=args.port,
        metrics_dir=args.metrics_dir,
    )

    def sig_handler(sig, frame):
        controller.running = False

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    controller.start()


if __name__ == "__main__":
    main()

