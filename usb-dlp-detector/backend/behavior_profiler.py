import datetime
from .database import execute_query

class BehaviorProfiler:
    def __init__(self):
        pass

    def evaluate_behavior(self, device_id, size_bytes):
        historical = execute_query('SELECT AVG(size) as avg_size, COUNT(*) as count FROM file_activity WHERE device_id = ?', (device_id,), fetch=True)
        
        score_penalty = 0
        reasons = []

        if historical and len(historical) > 0 and historical[0]['count'] > 10:
            avg_size = historical[0]['avg_size']
            if avg_size and size_bytes > avg_size * 5: # 5x times larger than baseline
                score_penalty += 15
                reasons.append(f"Unusual file size behavior (avg: {avg_size/1024:.1f}KB, this: {size_bytes/1024:.1f}KB)")
                
        return score_penalty, reasons
