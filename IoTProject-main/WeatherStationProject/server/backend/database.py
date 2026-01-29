import sqlite3
from flask import g

# Late import to avoid circular dependency
def _get_app_config():
    from backend.app import app, DB_PATH
    return app, DB_PATH

def get_db():
    app, DB_PATH = _get_app_config()
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(exception):
    db = g.pop('db', None)
    if db:
        db.close()

def init_db():
    app, DB_PATH = _get_app_config()
    app.teardown_appcontext(close_db)

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
