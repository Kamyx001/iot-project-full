"""
MQTT message handler - called by communication.py when sensor data arrives.
Stores data in the database without needing Flask request context.
"""
import re
import json
import time
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'greenhouse.db'
TOPIC_PATTERN = re.compile(r'^host/(\d+)/data$')


def init_db():
    """Initialize the database if it doesn't exist."""
    db = sqlite3.connect(DB_PATH)
    db.executescript('''
        CREATE TABLE IF NOT EXISTS rpi (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL DEFAULT 'Unnamed RPI',
            plant_id TEXT,
            curr_temp REAL,
            curr_humid REAL,
            status TEXT DEFAULT 'disconnected',
            last_seen INTEGER
        );

        CREATE TABLE IF NOT EXISTS reading (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rpi_id INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            FOREIGN KEY (rpi_id) REFERENCES rpi(id)
        );

        CREATE INDEX IF NOT EXISTS idx_reading_rpi_time ON reading(rpi_id, timestamp);
    ''')
    db.commit()
    db.close()


def handle_sensor_data(topic: str, payload: str) -> bool:
    """
    Process incoming MQTT sensor data and store in database.

    Args:
        topic: MQTT topic (e.g., "host/1/data")
        payload: JSON string with cur_temp and cur_humid

    Returns:
        True if data was stored successfully, False otherwise
    """
    # Parse topic to get RPI ID
    match = TOPIC_PATTERN.match(topic)
    if not match:
        return False

    rpi_id = int(match.group(1))

    # Parse payload
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return False

    temp = data.get('cur_temp')
    humid = data.get('cur_humid')

    if temp is None or humid is None:
        return False

    # Store in database
    now = int(time.time() * 1000)
    db = sqlite3.connect(DB_PATH)

    try:
        # Upsert RPI
        db.execute('''
            INSERT INTO rpi (id, curr_temp, curr_humid, status, last_seen)
            VALUES (?, ?, ?, 'connected', ?)
            ON CONFLICT(id) DO UPDATE SET
                curr_temp = excluded.curr_temp,
                curr_humid = excluded.curr_humid,
                status = 'connected',
                last_seen = excluded.last_seen
        ''', (rpi_id, temp, humid, now))

        # Store reading
        db.execute(
            'INSERT INTO reading (rpi_id, timestamp, temperature, humidity) VALUES (?, ?, ?, ?)',
            (rpi_id, now, temp, humid)
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error storing sensor data: {e}")
        return False
    finally:
        db.close()


def mark_disconnected(rpi_id: int):
    """Mark an RPI as disconnected."""
    db = sqlite3.connect(DB_PATH)
    try:
        db.execute(
            'UPDATE rpi SET status = ?, curr_temp = NULL, curr_humid = NULL WHERE id = ?',
            ('disconnected', rpi_id)
        )
        db.commit()
    finally:
        db.close()


def check_stale_rpis(timeout_ms: int = 30000):
    """Mark RPIs as disconnected if no data received within timeout."""
    threshold = int(time.time() * 1000) - timeout_ms
    db = sqlite3.connect(DB_PATH)
    try:
        db.execute('''
            UPDATE rpi
            SET status = 'disconnected', curr_temp = NULL, curr_humid = NULL
            WHERE status = 'connected' AND last_seen < ?
        ''', (threshold,))
        db.commit()
    finally:
        db.close()
