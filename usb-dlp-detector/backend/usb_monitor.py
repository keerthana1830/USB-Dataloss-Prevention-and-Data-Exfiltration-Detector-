import time
import os
import platform
import datetime
from .database import execute_query
from .device_trust_engine import DeviceTrustEngine
from .whitelist_manager import WhitelistManager
from .user_utils import get_current_username

class USBMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.connected_devices = set()
        self.trust_engine = DeviceTrustEngine()
        self.whitelist_manager = WhitelistManager()

    def start(self):
        if platform.system() == "Windows":
            self.monitor_windows()
        else:
            self.monitor_linux()

    def monitor_windows(self):
        import wmi
        c = wmi.WMI()
        print("[*] Starting USB Monitor (Windows)...")
        while True:
            current_devices = set()
            for physical_disk in c.Win32_DiskDrive():
                if physical_disk.InterfaceType == "USB":
                    device_id = physical_disk.DeviceID
                    current_devices.add(device_id)
                    
                    if device_id not in self.connected_devices:
                        self.connected_devices.add(device_id)
                        
                        mount_path = "Unknown"
                        for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
                            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                                mount_path = logical_disk.DeviceID + "\\"
                        
                        clean_device_id = str(physical_disk.PNPDeviceID) or "Unknown_PNP"
                        vendor = str(physical_disk.Manufacturer) or "Unknown"
                        serial = str(physical_disk.SerialNumber) or "Unknown"
                        
                        # Get current username
                        username = get_current_username()
                        
                        # Check whitelist
                        is_whitelisted, whitelist_info = self.whitelist_manager.is_whitelisted(vendor, serial)
                        
                        device_info = {
                            "device_id": clean_device_id,
                            "vendor": vendor,
                            "serial": serial,
                            "connect_time": datetime.datetime.now().isoformat(),
                            "mount_path": mount_path,
                            "username": username,
                            "is_whitelisted": 1 if is_whitelisted else 0
                        }
                        
                        execute_query('''
                            INSERT INTO usb_devices (device_id, vendor, serial, connect_time, mount_path, username, is_whitelisted)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (device_info['device_id'], device_info['vendor'], device_info['serial'], 
                              device_info['connect_time'], device_info['mount_path'], device_info['username'],
                              device_info['is_whitelisted']))
                        
                        # Initialize trust scoring
                        self.trust_engine.evaluate_device(clean_device_id)
                        
                        whitelist_status = "✓ WHITELISTED" if is_whitelisted else "⚠ NOT WHITELISTED"
                        print(f"[!] New USB Device Connected: {device_info['mount_path']} | User: {username} | {whitelist_status}")
                        
                        if whitelist_info:
                            print(f"    Trusted Device: {whitelist_info.get('description', 'N/A')}")
                        
                        if mount_path != "Unknown":
                            self.callback(mount_path, device_info['device_id'], username, is_whitelisted)
            
            self.connected_devices.intersection_update(current_devices)
            time.sleep(2)

    def monitor_linux(self):
        try:
            import pyudev
            import psutil
        except ImportError:
            print("pyudev not installed. Cannot monitor USB on Linux.")
            return

        print("[*] Starting USB Monitor (Linux)...")
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='block', device_type='partition')
        
        for action, device in monitor:
            if action == 'add' and device.get('ID_BUS') == 'usb':
                device_id = str(device.get('ID_SERIAL_SHORT', 'Unknown'))
                if device_id not in self.connected_devices:
                    self.connected_devices.add(device_id)
                    
                    time.sleep(2) # Wait for mount
                    mount_path = "Unknown"
                    for p in psutil.disk_partitions():
                        if p.device == device.device_node:
                            mount_path = p.mountpoint
                    
                    vendor = device.get('ID_VENDOR', 'Unknown')
                    serial = device.get('ID_SERIAL_SHORT', 'Unknown')
                    
                    # Get current username
                    username = get_current_username()
                    
                    # Check whitelist
                    is_whitelisted, whitelist_info = self.whitelist_manager.is_whitelisted(vendor, serial)
                    
                    device_info = {
                        "device_id": device_id,
                        "vendor": vendor,
                        "serial": serial,
                        "connect_time": datetime.datetime.now().isoformat(),
                        "mount_path": mount_path,
                        "username": username,
                        "is_whitelisted": 1 if is_whitelisted else 0
                    }
                    
                    execute_query('''
                        INSERT INTO usb_devices (device_id, vendor, serial, connect_time, mount_path, username, is_whitelisted)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (device_info['device_id'], device_info['vendor'], device_info['serial'], 
                          device_info['connect_time'], device_info['mount_path'], device_info['username'],
                          device_info['is_whitelisted']))
                    
                    self.trust_engine.evaluate_device(device_id)
                    
                    whitelist_status = "✓ WHITELISTED" if is_whitelisted else "⚠ NOT WHITELISTED"
                    print(f"[!] New USB Device Connected: {device_info['mount_path']} | User: {username} | {whitelist_status}")
                    
                    if whitelist_info:
                        print(f"    Trusted Device: {whitelist_info.get('description', 'N/A')}")
                    
                    if mount_path != "Unknown":
                        self.callback(mount_path, device_info['device_id'], username, is_whitelisted)
