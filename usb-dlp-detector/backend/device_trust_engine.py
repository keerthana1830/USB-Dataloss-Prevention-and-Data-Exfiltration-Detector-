import datetime
from .database import execute_query

class DeviceTrustEngine:
    def __init__(self):
        pass

    def evaluate_device(self, device_id):
        # check if in device_trust
        trust = execute_query('SELECT * FROM device_trust WHERE device_id = ?', (device_id,), fetch=True)
        
        score = 0
        status = "Unknown"
        
        if not trust:
            # First time connection
            score = -20
            status = "New"
            execute_query('INSERT INTO device_trust (device_id, first_seen, trust_score, status) VALUES (?, ?, ?, ?)',
                          (device_id, datetime.datetime.now().isoformat(), score, status))
        else:
            trust_record = trust[0]
            if trust_record['status'] == 'Trusted':
                score = 50
            elif trust_record['status'] == 'Known':
                score = 20
            else:
                score = trust_record['trust_score'] # previous score

        return score, status

    def update_trust(self, device_id, new_status, new_score):
        execute_query('UPDATE device_trust SET status = ?, trust_score = ? WHERE device_id = ?',
                      (new_status, new_score, device_id))
