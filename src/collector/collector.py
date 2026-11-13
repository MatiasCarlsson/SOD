#!/usr/bin/env python3
"""
Servicio Recolector (Ingesta) de Telemetría Hidropónica.
Se suscribe al broker MQTT y persiste las lecturas en disco compartido
para análisis por lotes (Batch) y en tiempo real (Structured Streaming).
"""
import argparse
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
        RAW_DATA_DIR,
        TOPIC_BASE,
    )
except ImportError:
    MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    MQTT_KEEPALIVE = 60
    RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "/data/raw")
    TOPIC_BASE = "hidroponia"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("CollectorService")


class TelemetryCollector:
    def __init__(
        self,
        broker_host: str,
        broker_port: int,
        output_dir: str,
        flush_interval_sec: float = 5.0,
        batch_size: int = 50,
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.output_dir = output_dir
        self.flush_interval_sec = flush_interval_sec
        self.batch_size = batch_size

        os.makedirs(self.output_dir, exist_ok=True)
        self.buffer = []
        self.last_flush = time.time()
        self.total_records = 0
        self.running = True

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"collector_{int(time.time())}",
        )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Recolector conectado al broker MQTT. Suscribiendo a '%s/#'...", TOPIC_BASE)
            client.subscribe(f"{TOPIC_BASE}/#", qos=1)
        else:
            logger.error("Error al conectar recolector con broker: %s", rc)

    def on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
            # Agregar metadatos de recolección
            data["_ingest_time"] = time.time()
            data["_topic"] = msg.topic
            self.buffer.append(data)
            self.total_records += 1

            if len(self.buffer) >= self.batch_size or (time.time() - self.last_flush) >= self.flush_interval_sec:
                self.flush_buffer()
        except Exception as e:
            logger.error("Error procesando mensaje en tópico %s: %s", msg.topic, e)

    def flush_buffer(self):
        if not self.buffer:
            return

        batch_to_write = self.buffer[:]
        self.buffer.clear()
        self.last_flush = time.time()

        now = datetime.now(timezone.utc)
        # Nombre de archivo único compatible con monitor de Spark Structured Streaming
        file_name = f"batch_{now.strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000)}.json"
        target_path = os.path.join(self.output_dir, file_name)
        temp_path = target_path + ".tmp"

        try:
            # Escribir en .tmp primero y luego renombrar atómicamente
            with open(temp_path, "w", encoding="utf-8") as f:
                for item in batch_to_write:
                    f.write(json.dumps(item) + "\n")
            os.replace(temp_path, target_path)
            logger.info("Persistidos %d registros en %s (Total acumulado: %d)", len(batch_to_write), file_name, self.total_records)
        except Exception as e:
            logger.error("Error guardando lote en disco: %s", e)
            # Recuperar registros en buffer si falló
            self.buffer.extend(batch_to_write)

    def start(self):
        logger.info("Iniciando servicio recolector en %s:%d (Salida: %s)", self.broker_host, self.broker_port, self.output_dir)

        # Conectar con reintentos
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
                if self.buffer and (time.time() - self.last_flush) >= self.flush_interval_sec:
                    self.flush_buffer()
        finally:
            self.stop()

    def stop(self):
        logger.info("Deteniendo recolector y purgando buffer final...")
        self.running = False
        self.flush_buffer()
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Recolector finalizado correctamente. Total registros guardados: %d", self.total_records)


def main():
    parser = argparse.ArgumentParser(description="Recolector de datos MQTT para cultivo hidropónico")
    parser.add_argument("--broker", default=os.getenv("MQTT_BROKER_HOST", MQTT_BROKER_HOST))
    parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_BROKER_PORT", MQTT_BROKER_PORT)))
    parser.add_argument("--outdir", default=os.getenv("RAW_DATA_DIR", RAW_DATA_DIR))
    parser.add_argument("--flush-interval", type=float, default=float(os.getenv("FLUSH_INTERVAL", "3.0")))
    parser.add_argument("--batch-size", type=int, default=int(os.getenv("BATCH_SIZE", "25")))

    args = parser.parse_args()

    collector = TelemetryCollector(
        broker_host=args.broker,
        broker_port=args.port,
        output_dir=args.outdir,
        flush_interval_sec=args.flush_interval,
        batch_size=args.batch_size,
    )

    def sig_handler(sig, frame):
        logger.info("Señal de terminación recibida.")
        collector.running = False

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    collector.start()


if __name__ == "__main__":
    main()

