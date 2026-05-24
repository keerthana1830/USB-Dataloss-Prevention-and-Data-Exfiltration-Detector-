import datetime
from .database import execute_query
from .alert_engine import AlertEngine
from .device_trust_engine import DeviceTrustEngine
from .sensitivity_scanner import SensitivityScanner
from .honeypot_monitor import HoneypotMonitor
from .behavior_profiler import BehaviorProfiler
from .anomaly_detector import AnomalyDetector
from .whitelist_manager import WhitelistManager

class RiskEngine:
    def __init__(self):
        self.alert_engine = AlertEngine()
        self.trust_engine = DeviceTrustEngine()
        self.scanner = SensitivityScanner()
        self.honeypot = HoneypotMonitor()
        self.profiler = BehaviorProfiler()
        self.anomaly_detector = AnomalyDetector()
        self.whitelist_manager = WhitelistManager()
        
        self.sensitive_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.ppt', '.pptx', '.sql', '.pem', '.key', '.zip']
        self.bulk_time_window = 60 # seconds
        self.bulk_threshold = 20 # files
        self.high_risk_threshold = 60
        self.critical_risk_threshold = 100

    def evaluate_risk(self, device_id, file_path, file_name, extension, size_bytes, file_hash, speed_mbps, timestamp, username="Unknown", is_whitelisted=False):
        score = 0
        reasons = []

        # Whitelist penalty - add risk if device is NOT whitelisted
        if not is_whitelisted:
            whitelist_penalty = self.whitelist_manager.get_unknown_device_penalty()
            score += whitelist_penalty
            reasons.append(f"Unknown/Non-whitelisted device (+{whitelist_penalty})")

        if self.honeypot.is_honeypot(file_name):
            score += 150
            reasons.append("HONEYPOT FILE EXFILTRATED")

        sensitive_keywords = self.scanner.scan_file(file_path, extension)
        if sensitive_keywords:
            score += 40
            reasons.append(f"Sensitive keywords found ({','.join(sensitive_keywords)})")

        if speed_mbps > 500:
            score += 30
            reasons.append(f"Unusually fast speed ({speed_mbps:.1f} MB/s)")
            
        if file_hash != "Unknown":
            hash_count = execute_query('SELECT COUNT(*) as c FROM file_activity WHERE file_hash = ? AND device_id = ?', (file_hash, device_id), fetch=True)
            if hash_count and hash_count[0]['c'] > 3:
                score += 20
                reasons.append("Repeated copying identical file")

        if size_bytes > 100 * 1024 * 1024:
            score += 30
            reasons.append("Large file transfer (>100MB)")

        if extension.lower() in self.sensitive_extensions:
            score += 20
            reasons.append(f"Sensitive file format ({extension})")

        dt = datetime.datetime.fromisoformat(timestamp)
        if dt.hour < 9 or dt.hour >= 18:
            score += 20
            reasons.append("Outside business hours")

        trust_score, trust_status = self.trust_engine.evaluate_device(device_id)
        if trust_score < 0:
            score += abs(trust_score)
            reasons.append(f"Untrusted USB device ({trust_status})")
        else:
            score -= trust_score 
        
        penalty, b_reasons = self.profiler.evaluate_behavior(device_id, size_bytes)
        if penalty > 0:
            score += penalty
            reasons.extend(b_reasons)

        time_limit = (dt - datetime.timedelta(seconds=self.bulk_time_window)).isoformat()
        recent_files = execute_query('SELECT count(*) as count FROM file_activity WHERE device_id = ? AND timestamp >= ?', (device_id, time_limit), fetch=True)
        if recent_files and recent_files[0]['count'] > self.bulk_threshold:
            score += 40
            reasons.append("Bulk file transfer ongoing")

        if self.anomaly_detector.detect_anomaly(device_id, size_bytes, timestamp):
            score += 30
            reasons.append("ML Anomaly Detected")

        if score < 0: score = 0 

        if score > self.critical_risk_threshold:
            self.alert_engine.generate_alert(device_id, file_name, score, ", ".join(reasons), severity="Critical", username=username)
        elif score > self.high_risk_threshold:
            self.alert_engine.generate_alert(device_id, file_name, score, ", ".join(reasons), severity="High", username=username)
        elif score > 20: 
            self.alert_engine.generate_alert(device_id, file_name, score, ", ".join(reasons), severity="Medium", username=username)
