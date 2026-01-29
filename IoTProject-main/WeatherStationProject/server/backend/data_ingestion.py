import time
from flask import jsonify, request
from backend.app import app
from backend.database import get_db

# ------------------ Data Ingestion (for MQTT later) ------------------

@app.route('/api/rpis/<int:id>/data', methods=['POST'])
def post_sensor_data(id):
    """Endpoint for RPIs to post sensor data (alternative to MQTT)"""
    data = request.json or {}
    temp = data.get('cur_temp')
    humid = data.get('cur_humid')

    if temp is None or humid is None:
        return jsonify({'error': 'Missing cur_temp or cur_humid'}), 400

    db = get_db()
    now = int(time.time() * 1000)

    # Upsert RPI
    db.execute('''
        INSERT INTO rpi (id, curr_temp, curr_humid, status, last_seen)
        VALUES (?, ?, ?, 'connected', ?)
        ON CONFLICT(id) DO UPDATE SET
            curr_temp = excluded.curr_temp,
            curr_humid = excluded.curr_humid,
            status = 'connected',
            last_seen = excluded.last_seen
    ''', (id, temp, humid, now))

    # Store reading
    db.execute(
        'INSERT INTO reading (rpi_id, timestamp, temperature, humidity) VALUES (?, ?, ?, ?)',
        (id, now, temp, humid)
    )
    db.commit()

    return jsonify({'status': 'ok'})
