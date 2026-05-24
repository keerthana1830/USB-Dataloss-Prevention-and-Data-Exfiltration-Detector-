import threading
import time
from backend.database import init_db
from backend.usb_monitor import USBMonitor
from backend.file_monitor import FileMonitor
from dashboard.app import app, socketio

def start_dashboard():
    # Run the flask app with socketio
    socketio.run(app, debug=False, port=5000, host='0.0.0.0', use_reloader=False)

def main():
    print("=" * 60)
    print("USB Data Loss Prevention Detector")
    print("=" * 60)
    print("Initializing Database...")
    init_db()
    
    file_monitor = FileMonitor()
    
    def on_usb_connected(mount_path, device_id, username="Unknown", is_whitelisted=False):
        # Start file monitoring for this device
        file_monitor.start_monitoring(mount_path, device_id, username, is_whitelisted)
        
    usb_monitor = USBMonitor(callback=on_usb_connected)
    
    # Start web dashboard in a separate thread
    print("Starting Web Dashboard on port 5000...")
    print("Dashboard URL: http://localhost:5000")
    print("Export CSV: http://localhost:5000/export/csv")
    print("Export PDF: http://localhost:5000/export/pdf")
    print("-" * 60)
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Give dashboard time to start
    time.sleep(2)
    
    try:
        # Start USB monitoring (blocking)
        print("Starting USB Device Monitoring...")
        print("Whitelist checking enabled")
        print("Email notifications configured (check config.py)")
        print("Real-time WebSocket alerts enabled")
        print("=" * 60)
        usb_monitor.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        file_monitor.stop_all()
        print("Goodbye.")

if __name__ == "__main__":
    main()
