# USB DLP Detector - New Features Documentation

## 🎯 Overview of New Features

This document describes the 6 major features added to the USB DLP Detector system:

1. **Device Whitelisting** - Trust management for approved USB devices
2. **Email Alert Notifications** - Automated email alerts for high-risk activities
3. **Audit Log Export (CSV/PDF)** - Comprehensive reporting capabilities
4. **User Identity Tagging** - Track which user performed each action
5. **Live WebSocket Alerts** - Real-time dashboard notifications
6. **File Hash Logging** - SHA-256 hashing for forensic integrity

---

## 1. Device Whitelisting

### Description
Maintains a list of trusted USB devices based on vendor and serial number. Unknown devices receive higher risk scores.

### Files Modified/Created
- **NEW:** `whitelist.json` - Stores trusted device list
- **NEW:** `backend/whitelist_manager.py` - Whitelist management logic
- **MODIFIED:** `backend/usb_monitor.py` - Checks devices against whitelist
- **MODIFIED:** `backend/risk_engine.py` - Applies whitelist penalty
- **MODIFIED:** `backend/database.py` - Added `is_whitelisted` column

### Configuration

Edit `whitelist.json`:
```json
{
  "trusted_devices": [
    {
      "vendor": "SanDisk",
      "serial": "4C530001234567890123",
      "description": "IT Department Approved USB",
      "added_date": "2024-01-15"
    }
  ],
  "whitelist_enabled": true,
  "unknown_device_penalty": 30
}
```

### How It Works
1. When USB device connects, system extracts vendor and serial number
2. `WhitelistManager` checks if device is in `whitelist.json`
3. If NOT whitelisted, adds +30 risk points (configurable)
4. Whitelist status stored in database for audit trail

### Usage
```python
from backend.whitelist_manager import WhitelistManager

wm = WhitelistManager()

# Check if device is whitelisted
is_trusted, device_info = wm.is_whitelisted("SanDisk", "ABC123")

# Add new trusted device
wm.add_device("Kingston", "XYZ789", "Executive USB Drive")

# Remove device
wm.remove_device("XYZ789")
```

---

## 2. Email Alert Notifications

### Description
Automatically sends email alerts to administrators when high-risk activities are detected (risk score ≥ 70).

### Files Modified/Created
- **NEW:** `config.py` - SMTP configuration
- **NEW:** `backend/email_notifier.py` - Email sending logic
- **MODIFIED:** `backend/alert_engine.py` - Integrated email notifications
- **MODIFIED:** `backend/database.py` - Added `email_sent` column

### Configuration

Edit `config.py`:
```python
SMTP_CONFIG = {
    'enabled': True,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password',  # Use app-specific password
    'recipient_emails': ['admin@company.com', 'security@company.com'],
    'alert_threshold': 70
}
```

### Gmail Setup
1. Enable 2-Factor Authentication on your Gmail account
2. Generate App Password: Google Account → Security → App Passwords
3. Use the 16-character app password in `config.py`

### Email Format
```
Subject: 🚨 USB DLP Alert: High Risk Detected (Score: 85)

USB Data Loss Prevention Alert
============================================================

ALERT DETAILS:
--------------
Severity:       High
Risk Score:     85
Timestamp:      2024-01-15 14:30:00
User:           john.doe
Device ID:      USB\VID_0781&PID_5567
File:           confidential_data.xlsx

RISK FACTORS:
-------------
Unknown/Non-whitelisted device (+30), Sensitive file format (.xlsx), 
Outside business hours

ACTION REQUIRED:
----------------
This alert indicates potential data exfiltration activity.
Please investigate immediately and take appropriate action.
```

### Testing Email Configuration
```python
from backend.email_notifier import EmailNotifier

notifier = EmailNotifier()
notifier.test_email_configuration()
```

---

## 3. Audit Log Export (CSV/PDF)

### Description
Export complete audit logs of USB connections, file transfers, and security alerts in CSV or PDF format.

### Files Modified/Created
- **MODIFIED:** `dashboard/app.py` - Added `/export/csv` and `/export/pdf` routes
- **MODIFIED:** `requirements.txt` - Added `fpdf2` dependency

### API Endpoints

#### Export CSV
```
GET /export/csv
```
Downloads: `usb_dlp_audit_YYYYMMDD_HHMMSS.csv`

#### Export PDF
```
GET /export/pdf
```
Downloads: `usb_dlp_audit_YYYYMMDD_HHMMSS.pdf`

### CSV Format
```csv
Type,Timestamp,Device ID,User,Details,Risk Score,File Hash
USB Connection,2024-01-15 10:30:00,USB\VID_0781,john.doe,"Vendor: SanDisk, Serial: ABC123",,
File Transfer,2024-01-15 10:31:00,USB\VID_0781,john.doe,"File: document.pdf, Size: 2048576 bytes",,a3f5b8c9...
Alert (High),2024-01-15 10:31:00,USB\VID_0781,john.doe,"Unknown device; Sensitive file type",75,
```

### PDF Contents
- Summary statistics
- Recent security alerts with details
- Recent file activity with hashes
- Formatted for professional reporting

### Usage from Dashboard
1. Click "📊 Export CSV" button in sidebar
2. Click "📄 Export PDF" button in sidebar
3. Files download automatically with timestamp

### Programmatic Export
```bash
# Download CSV
curl http://localhost:5000/export/csv -o audit.csv

# Download PDF
curl http://localhost:5000/export/pdf -o audit.pdf
```

---

## 4. User Identity Tagging

### Description
Captures and logs the currently logged-in OS username for every USB connection and file transfer event.

### Files Modified/Created
- **NEW:** `backend/user_utils.py` - Username detection logic
- **MODIFIED:** `backend/usb_monitor.py` - Captures username on USB connect
- **MODIFIED:** `backend/file_monitor.py` - Captures username on file transfer
- **MODIFIED:** `backend/database.py` - Added `username` columns
- **MODIFIED:** `backend/alert_engine.py` - Includes username in alerts

### How It Works
1. `get_current_username()` tries multiple methods:
   - `getpass.getuser()` (most reliable)
   - `os.getlogin()` (fallback)
   - Environment variables (`USERNAME` on Windows, `USER` on Linux)
2. Username captured at time of USB connection
3. Username passed through to file monitoring
4. All database records include username field

### Database Schema Updates
```sql
-- USB Devices
ALTER TABLE usb_devices ADD COLUMN username TEXT;

-- File Activity
ALTER TABLE file_activity ADD COLUMN username TEXT;

-- Alerts
ALTER TABLE alerts ADD COLUMN username TEXT;
```

### Usage Example
```python
from backend.user_utils import get_current_username

username = get_current_username()
print(f"Current user: {username}")
# Output: Current user: john.doe
```

### Benefits
- **Accountability**: Know exactly who performed each action
- **Incident Response**: Quickly identify users involved in security incidents
- **Compliance**: Meet audit requirements for user tracking
- **Forensics**: Build timeline of user activities

---

## 5. Live WebSocket Alerts on Dashboard

### Description
Real-time push notifications to the dashboard when security alerts are generated. Toast popups appear instantly without page refresh.

### Files Modified/Created
- **MODIFIED:** `dashboard/app.py` - Added Flask-SocketIO integration
- **MODIFIED:** `backend/alert_engine.py` - Emits WebSocket events
- **MODIFIED:** `dashboard/templates/index.html` - WebSocket client + toast UI
- **MODIFIED:** `requirements.txt` - Added Flask-SocketIO dependencies
- **MODIFIED:** `main.py` - Uses socketio.run() instead of app.run()

### Architecture
```
Alert Generated → Alert Engine → WebSocket Emit → Dashboard Client → Toast Popup
```

### WebSocket Events

#### Server → Client: `new_alert`
```javascript
{
    'id': 123,
    'device_id': 'USB\\VID_0781',
    'file_name': 'secret.pdf',
    'risk_score': 85,
    'reason': 'Unknown device; Sensitive file type',
    'severity': 'High',
    'username': 'john.doe',
    'timestamp': '2024-01-15T14:30:00',
    'email_sent': true
}
```

### Toast Notification Features
- **Color-coded by severity**:
  - Critical: Red background
  - High: Orange background
  - Medium: Yellow background
- **Auto-dismiss**: Disappears after 10 seconds
- **Manual close**: Click × button
- **Email indicator**: Shows if email was sent
- **Slide-in animation**: Smooth appearance from right
- **Multiple toasts**: Stack vertically

### Client-Side Code
```javascript
const socket = io();

socket.on('new_alert', function(alert) {
    showToast(alert);
    refreshDashboard();
});
```

### Connection Status
Dashboard header shows real-time connection status:
- ● Live Monitoring Active (green) - Connected
- ● Connection Lost (red) - Disconnected

---

## 6. File Hash Logging

### Description
Computes SHA-256 hash of every file transferred to USB devices for forensic integrity verification.

### Files Modified/Created
- **MODIFIED:** `backend/file_monitor.py` - Added `calculate_sha256()` function
- **MODIFIED:** `backend/database.py` - Added `file_hash` column
- **ALREADY IMPLEMENTED** - This feature was already in the original code!

### How It Works
1. When file is copied to USB, `calculate_sha256()` reads file in 4KB chunks
2. Computes SHA-256 hash of entire file contents
3. Stores hash in database alongside file metadata
4. Hash displayed in dashboard and exports

### Hash Function
```python
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        return "Unknown"
```

### Database Storage
```sql
CREATE TABLE file_activity (
    ...
    file_hash TEXT,
    ...
);
```

### Use Cases
- **Forensic Analysis**: Verify file integrity
- **Duplicate Detection**: Identify repeated file copies
- **Malware Detection**: Compare against known malware hashes
- **Chain of Custody**: Prove file hasn't been modified
- **Compliance**: Meet data integrity requirements

### Example Hashes
```
document.pdf → a3f5b8c9d2e1f4a7b6c5d8e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0
secret.xlsx  → 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2
```

### Viewing Hashes
- **Dashboard**: File Activity table shows first 16 characters
- **CSV Export**: Full 64-character hash included
- **Database Query**:
```sql
SELECT file_name, file_hash FROM file_activity WHERE file_hash != 'Unknown';
```

---

## 🚀 Installation & Setup

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

New packages added:
- `Flask-SocketIO>=5.3.5` - WebSocket support
- `python-socketio>=5.10.0` - SocketIO client
- `fpdf2>=2.7.6` - PDF generation

### 2. Configure Email (Optional)
Edit `config.py`:
```python
SMTP_CONFIG = {
    'enabled': True,  # Set to False to disable
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password',
    'recipient_emails': ['admin@company.com']
}
```

### 3. Configure Whitelist
Edit `whitelist.json` to add your trusted USB devices:
```json
{
  "trusted_devices": [
    {
      "vendor": "YourVendor",
      "serial": "YourSerialNumber",
      "description": "Description",
      "added_date": "2024-01-15"
    }
  ]
}
```

### 4. Run the System
```bash
python main.py
```

### 5. Access Dashboard
```
http://localhost:5000
```

---

## 📊 Feature Summary Table

| Feature | Status | Files Modified | Dependencies Added |
|---------|--------|----------------|-------------------|
| Device Whitelisting | ✅ Complete | 5 files | None |
| Email Notifications | ✅ Complete | 4 files | None (uses stdlib) |
| CSV/PDF Export | ✅ Complete | 2 files | fpdf2 |
| User Identity Tagging | ✅ Complete | 6 files | None (uses stdlib) |
| WebSocket Alerts | ✅ Complete | 4 files | Flask-SocketIO |
| File Hash Logging | ✅ Already Existed | 0 files | None (uses hashlib) |

---

## 🔧 Testing Each Feature

### Test Device Whitelisting
1. Add your USB device to `whitelist.json`
2. Connect USB device
3. Check console output for "✓ WHITELISTED" message
4. Connect unknown device - should see "⚠ NOT WHITELISTED"

### Test Email Notifications
```python
from backend.email_notifier import EmailNotifier
notifier = EmailNotifier()
notifier.test_email_configuration()
```

### Test CSV/PDF Export
1. Open dashboard: `http://localhost:5000`
2. Click "📊 Export CSV" button
3. Click "📄 Export PDF" button
4. Check downloads folder

### Test User Identity
1. Connect USB device
2. Copy file to USB
3. Check database:
```sql
SELECT username FROM usb_devices;
SELECT username FROM file_activity;
```

### Test WebSocket Alerts
1. Open dashboard in browser
2. Copy a large file (>100MB) to USB
3. Watch for toast notification popup
4. Check connection status indicator

### Test File Hashing
1. Copy file to USB
2. Check console for hash output
3. Query database:
```sql
SELECT file_name, file_hash FROM file_activity LIMIT 5;
```

---

## 🐛 Troubleshooting

### Email Not Sending
- Check SMTP credentials in `config.py`
- For Gmail, use App Password (not regular password)
- Verify `enabled: True` in config
- Check firewall allows SMTP port 587

### WebSocket Not Connecting
- Ensure Flask-SocketIO installed: `pip install Flask-SocketIO`
- Check browser console for errors
- Verify port 5000 is not blocked

### Whitelist Not Working
- Check `whitelist.json` syntax (valid JSON)
- Verify vendor/serial match exactly (case-insensitive)
- Check console output for whitelist loading errors

### PDF Export Fails
- Install fpdf2: `pip install fpdf2`
- Check for special characters in data
- Try CSV export as alternative

### Username Shows "Unknown"
- Normal on some systems/environments
- Check if running with proper user context
- Verify not running as system service

---

## 📝 API Reference

### WhitelistManager
```python
from backend.whitelist_manager import WhitelistManager

wm = WhitelistManager()
is_trusted, info = wm.is_whitelisted(vendor, serial)
penalty = wm.get_unknown_device_penalty()
wm.add_device(vendor, serial, description)
wm.remove_device(serial)
```

### EmailNotifier
```python
from backend.email_notifier import EmailNotifier

notifier = EmailNotifier()
success = notifier.send_alert_email(device_id, file_name, risk_score, reason, severity, username)
notifier.test_email_configuration()
```

### Export Routes
```
GET /export/csv  - Download CSV audit log
GET /export/pdf  - Download PDF audit report
```

### WebSocket Events
```javascript
socket.on('connect', callback)
socket.on('disconnect', callback)
socket.on('new_alert', callback)
```

---

## 🎓 Best Practices

### Whitelist Management
- Regularly review and update whitelist
- Document reason for each trusted device
- Remove devices when no longer needed
- Use descriptive names in `description` field

### Email Configuration
- Use dedicated security email account
- Configure multiple recipients for redundancy
- Test email configuration before production
- Monitor email delivery logs

### Audit Exports
- Export logs regularly (weekly/monthly)
- Store exports in secure location
- Include exports in backup procedures
- Review exports for compliance

### User Tracking
- Inform users about monitoring (legal requirement)
- Include in acceptable use policy
- Protect username data (privacy)
- Use for incident response only

### WebSocket Monitoring
- Monitor connection status
- Handle reconnection gracefully
- Don't rely solely on WebSocket (also poll API)
- Test with multiple concurrent users

---

## 📚 Additional Resources

- Flask-SocketIO Documentation: https://flask-socketio.readthedocs.io/
- FPDF2 Documentation: https://py-pdf.github.io/fpdf2/
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- SHA-256 Hashing: https://docs.python.org/3/library/hashlib.html

---

## ✅ Verification Checklist

- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `config.py` configured with SMTP settings
- [ ] `whitelist.json` contains trusted devices
- [ ] Database schema updated (automatic on first run)
- [ ] Email test successful
- [ ] Dashboard accessible at http://localhost:5000
- [ ] WebSocket connection indicator shows green
- [ ] CSV export downloads successfully
- [ ] PDF export downloads successfully
- [ ] Toast notifications appear on alerts
- [ ] Username captured in database
- [ ] File hashes computed and stored

---

**All features are production-ready and fully integrated!** 🎉
