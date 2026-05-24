from flask import Flask, render_template, jsonify, send_file, Response, request
from flask_socketio import SocketIO
import sys
import os
import csv
import io
import hashlib
import secrets
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import execute_query
from backend import alert_engine

app = Flask(__name__)
# SECURITY FIX: Use a proper random secret key instead of hardcoded string
app.config['SECRET_KEY'] = os.environ.get('DLP_SECRET_KEY', secrets.token_hex(32))
socketio = SocketIO(app, cors_allowed_origins="*")

# Set the socketio instance in alert_engine for real-time alerts
alert_engine.set_socketio(socketio)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    try:
        connections = execute_query('SELECT COUNT(*) as c FROM usb_devices', fetch=True)[0]['c']
        files_transferred = execute_query('SELECT COUNT(*) as c FROM file_activity', fetch=True)[0]['c']
        total_alerts = execute_query('SELECT COUNT(*) as c FROM alerts', fetch=True)[0]['c']
    except Exception:
        connections = files_transferred = total_alerts = 0
    return jsonify({
        "usb_connections": connections,
        "files_transferred": files_transferred,
        "total_alerts": total_alerts
    })

@app.route('/api/usb_devices')
def get_usb_devices():
    devices = execute_query('SELECT * FROM usb_devices ORDER BY connect_time DESC LIMIT 25', fetch=True)
    return jsonify(devices)

@app.route('/api/device_trust')
def get_device_trust():
    trusts = execute_query('SELECT * FROM device_trust ORDER BY first_seen DESC', fetch=True)
    return jsonify(trusts)

@app.route('/api/file_activity')
def get_file_activity():
    activity = execute_query('SELECT * FROM file_activity ORDER BY timestamp DESC LIMIT 30', fetch=True)
    return jsonify(activity)

@app.route('/api/alerts')
def get_alerts():
    alerts = execute_query('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 25', fetch=True)
    return jsonify(alerts)

@app.route('/api/chart_data')
def get_chart_data():
    files_per_day = execute_query('''
        SELECT date(timestamp) as date, COUNT(*) as count 
        FROM file_activity GROUP BY date(timestamp) ORDER BY date DESC LIMIT 7
    ''', fetch=True)
    
    alerts_per_day = execute_query('''
        SELECT date(timestamp) as date, COUNT(*) as count 
        FROM alerts GROUP BY date(timestamp) ORDER BY date DESC LIMIT 7
    ''', fetch=True)
    
    risk_scores = execute_query('SELECT risk_score FROM alerts', fetch=True)
    
    return jsonify({
        "files_per_day": files_per_day,
        "alerts_per_day": alerts_per_day,
        "risk_scores": [r['risk_score'] for r in risk_scores]
    })

@app.route('/api/heatmap_data')
def get_heatmap():
    res = execute_query('''
        SELECT strftime('%H', timestamp) as hour, AVG(risk_score) as avg_risk
        FROM alerts GROUP BY hour ORDER BY hour
    ''', fetch=True)
    return jsonify(res)

@app.route('/api/timeline')
def get_timeline():
    files = execute_query("SELECT 'Activity' as type, timestamp, file_name as detail, 0 as risk_score FROM file_activity ORDER BY timestamp DESC LIMIT 30", fetch=True)
    alerts = execute_query("SELECT 'Alert' as type, timestamp, reason as detail, risk_score FROM alerts ORDER BY timestamp DESC LIMIT 30", fetch=True)
    events = files + alerts
    events.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(events[:40])


# ──────────────────────────────────────────────
# SIMULATE ATTACK (Demo endpoint for testing)
# ──────────────────────────────────────────────
@app.route('/api/simulate', methods=['POST'])
def simulate_attack():
    """
    Injects realistic simulated attack data into the database.
    Perfect for demos & presentations. No actual USB required.
    
    'I'm in' - every pentester ever
    """
    try:
        now = datetime.now()
        
        # Simulated attacker profiles
        attackers = ['r.hacker', 'j.disgruntled', 'suspicious.intern', 'ex.employee']
        devices = [
            ('USBSTOR\\DISK&VEN_SANDISK&PROD_ULTRA&REV_1.00', 'SanDisk', 'A1B2C3'),
            ('USBSTOR\\DISK&VEN_KINGSTON&PROD_DT&REV_PMAP', 'Kingston', 'X9Y8Z7'),
            ('USBSTOR\\DISK&VEN_UNKNOWN&PROD_FLASH&REV_2.0', 'Unknown_Vendor', 'DEADBEEF'),
        ]
        
        # Pick random attacker and device
        attacker = random.choice(attackers)
        dev_id, vendor, serial = random.choice(devices)
        
        # 1. Insert USB connection
        connect_time = (now - timedelta(minutes=random.randint(1, 30))).isoformat()
        execute_query('''
            INSERT INTO usb_devices (device_id, vendor, serial, connect_time, mount_path, username, is_whitelisted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (dev_id, vendor, serial, connect_time, 'E:\\', attacker, 0))
        
        # 2. Insert device trust (untrusted)
        existing = execute_query('SELECT * FROM device_trust WHERE device_id = ?', (dev_id,), fetch=True)
        if not existing:
            execute_query('INSERT INTO device_trust (device_id, first_seen, trust_score, status) VALUES (?, ?, ?, ?)',
                          (dev_id, connect_time, -20, 'New'))
        
        # 3. Simulate file transfers with suspicious patterns
        sim_files = [
            ('salary_2025.xlsx', '.xlsx', 2048000, 'HONEYPOT FILE EXFILTRATED'),
            ('passwords.txt', '.txt', 512, 'Sensitive keywords found (password, secret)'),
            ('customer_database.csv', '.csv', 15728640, 'HONEYPOT FILE EXFILTRATED, Large file transfer'),
            ('quarterly_financials.pdf', '.pdf', 8388608, 'Sensitive file format (.pdf), Outside business hours'),
            ('source_code_backup.zip', '.zip', 104857600, 'Large file transfer (>100MB), Sensitive file format (.zip)'),
            ('employee_ssn_list.docx', '.docx', 1048576, 'Sensitive keywords found (confidential, salary)'),
        ]
        
        alert_id = None
        for fname, ext, size, reason in sim_files:
            file_hash = hashlib.sha256(f"{fname}{now.isoformat()}{random.random()}".encode()).hexdigest()
            ts = (now - timedelta(seconds=random.randint(5, 300))).isoformat()
            speed = round(random.uniform(10, 500), 2)
            
            execute_query('''
                INSERT INTO file_activity (file_name, extension, size, source, destination, timestamp, device_id, file_hash, speed_mbps, username)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (fname, ext, size, 'LocalDisk -> USB', f'E:\\{fname}', ts, dev_id, file_hash, speed, attacker))
        
        # 4. Generate alerts of various severities
        alert_scenarios = [
            (150, 'Critical', 'HONEYPOT FILE EXFILTRATED, Unknown/Non-whitelisted device (+30), Sensitive keywords found (salary), Outside business hours'),
            (95, 'Critical', 'Large file transfer (>100MB), Bulk file transfer ongoing, Unknown/Non-whitelisted device (+30), ML Anomaly Detected'),
            (72, 'High', 'Sensitive file format (.pdf), Unknown/Non-whitelisted device (+30), Outside business hours, Unusual file size behavior'),
            (45, 'Medium', 'Sensitive file format (.zip), Unknown/Non-whitelisted device (+30)'),
            (35, 'Medium', 'Sensitive keywords found (password, secret), Unusual file size behavior'),
        ]
        
        for risk_score, severity, reason in alert_scenarios:
            ts = (now - timedelta(seconds=random.randint(1, 600))).isoformat()
            fname = random.choice([f[0] for f in sim_files])
            
            alert_id = execute_query('''
                INSERT INTO alerts (device_id, risk_score, reason, timestamp, severity, username, email_sent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (dev_id, risk_score, f"{reason} [File: {fname}]", ts, severity, attacker, 0))
            
            # Emit WebSocket alert for real-time toast notification
            if alert_engine.socketio_instance:
                try:
                    alert_engine.socketio_instance.emit('new_alert', {
                        'id': alert_id,
                        'device_id': dev_id,
                        'file_name': fname,
                        'risk_score': risk_score,
                        'reason': reason,
                        'severity': severity,
                        'username': attacker,
                        'timestamp': ts,
                        'email_sent': False
                    }, namespace='/')
                except Exception:
                    pass
        
        return jsonify({
            'status': 'ok',
            'message': f'Simulated {len(alert_scenarios)} alerts from attacker "{attacker}" using device {vendor}',
            'attacker': attacker,
            'device': vendor,
            'alerts_created': len(alert_scenarios),
            'files_simulated': len(sim_files)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print('[WEBSOCKET] Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('[WEBSOCKET] Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
