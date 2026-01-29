from flask import send_from_directory
from backend.app import app

# ------------------ Frontend ------------------

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/assets/<path:path>', methods=['GET'])
def serve_assets(path):
    return send_from_directory(f'{app.static_folder}/assets', path)
