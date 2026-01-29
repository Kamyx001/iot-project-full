import os
from pathlib import Path
from flask import Flask

app = Flask(__name__, static_folder='./static')

DB_PATH = Path(__file__).parent / 'greenhouse.db'
TREFLE_TOKEN = os.environ.get('TREFLE_TOKEN')

# Import modules to register routes (after app is created)
from backend.database import init_db, get_db, close_db
from backend.endpoints import *
from backend.frontend import *
from backend.trefle import *
from backend.data_ingestion import *

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=4000, debug=True)
