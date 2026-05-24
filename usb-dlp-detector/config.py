"""
Configuration file for USB DLP Detector
"""

# SMTP Email Configuration
SMTP_CONFIG = {
    'enabled': False,  # Set to True and configure credentials to enable email alerts
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'sender_email': 'your-email@gmail.com',  # Change this
    'sender_password': 'your-app-password',  # Use app-specific password for Gmail
    'recipient_emails': ['admin@company.com', 'security@company.com'],  # List of recipients
    'alert_threshold': 70  # Send email only for alerts with risk score >= this value
}

# Risk Scoring Thresholds
RISK_THRESHOLDS = {
    'high': 70,
    'critical': 100,
    'medium': 50
}

# Whitelist Configuration
WHITELIST_FILE = 'whitelist.json'

# Database Configuration
DB_PATH = 'dlp_detector.db'
