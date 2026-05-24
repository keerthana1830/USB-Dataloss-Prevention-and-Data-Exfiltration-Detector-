# USB DLP Detector - Quick Start Guide

## 🚀 Installation (5 Minutes)

### Step 1: Install Dependencies
```bash
cd usb-dlp-detector
pip install -r requirements.txt
```

### Step 2: Configure Email Alerts (Optional)
Edit `config.py`:
```python
SMTP_CONFIG = {
    'enabled': True,  # Set False to disable
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password',  # Gmail App Password
    'recipient_emails': ['admin@company.com']
}
```

**Gmail Setup:**
1. Enable 2FA on Gmail
2. Go to: Google Account → Security → App Passwords
3. Generate password for "Mail"
4. Use 16-character password in config

### Step 3: Configure Trusted Devices (Optional)
Edit `whitelist.json`:
```json
{
  "trusted_devices": [
    {
      "vendor": "SanDisk",
      "serial": "ABC123XYZ",
      "description": "IT Approved USB"
    }
  ],
  "whitelist_enabled": true
}
```

### Step 4: Run the System
```bash
python main.py
```

### Step 5: Open Dashboard
```
http://localhost:5000
```

---

## 📋 Feature Checklist

### ✅ Device Whitelisting
- **File:** `whitelist.json`
- **Purpose:** Trust approved USB devices
- **Risk Penalty:** +30 points for unknown devices
- **Status:** Check console for "✓ WHITELISTED" or "⚠ NOT WHITELISTED"

### ✅ Email Alerts
- **File:** `config.py`
- **Trigger:** Risk score ≥ 70
- **Test:** Run `python -c "from backend.email_notifier import EmailNotifier; EmailNotifier().test_email_configuration()"`
- **Status:** Check console for "[EMAIL] Alert sent"

### ✅ CSV/PDF Export
- **URLs:** 
  - CSV: `http://localhost:5000/export/csv`
  - PDF: `http://localhost:5000/export/pdf`
- **Buttons:** Click "📊 Export CSV" or "📄 Export PDF" in dashboard sidebar
- **Output:** Downloads `usb_dlp_audit_YYYYMMDD_HHMMSS.csv/pdf`

### ✅ User Identity Tracking
- **Automatic:** Captures OS username on every event
- **View:** Check "User" column in dashboard tables
- **Database:** `username` field in all tables

### ✅ Live WebSocket Alerts
- **Status:** Check "● Live Monitoring Active" in dashboard header
- **Toast:** Popup appears when alert generated
- **Auto-refresh:** Dashboard updates automatically

### ✅ File Hash Logging
- **Automatic:** SHA-256 hash computed for every file
- **View:** "Hash (SHA256)" column in File Activity table
- **Export:** Full hash included in CSV/PDF exports

---

## 🎯 Quick Tests

### Test 1: Whitelist (30 seconds)
```bash
# 1. Connect USB device
# 2. Check console output:
#    ✓ WHITELISTED = trusted device
#    ⚠ NOT WHITELISTED = unknown device
```

### Test 2: Email (1 minute)
```bash
python -c "from backend.email_notifier import EmailNotifier; EmailNotifier().test_email_configuration()"
# Check your email inbox
```

### Test 3: Export (30 seconds)
```bash
# Open browser: http://localhost:5000
# Click "📊 Export CSV" button
# Click "📄 Export PDF" button
# Check Downloads folder
```

### Test 4: WebSocket (1 minute)
```bash
# 1. Open dashboard in browser
# 2. Copy large file (>100MB) to USB
# 3. Watch for toast notification popup
# 4. Check "● Live Monitoring Active" status
```

### Test 5: User Tracking (30 seconds)
```bash
# 1. Connect USB and copy file
# 2. Check dashboard "File Activity" table
# 3. Verify your username appears in "User" column
```

---

## 📊 Dashboard Overview

### Main Sections
1. **Overview Metrics** - Total connections, files, alerts
2. **Risk Heatmap** - 24-hour risk visualization
3. **Charts** - Files per day, alerts per day, risk distribution
4. **Security Alerts** - Real-time alert table
5. **Device Trust Status** - Whitelist status
6. **Forensic Timeline** - Chronological event view
7. **File Activity** - Detailed transfer logs with hashes
8. **Hardware Logs** - USB connection history

### Export Buttons (Sidebar)
- 📊 Export CSV - Download audit log as CSV
- 📄 Export PDF - Download audit report as PDF

### Live Status Indicator (Header)
- ● Live Monitoring Active (green) - System running
- ● Connection Lost (red) - WebSocket disconnected

---

## 🔧 Configuration Files

### `config.py` - System Configuration
```python
SMTP_CONFIG = {...}        # Email settings
RISK_THRESHOLDS = {...}    # Risk score thresholds
WHITELIST_FILE = '...'     # Whitelist file path
```

### `whitelist.json` - Trusted Devices
```json
{
  "trusted_devices": [...],
  "whitelist_enabled": true,
  "unknown_device_penalty": 30
}
```

---

## 🐛 Common Issues

### Issue: Email not sending
**Solution:** 
- Use Gmail App Password (not regular password)
- Set `enabled: True` in config.py
- Check SMTP port 587 not blocked

### Issue: WebSocket not connecting
**Solution:**
- Install: `pip install Flask-SocketIO`
- Restart system: `python main.py`
- Check browser console for errors

### Issue: PDF export fails
**Solution:**
- Install: `pip install fpdf2`
- Use CSV export as alternative

### Issue: Username shows "Unknown"
**Solution:**
- Normal on some systems
- Check running with proper user context
- Not critical - system still works

---

## 📈 Risk Scoring

### Risk Factors
| Factor | Points | Description |
|--------|--------|-------------|
| Unknown Device | +30 | Not in whitelist |
| Large File | +30 | File > 100MB |
| Sensitive Type | +20 | .pdf, .xlsx, .sql, etc. |
| After Hours | +20 | Outside 9 AM - 6 PM |
| Bulk Transfer | +40 | >20 files in 60 seconds |
| Honeypot File | +150 | Decoy file accessed |
| Sensitive Keywords | +40 | Password, confidential, etc. |
| ML Anomaly | +30 | Unusual pattern detected |

### Alert Thresholds
- **Medium:** 20-59 points
- **High:** 60-99 points
- **Critical:** 100+ points

### Email Trigger
- Emails sent for alerts ≥ 70 points (configurable)

---

## 📝 Database Schema

### Tables Created
```sql
usb_devices (id, device_id, vendor, serial, connect_time, mount_path, username, is_whitelisted)
file_activity (id, file_name, extension, size, source, destination, timestamp, device_id, file_hash, speed_mbps, username)
alerts (id, device_id, risk_score, reason, timestamp, severity, username, email_sent)
device_trust (device_id, first_seen, trust_score, status)
```

### Query Examples
```sql
-- View all whitelisted devices
SELECT * FROM usb_devices WHERE is_whitelisted = 1;

-- View files with hashes
SELECT file_name, file_hash, username FROM file_activity WHERE file_hash != 'Unknown';

-- View high-risk alerts
SELECT * FROM alerts WHERE risk_score >= 70 ORDER BY timestamp DESC;

-- View alerts with email sent
SELECT * FROM alerts WHERE email_sent = 1;
```

---

## 🎓 Usage Scenarios

### Scenario 1: IT Department
- Add all approved USB devices to whitelist
- Configure email to security team
- Export weekly audit reports (CSV/PDF)
- Monitor dashboard for real-time alerts

### Scenario 2: Compliance Audit
- Export PDF report for auditors
- Show user tracking in File Activity
- Demonstrate file hash integrity
- Review alert history

### Scenario 3: Incident Response
- Check WebSocket alerts for real-time threats
- Export CSV for forensic analysis
- Verify file hashes for integrity
- Track user activity timeline

### Scenario 4: Security Demo
- Connect unknown USB (triggers alert)
- Copy large file (triggers alert)
- Show toast notification popup
- Export PDF report

---

## 🔐 Security Best Practices

1. **Whitelist Management**
   - Review whitelist monthly
   - Remove unused devices
   - Document approval process

2. **Email Security**
   - Use dedicated security email
   - Configure multiple recipients
   - Monitor email delivery

3. **Audit Logs**
   - Export logs weekly
   - Store in secure location
   - Include in backups

4. **User Privacy**
   - Inform users about monitoring
   - Include in acceptable use policy
   - Protect username data

5. **System Security**
   - Run with appropriate permissions
   - Keep dependencies updated
   - Monitor system logs

---

## 📞 Support

### Check Logs
```bash
# Console output shows all events
python main.py

# Look for:
# [USB] Device connected
# [FILE] File transferred
# [ALERT] Security alert
# [EMAIL] Email sent
# [WEBSOCKET] Alert broadcasted
```

### Verify Installation
```bash
pip list | grep -E "Flask|watchdog|psutil|fpdf2|socketio"
```

### Test Components
```python
# Test email
from backend.email_notifier import EmailNotifier
EmailNotifier().test_email_configuration()

# Test whitelist
from backend.whitelist_manager import WhitelistManager
wm = WhitelistManager()
print(wm.get_all_devices())

# Test username
from backend.user_utils import get_current_username
print(get_current_username())
```

---

## ✅ Success Indicators

You know the system is working when:
- ✅ Console shows "[*] Starting USB Monitor"
- ✅ Dashboard accessible at http://localhost:5000
- ✅ Connection status shows "● Live Monitoring Active"
- ✅ USB connection logged in dashboard
- ✅ File transfer shows hash in Activity table
- ✅ Alert generates toast notification
- ✅ CSV/PDF export downloads successfully
- ✅ Email received (if configured)

---

**System is ready for production use!** 🎉

For detailed documentation, see `NEW_FEATURES_DOCUMENTATION.md`
