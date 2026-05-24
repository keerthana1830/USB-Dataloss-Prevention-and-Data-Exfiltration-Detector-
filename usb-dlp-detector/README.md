# USB DLP — Insider Threat Detection Platform

A host-based **Data Loss Prevention (DLP)** and **Insider Threat Detection** platform that monitors USB storage devices in real-time, scores risk using behavioral analysis and machine learning, and provides a professional web dashboard for security operations teams.

---

## Features

| Category | Feature |
|---|---|
| **USB Monitoring** | Automatic detection of USB storage devices on Windows & Linux |
| **File Interception** | Real-time file transfer monitoring via `watchdog` |
| **Risk Engine** | Multi-factor scoring — file size, extension, time-of-day, bulk transfers, device trust |
| **ML Anomaly Detection** | Isolation Forest model detects unusual transfer patterns |
| **Honeypot Files** | Decoy file monitoring for instant critical alerts |
| **Sensitivity Scanner** | Keyword-based content scanning (passwords, salaries, confidential data) |
| **Device Trust** | Trust scoring system for known vs. unknown USB devices |
| **Device Whitelist** | JSON-based whitelist for approved USB devices |
| **User Identification** | Automatic OS-level user attribution on all events |
| **Email Alerts** | SMTP-based email notifications for high-risk events (configurable) |
| **Real-Time Dashboard** | Professional dark-themed web UI with live WebSocket updates |
| **Forensic Timeline** | Chronological event reconstruction for incident response |
| **Risk Heatmap** | 24-hour risk visualization by hour |

---

## Technology Stack

- **Backend**: Python 3.8+ (Flask, Flask-SocketIO, watchdog, psutil, scikit-learn, SQLite3)
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Database**: SQLite (zero-configuration)
- **Real-Time**: WebSocket (Socket.IO)

---

## Project Structure

```
usb-dlp-detector/
├── backend/
│   ├── __init__.py
│   ├── alert_engine.py          # Alert generation & WebSocket broadcast
│   ├── anomaly_detector.py      # ML-based anomaly detection (IsolationForest)
│   ├── behavior_profiler.py     # Behavioral baseline & deviation scoring
│   ├── database.py              # SQLite database operations
│   ├── device_trust_engine.py   # USB device trust scoring
│   ├── email_notifier.py        # SMTP email alert system
│   ├── file_monitor.py          # File transfer monitoring (watchdog)
│   ├── honeypot_monitor.py      # Honeypot/decoy file detection
│   ├── risk_engine.py           # Multi-factor risk scoring engine
│   ├── sensitivity_scanner.py   # File content keyword scanner
│   ├── usb_monitor.py           # USB device detection (Windows/Linux)
│   ├── user_utils.py            # OS username detection
│   └── whitelist_manager.py     # Device whitelist management
├── dashboard/
│   ├── __init__.py
│   ├── app.py                   # Flask web app & API endpoints
│   ├── static/
│   │   ├── charts.js            # Dashboard charts & data fetching
│   │   └── style.css            # Premium dark theme CSS
│   └── templates/
│       └── index.html           # Dashboard HTML template
├── config.py                    # Configuration (email, thresholds)
├── main.py                      # Application entry point
├── simulate_attack.py           # Demo simulation script
├── whitelist.json               # USB device whitelist
├── requirements.txt             # Python dependencies
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd usb-dlp-detector
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure (optional)**
   - Edit `config.py` to enable email alerts (SMTP credentials required)
   - Edit `whitelist.json` to add trusted USB devices

---

## Running the System

```bash
python main.py
```

This starts:
- USB device monitoring (background)
- File transfer interception (background)
- Web dashboard on **http://localhost:5000**

### Dashboard URLs
| URL | Description |
|---|---|
| `http://localhost:5000` | Main Dashboard |

---

## Demonstration

Run the attack simulation script while the system is running:

```bash
python simulate_attack.py
```

This simulates:
1. **Honeypot exfiltration** — copies decoy salary file (Critical alert)
2. **Bulk file transfer** — rapid copy of 25 files (ML anomaly + bulk alert)
3. **Sensitive content** — copies file with passwords (sensitivity scan alert)

Watch the dashboard update in real-time with alerts, timeline events, and chart changes.

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/stats` | Dashboard statistics |
| `GET /api/usb_devices` | Recent USB connections |
| `GET /api/device_trust` | Device trust scores |
| `GET /api/file_activity` | File transfer logs |
| `GET /api/alerts` | Security alerts |
| `GET /api/chart_data` | Chart data (files/day, alerts/day, risk scores) |
| `GET /api/heatmap_data` | Risk heatmap by hour |
| `GET /api/timeline` | Forensic timeline events |

---

## Configuration

### Email Alerts (`config.py`)
```python
SMTP_CONFIG = {
    'enabled': True,               # Enable/disable email
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password',  # Gmail app password
    'recipient_emails': ['admin@company.com'],
    'alert_threshold': 70
}
```

### Device Whitelist (`whitelist.json`)
```json
{
  "whitelist_enabled": true,
  "unknown_device_penalty": 30,
  "trusted_devices": [
    {
      "vendor": "SanDisk",
      "serial": "ABC123",
      "description": "Company-issued USB drive"
    }
  ]
}
```

---

## License

This project is for educational and research purposes.
