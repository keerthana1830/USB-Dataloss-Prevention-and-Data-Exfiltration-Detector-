"""
Device Whitelist Manager
Manages trusted USB devices based on vendor and serial number
"""
import json
import os

class WhitelistManager:
    def __init__(self, whitelist_file='whitelist.json'):
        self.whitelist_file = whitelist_file
        self.whitelist_data = self._load_whitelist()
    
    def _load_whitelist(self):
        """Load whitelist from JSON file"""
        try:
            # Check in project root
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r') as f:
                    return json.load(f)
            
            # Check in parent directory
            parent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.whitelist_file)
            if os.path.exists(parent_path):
                with open(parent_path, 'r') as f:
                    return json.load(f)
            
            # Return default structure if file doesn't exist
            print(f"[WARNING] Whitelist file not found: {self.whitelist_file}")
            return {
                "trusted_devices": [],
                "whitelist_enabled": True,
                "unknown_device_penalty": 30
            }
        except Exception as e:
            print(f"[ERROR] Failed to load whitelist: {e}")
            return {
                "trusted_devices": [],
                "whitelist_enabled": True,
                "unknown_device_penalty": 30
            }
    
    def is_whitelisted(self, vendor, serial):
        """
        Check if a device is in the whitelist
        Returns: (is_whitelisted: bool, device_info: dict or None)
        """
        if not self.whitelist_data.get('whitelist_enabled', True):
            # Whitelist disabled, treat all devices as trusted
            return True, None
        
        vendor_clean = str(vendor).strip().lower()
        serial_clean = str(serial).strip().lower()
        
        for device in self.whitelist_data.get('trusted_devices', []):
            device_vendor = str(device.get('vendor', '')).strip().lower()
            device_serial = str(device.get('serial', '')).strip().lower()
            
            # Match on both vendor and serial
            if device_vendor == vendor_clean and device_serial == serial_clean:
                return True, device
            
            # Also match if serial matches (more specific identifier)
            if device_serial and device_serial == serial_clean:
                return True, device
        
        return False, None
    
    def get_unknown_device_penalty(self):
        """Get the risk penalty for unknown devices"""
        return self.whitelist_data.get('unknown_device_penalty', 30)
    
    def add_device(self, vendor, serial, description=""):
        """Add a device to the whitelist"""
        from datetime import datetime
        
        new_device = {
            "vendor": vendor,
            "serial": serial,
            "description": description,
            "added_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.whitelist_data['trusted_devices'].append(new_device)
        self._save_whitelist()
        print(f"[WHITELIST] Added device: {vendor} - {serial}")
    
    def remove_device(self, serial):
        """Remove a device from the whitelist by serial number"""
        original_count = len(self.whitelist_data['trusted_devices'])
        self.whitelist_data['trusted_devices'] = [
            d for d in self.whitelist_data['trusted_devices']
            if d.get('serial', '').lower() != serial.lower()
        ]
        
        if len(self.whitelist_data['trusted_devices']) < original_count:
            self._save_whitelist()
            print(f"[WHITELIST] Removed device with serial: {serial}")
            return True
        return False
    
    def _save_whitelist(self):
        """Save whitelist to JSON file"""
        try:
            # Try to save in project root first
            save_path = self.whitelist_file
            if not os.path.exists(os.path.dirname(save_path) or '.'):
                save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.whitelist_file)
            
            with open(save_path, 'w') as f:
                json.dump(self.whitelist_data, f, indent=2)
            print(f"[WHITELIST] Saved to {save_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save whitelist: {e}")
    
    def get_all_devices(self):
        """Get all whitelisted devices"""
        return self.whitelist_data.get('trusted_devices', [])
