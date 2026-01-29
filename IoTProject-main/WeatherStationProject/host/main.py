#!/usr/bin/env python3

import os

#import RPi.GPIO as GPIO # type: ignore
import communication 
from simulation import getData
from lib.data import Data
import time
import json
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv
#from display import initDisplay, updateDisplayReading

load_dotenv()
_running = True

SEND_INTERVAL = 10  # seconds
SETTINGS = "settings.json"
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))

def get_settings():
    with open(SETTINGS, "r") as f:
        load = json.load(f)
        return load["min_temp"], load["max_temp"], load["min_humid"], load["max_humid"]
def main():
    global _running
    communication.__init__()
    
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.on_connect = communication.on_connect
    client.on_message = communication.on_message
    client.connect_async(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    #initDisplay()
    topic_data, topic_config = communication.get_topics()
    host_id = os.getenv("HOST_ID")
    min_temp, max_temp, min_humid, max_humid = get_settings()
    data = Data(
        cur_temp=0.0,
        cur_humid=0.0,
        min_temp=min_temp,
        max_temp=max_temp,
        min_humid=min_humid,
        max_humid=max_humid
    )
    last_send_time = time.time()
    try:
        while _running:
            min_temp, max_temp, min_humid, max_humid = get_settings()
            data.set_settings(min_temp, max_temp, min_humid, max_humid)
            data_values = getData()
            data.set_values(data_values[0], data_values[1])
            now = time.time()
            #updateDisplayReading(data.cur_temp, data.cur_humid, "BLUE")
            if now - last_send_time >= SEND_INTERVAL:
                print(f"min_temp: {min_temp}, max_temp: {max_temp}, min_humid: {min_humid}, max_humid: {max_humid}")
                communication.send(data.to_json())
                last_send_time = now
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
