from pathlib import Path
from flask import jsonify, request
from backend.app import app
from backend.database import get_db
from backend.helpers import format_rpi

# ------------------ RPI Endpoints ------------------

@app.route('/api/rpis', methods=['GET'])
def get_rpis():
    rows = get_db().execute('SELECT * FROM rpi').fetchall()
    return jsonify([format_rpi(r) for r in rows])

@app.route('/api/rpis', methods=['POST'])
def create_rpi():
    data = request.json or {}
    db = get_db()
    cur = db.execute(
        'INSERT INTO rpi (name) VALUES (?)',
        (data.get('rpiName', 'Unnamed RPI'),)
    )
    db.commit()
    row = db.execute('SELECT * FROM rpi WHERE id = ?', (cur.lastrowid,)).fetchone()
    return jsonify(format_rpi(row)), 201

@app.route('/api/rpis/<int:id>', methods = ['GET'])
def get_rpi(id):
    row = get_db().execute('SELECT * FROM rpi WHERE id = ?', (id,)).fetchone()
    if not row:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(format_rpi(row))

@app.route('/api/rpis/<int:id>', methods=['PUT'])
def update_rpi(id):
    data = request.json or {}
    db = get_db()

    row = db.execute('SELECT * FROM rpi WHERE id = ?', (id,)).fetchone()
    if not row:
        return jsonify({'error': 'Not found'}), 404

    name = data.get('rpiName', row['name'])
    plant_id = data.get('plant', {}).get('id') if data.get('plant') else None

    db.execute(
        'UPDATE rpi SET name = ?, plant_id = ? WHERE id = ?',
        (name, plant_id, id)
    )
    db.commit()

    # If plant was assigned, send critical ranges to RPI via MQTT
    if plant_id:
        from backend.helpers import get_plant_by_id
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from communication import send_plant_ranges

        plant_data = get_plant_by_id(plant_id)
        if plant_data and plant_data.get('temperature') and plant_data.get('humidity'):
            send_plant_ranges(
                rpi_id=id,
                temp_min=plant_data['temperature']['critical']['min'],
                temp_max=plant_data['temperature']['critical']['max'],
                humid_min=plant_data['humidity']['critical']['min'],
                humid_max=plant_data['humidity']['critical']['max']
            )

    row = db.execute('SELECT * FROM rpi WHERE id = ?', (id,)).fetchone()
    return jsonify(format_rpi(row))

@app.route('/api/rpis/<int:id>',methods=['DELETE'])
def delete_rpi(id):
    db = get_db()
    row = db.execute('SELECT * FROM rpi WHERE id = ?', (id,)).fetchone()
    if not row:
        return jsonify({'error': 'Not found'}), 404

    # Delete associated readings first (due to foreign key)
    db.execute('DELETE FROM reading WHERE rpi_id = ?', (id,))
    # Delete the RPI
    db.execute('DELETE FROM rpi WHERE id = ?', (id,))
    db.commit()

    return jsonify({'success': True}), 200

@app.route('/api/rpis/readings', methods=['GET'])
def get_readings():
    rows = get_db().execute('SELECT id, curr_temp, curr_humid, status FROM rpi').fetchall()
    return jsonify([{
        'id': r['id'],
        'currTemperature': r['curr_temp'],
        'currHumidity': r['curr_humid'],
        'connectionStatus': r['status']
    } for r in rows])

@app.route('/api/rpis/<int:id>/history', methods=['GET'])
def get_history(id):
    rows = get_db().execute(
        'SELECT timestamp, temperature, humidity FROM reading WHERE rpi_id = ? ORDER BY timestamp LIMIT 1000',
        (id,)
    ).fetchall()
    return jsonify({
        'measurements': [{
            'timestamp': r['timestamp'],
            'temperature': r['temperature'],
            'humidity': r['humidity']
        } for r in rows]
    })
