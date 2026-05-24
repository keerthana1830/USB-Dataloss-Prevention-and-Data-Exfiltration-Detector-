# Changelog - USB DLP Detector

## Version 2.0.0 - Enhanced Enterprise Features (2024-01-15)

### 🎉 Major Features Added

#### 1. Device Whitelisting System
- **NEW:** `whitelist.json` configuration file for trusted devices
- **NEW:** `backend/whitelist_manager.py` - Complete whitelist management
- **FEATURE:** Vendor and serial number matching
- **FEATURE:** Configurable risk penalty for unknown devices (+30 points default)
- **FEATURE:** Whitelist enable/disable toggle
- **FEATURE:** Device description and date tracking
- **UI:** Console shows "✓ WHITELISTED" or "⚠ NOT WHITELISTED" status

#### 2. Email Alert Notifications
- **NEW:** `config.py` - Centralized configuration management
- **NEW:** `backend/email_notifier.py` - SMTP email integration
- **FEATURE:** Automatic email alerts for high-risk activities (≥70 score)
- **FEATURE:** Configurable SMTP settings (server, port, TLS)
- **FEATURE:** Multiple recipient support
- **FEATURE:** Formatted email templates with alert details
- **FEATURE:** Email delivery tracking in database
- **FEATURE:** Test email configuration function
- **SUPPORT:** Gmail, Outlook, custom SMTP servers

#### 3. Audit Log Export (CSV/PDF)
- **NEW:** `/export/csv` API endpoint
- **NEW:** `/export/pdf` API endpoint
- **FEATURE:** One-click CSV export with all audit data
- **FEATURE:** Professional PDF reports with charts
- **FEATURE:** Timestamped filenames
- **FEATURE:** Includes USB connections, file transfers, and alerts
- **FEATURE:** File hash integrity data included
- **UI:** Export buttons in dashboard sidebar
- **DEPENDENCY:** Added fpdf2 for PDF generation

#### 4. User Identity Tagging
- **NEW:** `backend/user_utils.py` - OS username detection
- **FEATURE:** Captures logged-in username for all events
- **FEATURE:** Multi-method username detection (getpass, os.getlogin, env vars)
- **FEATURE:** Cross-platform support (Windows/Linux/macOS)
- **DATABASE:** Added `username` column to usb_devices table
- **DATABASE:** Added `username` column to file_activity table
- **DATABASE:** Added `username` column to alerts table
- **UI:** Username displayed in all dashboard tables
- **EXPORT:** Username included in CSV/PDF exports

#### 5. Live WebSocket Alerts
- **NEW:** Flask-SocketIO integration
- **FEATURE:** Real-time push notifications to dashboard
- **FEATURE:** Toast notification popups
- **FEATURE:** Color-coded by severity (Critical/High/Medium)
- **FEATURE:** Auto-dismiss after 10 seconds
- **FEATURE:** Manual close button
- **FEATURE:** Connection status indicator
- **FEATURE:** Email sent indicator in toasts
- **FEATURE:** Slide-in animation
- **FEATURE:** Multiple toast stacking
- **UI:** Live connection status in header
- **DEPENDENCY:** Added Flask-SocketIO and python-socketio

#### 6. File Hash Logging (Enhanced)
- **STATUS:** Already implemented in v1.0
- **FEATURE:** SHA-256 hash computation for all files
- **FEATURE:** 4KB chunk reading for memory efficiency
- **FEATURE:** Hash stored in database
- **FEATURE:** Hash displayed in dashboard (truncated)
- **FEATURE:** Full hash in CSV/PDF exports
- **USE CASE:** Forensic integrity verification
- **USE CASE:** Duplicate file detection

### 🔧 Technical Improvements

#### Database Schema Updates
```sql
-- usb_devices table
ALTER TABLE usb_devices ADD COLUMN username TEXT;
ALTER TABLE usb_devices ADD COLUMN is_whitelisted INTEGER DEFAULT 0;

-- file_activity table
ALTER TABLE file_activity ADD COLUMN username TEXT;

-- alerts table
ALTER TABLE alerts ADD COLUMN username TEXT;
ALTER TABLE alerts ADD COLUMN email_sent INTEGER DEFAULT 0;
```

#### Architecture Changes
- **MODIFIED:** `main.py` - Uses `socketio.run()` instead of `app.run()`
- **MODIFIED:** `dashboard/app.py` - Added SocketIO instance and export routes
- **MODIFIED:** `backend/alert_engine.py` - Integrated email and WebSocket
- **MODIFIED:** `backend/usb_monitor.py` - Added whitelist checking and username capture
- **MODIFIED:** `backend/file_monitor.py` - Added username parameter passing
- **MODIFIED:** `backend/risk_engine.py` - Added whitelist penalty calculation

#### New Dependencies
```
Flask-SocketIO>=5.3.5
python-socketio>=5.10.0
fpdf2>=2.7.6
```

### 📚 Documentation Added
- **NEW:** `NEW_FEATURES_DOCUMENTATION.md` - Comprehensive feature guide
- **NEW:** `QUICK_START_GUIDE.md` - Quick reference for users
- **NEW:** `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- **NEW:** `CHANGELOG.md` - This file

### 🎨 UI/UX Improvements
- Added export buttons to dashboard sidebar
- Added live connection status indicator
- Added toast notification system with animations
- Added color-coded severity indicators
- Improved visual feedback for all actions

### 🔒 Security Enhancements
- Whitelist-based device trust management
- User accountability tracking
- Email notifications for immediate response
- File integrity verification via hashing
- Audit trail with user attribution

### 📊 Compliance Features
- Complete audit log exports (CSV/PDF)
- User identity tracking for all actions
- File hash integrity evidence
- Timestamped event logging
- Email notification records

### 🐛 Bug Fixes
- None (new features only)

### ⚠️ Breaking Changes
- None - All changes are backward compatible
- Existing databases automatically upgraded on first run

### 🔄 Migration Notes
- Run `pip install -r requirements.txt` to install new dependencies
- Database schema updates automatically on first run
- Create `config.py` for email configuration (optional)
- Create `whitelist.json` for device whitelisting (optional)
- No data loss - all existing data preserved

---

## Version 1.0.0 - Initial Release

### Core Features
- USB device detection (Windows/Linux)
- File transfer monitoring with watchdog
- Behavioral risk scoring engine
- Alert generation system
- SQLite database logging
- Flask web dashboard
- Chart.js visualizations
- Device trust engine
- Sensitivity scanner
- Honeypot monitoring
- Behavior profiler
- ML anomaly detection (Isolation Forest)
- File hash computation (SHA-256)

### Modules
- `backend/database.py` - Database management
- `backend/usb_monitor.py` - USB device detection
- `backend/file_monitor.py` - File transfer monitoring
- `backend/risk_engine.py` - Risk scoring
- `backend/alert_engine.py` - Alert generation
- `backend/device_trust_engine.py` - Device trust scoring
- `backend/sensitivity_scanner.py` - Content scanning
- `backend/honeypot_monitor.py` - Honeypot detection
- `backend/behavior_profiler.py` - Behavioral analysis
- `backend/anomaly_detector.py` - ML anomaly detection
- `dashboard/app.py` - Flask web application
- `dashboard/templates/index.html` - Dashboard UI
- `dashboard/static/style.css` - Dashboard styling
- `dashboard/static/charts.js` - Chart rendering
- `main.py` - Application entry point

### Risk Factors (v1.0)
- Large file transfer (>100MB) - +30 points
- Sensitive file types - +20 points
- Bulk transfer (>20 files) - +40 points
- After-hours transfer - +20 points
- Unknown device - +30 points
- Honeypot file - +150 points
- Sensitive keywords - +40 points
- High speed transfer - +30 points
- Repeated file copying - +20 points
- ML anomaly - +30 points

---

## Upgrade Path

### From v1.0 to v2.0

1. **Backup Database**
   ```bash
   cp dlp_detector.db dlp_detector.db.backup
   ```

2. **Update Code**
   ```bash
   git pull  # or download new version
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create Configuration Files**
   ```bash
   # Copy templates
   cp config.py.example config.py  # Edit with your settings
   cp whitelist.json.example whitelist.json  # Edit with your devices
   ```

5. **Run System**
   ```bash
   python main.py
   ```
   Database schema will auto-upgrade on first run.

6. **Verify Features**
   - Check email configuration: Test email function
   - Check whitelist: Connect USB device
   - Check exports: Click export buttons
   - Check WebSocket: Watch for live status
   - Check username: View dashboard tables

---

## Roadmap

### Version 2.1.0 (Planned)
- [ ] SMS alert notifications
- [ ] Slack/Teams integration
- [ ] Custom alert rules engine
- [ ] Device blocking capability
- [ ] Multi-user dashboard with authentication
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Cloud storage integration
- [ ] Mobile app for alerts

### Version 2.2.0 (Planned)
- [ ] SIEM integration (Splunk, ELK)
- [ ] Active Directory integration
- [ ] Geolocation tracking
- [ ] Video recording on alert
- [ ] Automated incident response
- [ ] Compliance report templates
- [ ] Multi-language support
- [ ] Dark mode UI

### Version 3.0.0 (Future)
- [ ] Distributed deployment
- [ ] Central management console
- [ ] Agent-based architecture
- [ ] Real-time file content inspection
- [ ] Encrypted USB support
- [ ] Blockchain audit trail
- [ ] AI-powered threat intelligence
- [ ] Zero-trust architecture

---

## Contributors
- Initial development and v2.0 features implementation

## License
Educational and demonstration purposes

## Support
- Documentation: See `NEW_FEATURES_DOCUMENTATION.md`
- Quick Start: See `QUICK_START_GUIDE.md`
- Issues: Check console logs and documentation

---

**Current Version: 2.0.0** - All features production-ready ✅
