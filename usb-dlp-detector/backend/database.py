import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dlp_detector.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usb_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            vendor TEXT,
            serial TEXT,
            connect_time DATETIME,
            mount_path TEXT,
            username TEXT,
            is_whitelisted INTEGER DEFAULT 0
        )
    ''')
    
    # Add new columns if they don't exist
    try: cursor.execute("ALTER TABLE usb_devices ADD COLUMN username TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE usb_devices ADD COLUMN is_whitelisted INTEGER DEFAULT 0")
    except: pass
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            extension TEXT,
            size INTEGER,
            source TEXT,
            destination TEXT,
            timestamp DATETIME,
            device_id TEXT,
            file_hash TEXT,
            speed_mbps REAL,
            username TEXT
        )
    ''')
    
    try: cursor.execute("ALTER TABLE file_activity ADD COLUMN file_hash TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE file_activity ADD COLUMN speed_mbps REAL")
    except: pass
    try: cursor.execute("ALTER TABLE file_activity ADD COLUMN username TEXT")
    except: pass
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            risk_score INTEGER,
            reason TEXT,
            timestamp DATETIME,
            severity TEXT,
            username TEXT,
            email_sent INTEGER DEFAULT 0
        )
    ''')
    
    try: cursor.execute("ALTER TABLE alerts ADD COLUMN severity TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE alerts ADD COLUMN username TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE alerts ADD COLUMN email_sent INTEGER DEFAULT 0")
    except: pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_trust (
            device_id TEXT PRIMARY KEY,
            first_seen DATETIME,
            trust_score INTEGER,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def execute_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    if fetch:
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
        
    conn.commit()
    lastrowid = cursor.lastrowid
    conn.close()
    return lastrowid
