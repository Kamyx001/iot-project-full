import os
import logging
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from dotenv import load_dotenv
from backend.mqtt_handler import handle_sensor_data

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))

TOPIC_DATA = "host/+/data"
TOPIC_CONFIG = "host/{host_id}/config"

def on_connect(client, userdata, flags, reason_code, properties=None):
    logging.info("Connected to broker (rc=%s)", reason_code)
    result = client.subscribe(TOPIC_DATA)
    logging.info("Subscribe result: %s", result)

def on_message(client, userdata, msg):
    print(
        "Message received on topic %s : %s (mid=%s qos=%s dup=%s retain=%s)",
        msg.topic, msg.payload, getattr(msg, "mid", None),
        getattr(msg, "qos", None), getattr(msg, "dup", None),
        getattr(msg, "retain", None),
    )
    # Store sensor data in backend database
    payload = msg.payload.decode('utf-8', errors='replace')
    handle_sensor_data(msg.topic, payload)

def send_settings(host_id: str, settings: str):
    topic = TOPIC_CONFIG.format(host_id=host_id)
    try:
        publish.single(topic, payload=settings, hostname=MQTT_BROKER, port=MQTT_PORT)
    except Exception:
        logging.exception("Failed to publish settings to %s:%s", MQTT_BROKER, MQTT_PORT)

def send_plant_ranges(rpi_id: int, temp_min: float, temp_max: float, humid_min: float, humid_max: float):
    """
    Send critical temperature and humidity ranges to an RPI.

    Args:
        rpi_id: RPI identifier
        temp_min: Minimum critical temperature (°C)
        temp_max: Maximum critical temperature (°C)
        humid_min: Minimum critical humidity (%)
        humid_max: Maximum critical humidity (%)
    """
    topic = TOPIC_CONFIG.format(host_id=rpi_id)
    import json
    payload = json.dumps({
        'temp_min': temp_min,
        'temp_max': temp_max,
        'humid_min': humid_min,
        'humid_max': humid_max
    })
    try:
        publish.single(topic, payload=payload, hostname=MQTT_BROKER, port=MQTT_PORT)
        logging.info(f"Sent ranges to RPI {rpi_id}: {payload}")
    except Exception:
        logging.exception("Failed to publish ranges to %s:%s", MQTT_BROKER, MQTT_PORT)

def send_zero():
    try:
        publish.single("host/0/data", payload="0", hostname=MQTT_BROKER, port=MQTT_PORT)
    except Exception:
        logging.exception("Failed to publish zero to %s:%s", MQTT_BROKER, MQTT_PORT)