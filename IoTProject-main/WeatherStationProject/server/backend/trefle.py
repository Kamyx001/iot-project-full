import requests
from pathlib import Path
from flask import jsonify, request
from backend.app import app

# ------------------ Plants (Trefle API) ------------------

TREFLE_BASE = 'https://trefle.io/api/v1'
TOKEN_FILE = Path(__file__).parent / '.trefle_token'

def get_token():
    """Get token from file or environment"""
    import os
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return os.environ.get('TREFLE_TOKEN')

def save_token(token):
    """Save token to file"""
    TOKEN_FILE.write_text(token)

@app.route('/api/plants', methods=['GET'])
def search_plants():
    q = request.args.get('q', '')
    token = get_token()

    if not token:
        return jsonify({'error': 'api_key_required'}), 401

    if not q:
        return jsonify([])

    try:
        resp = requests.get(
            f'{TREFLE_BASE}/plants/search',
            params={'q': q, 'token': token},
            timeout=5
        )

        if resp.status_code == 401:
            return jsonify({'error': 'api_key_invalid'}), 401

        resp.raise_for_status()
        data = resp.json().get('data', [])

        # Transform to frontend format
        plants = []
        for p in data[:10]:
            plants.append({
                'id': str(p.get('id')),
                'commonName': p.get('common_name') or p.get('scientific_name'),
                'scientificName': p.get('scientific_name'),
                'imageUrl': p.get('image_url') or '',
                'temperature': {
                    'warning': {'min': 15, 'max': 25},
                    'critical': {'min': 5, 'max': 35}
                },
                'humidity': {
                    'warning': {'min': 40, 'max': 70},
                    'critical': {'min': 20, 'max': 90}
                }
            })
        return jsonify(plants)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return jsonify({'error': 'api_key_invalid'}), 401
        print(f'Trefle API error: {e}')
        return jsonify([])
    except Exception as e:
        print(f'Trefle API error: {e}')
        return jsonify([])

@app.route('/api/settings/trefle-token', methods=['POST'])
def set_trefle_token():
    data = request.json or {}
    token = data.get('token', '').strip()

    if not token:
        return jsonify({'error': 'Token required'}), 400

    # Validate token by making a test request
    try:
        resp = requests.get(
            f'{TREFLE_BASE}/plants',
            params={'token': token},
            timeout=5
        )
        if resp.status_code == 401:
            return jsonify({'error': 'Invalid token'}), 401
        resp.raise_for_status()
    except Exception as e:
        return jsonify({'error': f'Token validation failed: {e}'}), 400

    save_token(token)
    return jsonify({'status': 'ok'})

@app.route('/api/settings/trefle-token',methods=['GET'])
def check_trefle_token():
    token = get_token()
    return jsonify({'configured': bool(token)})
