import logging
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import os
import json
from dotenv import load_dotenv, set_key
import tempfile
import io

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
id = os.getenv("HOST_ID")
TOPIC_DATA = "host/test"
TOPIC_CONFIG = ""
SETTINGS = "settings.json"
id_present = False

def send(message: str):
    try:
        publish.single(topic=TOPIC_DATA, payload=message, hostname=MQTT_BROKER, port=MQTT_PORT)
        logging.info(f"Sent message to {TOPIC_DATA}: {message}")
    except Exception as e:
        logging.error(f"Failed to send message: {e}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    try:
        parsed = json.loads(payload)
    except Exception as e:
        logging.error(f"Received invalid JSON on {msg.topic}: {e}")
        return

    # Write to a temp file in the same directory, fsync, then atomically replace
    dirpath = os.path.dirname(os.path.abspath(SETTINGS)) or "."
    fd, tmp_path = tempfile.mkstemp(prefix="settings_", dir=dirpath, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
            tmpf.write(json.dumps(parsed, indent=2))
            tmpf.flush()
            os.fsync(tmpf.fileno())
        os.replace(tmp_path, SETTINGS)
        logging.info(f"Received new settings on {msg.topic}: {payload}")
    except Exception as e:
        logging.error(f"Failed to write settings atomically: {e}")
        try:
            os.remove(tmp_path)
        except Exception:
            pass

def get_id(client,userdata,msg):
    global id
    print (f"Received ID assignment message on {msg.topic}")
    _, id = str(max(int(msg.topic.split("/", 1))), int(id))

def on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe(TOPIC_CONFIG)

def get_id_connect(client, userdata, flags, reason_code, properties=None):
    global id_present
    print("Subscribed to host/# for ID assignment")
    client.subscribe("host/#")
    print("Subscribed to host/# for ID assignment")
    id_present = True

def __init__():
    global id, TOPIC_DATA, TOPIC_CONFIG, id_present
    client = mqtt.Client()
    if not id:
        id = "0"
        client.on_message = get_id
        client.on_connect = get_id_connect
        client.reconnect_delay_set(min_delay=1, max_delay=2)
        client.connect_async(MQTT_BROKER, MQTT_PORT, 60)
        print(f"{MQTT_BROKER, MQTT_PORT}")
        client.loop_start()
        while not id_present:
            time.sleep(1)
        
        time.sleep(2)
        client.loop_stop()
        client.disconnect()
        id = str(int(id) + 1)
        set_key(".env", "HOST_ID", id)
        publish.single(
            topic=f"host/{id}/config",
            payload=json.dumps({"min_temp": 15.0, "max_temp": 25.0}),
            hostname=MQTT_BROKER,
            port=MQTT_PORT
        )   
    TOPIC_DATA = f"host/{id}/data"
    TOPIC_CONFIG = f"host/{id}/config"


def get_topics():
    return TOPIC_DATA, TOPIC_CONFIG