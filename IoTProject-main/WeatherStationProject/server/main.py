#!/usr/bin/env python3

import os
import time
import signal
import sys
import logging
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import communication
import json

from backend.mqtt_handler import init_db, check_stale_rpis
from backend.app import app as flask_app

_running = True

def run_flask():
    """Run Flask server in a separate thread."""
    flask_app.run(host='0.0.0.0', port=4000, debug=False, use_reloader=False)

def main():
    global _running
    logging.basicConfig(level=logging.INFO)

    # Initialize backend database
    init_db()

    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask server started on http://0.0.0.0:4000")

    # Start MQTT client
    communication.send_zero()
    from paho.mqtt.enums import CallbackAPIVersion
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.on_connect = communication.on_connect
    client.on_message = communication.on_message
    client.connect_async(communication.MQTT_BROKER, communication.MQTT_PORT)
    client.loop_start()
    print("MQTT client connected. Server is running. Press Ctrl+C to exit.")

    last_settings = time.time()
    last_stale_check = time.time()

    try:
        while _running:
            now = time.time()

            # Check for stale RPIs every 10 seconds
            if now - last_stale_check >= 10:
                last_stale_check = now
                check_stale_rpis(timeout_ms=30000)

            time.sleep(1)
    finally:
        client.loop_stop()
        client.disconnect()
        print("Server stopped.")

if __name__ == "__main__":
    main()