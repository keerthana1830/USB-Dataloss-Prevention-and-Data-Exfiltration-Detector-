import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np
import datetime
from .database import execute_query

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)

    def detect_anomaly(self, device_id, size_bytes, timestamp):
        dt = datetime.datetime.fromisoformat(timestamp)
        # using strftime to get the hour handles string dates better in Sqlite
        historical_data = execute_query('''
            SELECT size, strftime('%H', timestamp) as hour 
            FROM file_activity WHERE device_id = ?
        ''', (device_id,), fetch=True)
        
        if len(historical_data) > 20: 
            try:
                df = pd.DataFrame(historical_data)
                df['size'] = pd.to_numeric(df['size'], errors='coerce').fillna(0)
                df['hour'] = pd.to_numeric(df['hour'], errors='coerce').fillna(0) # fallbacks for safe parsing
                
                if df.empty or len(df) < 5: return False
                
                X_train = df[['size', 'hour']].values
                self.model.fit(X_train)
                
                X_test = np.array([[float(size_bytes), float(dt.hour)]])
                pred = self.model.predict(X_test)
                if pred[0] == -1:
                    return True
            except Exception as e:
                print(f"Error in ML anomaly detection: {e}")
        return False
