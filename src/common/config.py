"""
Configuración centralizada y constantes agronómicas para el sistema hidropónico.
"""
import os

# MQTT Broker Configuration
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_KEEPALIVE = 60

# Directorios de datos y métricas
DATA_DIR = os.getenv("DATA_DIR", "/data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
METRICS_DATA_DIR = os.path.join(DATA_DIR, "metrics")

# Tópicos MQTT
TOPIC_BASE = "hidroponia"
TOPIC_TELEMETRY = f"{TOPIC_BASE}/+/telemetria"
TOPIC_TELEMETRY_TEMPLATE = f"{TOPIC_BASE}/{{zona_id}}/telemetria"
TOPIC_ACTUATORS_TEMPLATE = f"{TOPIC_BASE}/{{zona_id}}/actuadores/{{actuador}}"
TOPIC_ALERTS = f"{TOPIC_BASE}/alertas"

# Rangos agronómicos óptimos y umbrales de alerta
# Cultivo de referencia: Hortalizas de hoja (Lechuga / Rúcula / Espinaca en NFT)
THRESHOLDS = {
    "ph": {
        "min_optimal": 5.5,
        "max_optimal": 6.5,
        "critical_low": 5.0,
        "critical_high": 7.0,
        "unit": "pH",
    },
    "ec": {  # Conductividad Eléctrica (mS/cm)
        "min_optimal": 1.2,
        "max_optimal": 2.5,
        "critical_low": 0.8,
        "critical_high": 3.0,
        "unit": "mS/cm",
    },
    "temperature": {  # Temperatura del agua (°C)
        "min_optimal": 18.0,
        "max_optimal": 24.0,
        "critical_low": 15.0,
        "critical_high": 27.0,
        "unit": "°C",
    },
    "humidity": {  # Humedad relativa del ambiente (%)
        "min_optimal": 60.0,
        "max_optimal": 80.0,
        "critical_low": 40.0,
        "critical_high": 90.0,
        "unit": "%",
    },
    "water_level": {  # Nivel del tanque de solución nutritiva (%)
        "min_optimal": 50.0,
        "max_optimal": 100.0,
        "critical_low": 30.0,  # Requiere reposición inmediata
        "critical_high": 100.0,
        "unit": "%",
    },
}

# Actuadores disponibles y acciones correctivas
ACTUATOR_ACTIONS = {
    "ph_high": {
        "actuator": "dosificador_acido",
        "action": "DOSIFICAR_ACIDO",
        "reason": "pH superior al umbral máximo permitido (> 6.5)",
    },
    "ph_low": {
        "actuator": "dosificador_base",
        "action": "DOSIFICAR_BASE",
        "reason": "pH inferior al umbral mínimo permitido (< 5.5)",
    },
    "water_low": {
        "actuator": "bomba_agua",
        "action": "REPONER_AGUA",
        "reason": "Nivel de solución nutritiva bajo (< 30%)",
    },
    "temp_high": {
        "actuator": "chiller_enfriador",
        "action": "ACTIVAR_ENFRIADOR",
        "reason": "Temperatura de agua elevada (> 24°C)",
    },
    "temp_low": {
        "actuator": "calefactor_agua",
        "action": "ACTIVAR_CALEFACTOR",
        "reason": "Temperatura de agua baja (< 18°C)",
    },
}

