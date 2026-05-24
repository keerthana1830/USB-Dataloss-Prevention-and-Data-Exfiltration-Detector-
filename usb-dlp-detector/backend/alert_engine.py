import datetime
from .database import execute_query
from .email_notifier import EmailNotifier

# Global socketio instance (will be set by main.py)
socketio_instance = None

def set_socketio(socketio):
    """Set the SocketIO instance for real-time alerts"""
    global socketio_instance
    socketio_instance = socketio

class AlertEngine:
    def __init__(self):
        self.email_notifier = EmailNotifier()

    def generate_alert(self, device_id, file_name, risk_score, reason, severity="High", username="Unknown"):
        timestamp = datetime.datetime.now().isoformat()
        
        # Insert alert into database
        alert_id = execute_query('''
            INSERT INTO alerts (device_id, risk_score, reason, timestamp, severity, username, email_sent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (device_id, risk_score, f"{reason} [File: {file_name}]", timestamp, severity, username, 0))
        
        print(f"[{severity.upper()}] ALERT: Risk Score {risk_score} | User: {username} | Reason: {reason}")
        
        # Send email notification for high-risk alerts
        email_sent = False
        if risk_score >= 70:  # High threshold
            email_sent = self.email_notifier.send_alert_email(
                device_id, file_name, risk_score, reason, severity, username
            )
            
            if email_sent:
                # Update database to mark email as sent
                execute_query('''
                    UPDATE alerts SET email_sent = 1 WHERE id = ?
                ''', (alert_id,))
        
        # Emit WebSocket event for real-time dashboard updates
        if socketio_instance:
            try:
                alert_data = {
                    'id': alert_id,
                    'device_id': device_id,
                    'file_name': file_name,
                    'risk_score': risk_score,
                    'reason': reason,
                    'severity': severity,
                    'username': username,
                    'timestamp': timestamp,
                    'email_sent': email_sent
                }
                socketio_instance.emit('new_alert', alert_data, namespace='/')
                print(f"[WEBSOCKET] Alert broadcasted to dashboard")
            except Exception as e:
                print(f"[WEBSOCKET] Failed to emit alert: {e}")
