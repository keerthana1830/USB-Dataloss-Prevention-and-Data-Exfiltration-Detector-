import os
import time
import datetime
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .database import execute_query
from .risk_engine import RiskEngine
from .user_utils import get_current_username

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        return "Unknown"

class USBEventHandler(FileSystemEventHandler):
    def __init__(self, mount_path, device_id, username, is_whitelisted):
        self.mount_path = mount_path
        self.device_id = device_id
        self.username = username
        self.is_whitelisted = is_whitelisted
        self.risk_engine = RiskEngine()
        self.copy_start_times = {}

    def on_created(self, event):
        if not event.is_directory:
            self.copy_start_times[event.src_path] = time.time()
            self.process_file(event.src_path)

    def process_file(self, file_path):
        time.sleep(0.5) # Allow file write to complete
        
        if not os.path.exists(file_path):
            return
            
        file_name = os.path.basename(file_path)
        _, extension = os.path.splitext(file_name)
        
        try:
            size_bytes = os.path.getsize(file_path)
            file_hash = calculate_sha256(file_path)
        except:
            size_bytes = 0
            file_hash = "Unknown"
            
        timestamp = datetime.datetime.now().isoformat()
        source_path = "LocalDisk -> USB"
        
        speed_mbps = 0.0
        if file_path in self.copy_start_times:
            duration = time.time() - self.copy_start_times[file_path]
            if duration > 0.1:
                speed_mbps = (size_bytes / (1024 * 1024)) / duration
            del self.copy_start_times[file_path]
            
        execute_query('''
            INSERT INTO file_activity (file_name, extension, size, source, destination, timestamp, device_id, file_hash, speed_mbps, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_name, extension, size_bytes, source_path, file_path, timestamp, self.device_id, file_hash, speed_mbps, self.username))
        
        if file_hash != "Unknown":
            print(f"[+] File Transferred: {file_name} ({size_bytes} bytes) | User: {self.username} | Hash: {file_hash[:8]} | Speed: {speed_mbps:.1f}MB/s")
        
        if file_hash != "Unknown":
            self.risk_engine.evaluate_risk(
                self.device_id, file_path, file_name, extension, size_bytes, 
                file_hash, speed_mbps, timestamp, self.username, self.is_whitelisted
            )

class FileMonitor:
    def __init__(self):
        self.observers = []

    def start_monitoring(self, mount_path, device_id, username="Unknown", is_whitelisted=False):
        event_handler = USBEventHandler(mount_path, device_id, username, is_whitelisted)
        observer = Observer()
        observer.schedule(event_handler, mount_path, recursive=True)
        observer.start()
        self.observers.append(observer)
        print(f"[*] Started monitoring files on: {mount_path} for user: {username}")

    def stop_all(self):
        for observer in self.observers:
            observer.stop()
        for observer in self.observers:
            observer.join()
