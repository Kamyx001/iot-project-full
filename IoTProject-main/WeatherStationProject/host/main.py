#!/usr/bin/env python3

import os
from unittest import case

import RPi.GPIO as GPIO # type: ignore
from buzzer import turnOnAlarm, turnOffAlarm
import communication 
from sensors import getData
from lib.data import Data
import time
import json
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from display import initDisplay, updateDisplayReading

load_dotenv()
_running = True

SEND_INTERVAL = 10  # seconds
SETTINGS = "settings.json"
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))

def get_settings():
    with open(SETTINGS, "r") as f:
        load = json.load(f)
        return load["temp_min"], load["temp_max"], load["humid_min"], load["humid_max"]
def main():
    global _running
    communication.__init__()
    
    client = mqtt.Client()
    client.on_connect = communication.on_connect
    client.on_message = communication.on_message
    client.connect_async(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    initDisplay()
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
            # Check temperature first
            if data.cur_temp < data.min_temp or data.cur_temp > data.max_temp:
                # too cold or too hot
                updateDisplayReading(data.cur_temp, data.cur_humid, "RED")
                turnOnAlarm()

            # If temperature is okay, check humidity
            elif data.cur_humid < data.min_humid or data.cur_humid > data.max_humid:
                # too dry or too humid
                updateDisplayReading(data.cur_temp, data.cur_humid, "RED")
                turnOnAlarm()

            # Everything is within range
            else:
                updateDisplayReading(data.cur_temp, data.cur_humid, "GREEN")
                turnOffAlarm()
            # updateDisplayReading(data.cur_temp, data.cur_humid, "BLUE")
            if now - last_send_time >= SEND_INTERVAL:
                print(f"min_temp: {min_temp}, max_temp: {max_temp}, min_humid: {min_humid}, max_humid: {max_humid}")
                communication.send(data.to_json())
                last_send_time = now
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
