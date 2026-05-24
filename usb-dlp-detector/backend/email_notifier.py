"""
Email Alert Notification System
Sends email alerts when high-risk activities are detected
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys
import os

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from config import SMTP_CONFIG
except ImportError:
    # Default configuration if config.py not found
    SMTP_CONFIG = {
        'enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_tls': True,
        'sender_email': 'your-email@gmail.com',
        'sender_password': 'your-password',
        'recipient_emails': ['admin@company.com'],
        'alert_threshold': 70
    }

class EmailNotifier:
    def __init__(self):
        self.config = SMTP_CONFIG
        self.enabled = self.config.get('enabled', False)
        
        if not self.enabled:
            print("[EMAIL] Email notifications are disabled in config.py")
    
    def send_alert_email(self, device_id, file_name, risk_score, reason, severity, username="Unknown"):
        """
        Send email alert for high-risk activity
        """
        if not self.enabled:
            return False
        
        # Check if risk score meets threshold
        threshold = self.config.get('alert_threshold', 70)
        if risk_score < threshold:
            return False
        
        try:
            # Create email message
            subject = f"🚨 USB DLP Alert: {severity} Risk Detected (Score: {risk_score})"
            
            body = self._create_email_body(device_id, file_name, risk_score, reason, severity, username)
            
            # Send to all recipients
            recipients = self.config.get('recipient_emails', [])
            if not recipients:
                print("[EMAIL] No recipient emails configured")
                return False
            
            for recipient in recipients:
                self._send_email(recipient, subject, body)
            
            print(f"[EMAIL] Alert sent to {len(recipients)} recipient(s)")
            return True
            
        except Exception as e:
            print(f"[EMAIL] Failed to send alert: {e}")
            return False
    
    def _create_email_body(self, device_id, file_name, risk_score, reason, severity, username):
        """Create formatted email body"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        body = f"""
USB Data Loss Prevention Alert
{'=' * 60}

ALERT DETAILS:
--------------
Severity:       {severity}
Risk Score:     {risk_score}
Timestamp:      {timestamp}
User:           {username}
Device ID:      {device_id}
File:           {file_name}

RISK FACTORS:
-------------
{reason}

ACTION REQUIRED:
----------------
This alert indicates potential data exfiltration activity.
Please investigate immediately and take appropriate action.

RECOMMENDATIONS:
----------------
1. Contact the user to verify the file transfer
2. Review the file contents if necessary
3. Check if the USB device is authorized
4. Consider blocking the device if unauthorized
5. Document the incident for compliance

{'=' * 60}
This is an automated alert from USB DLP Detector.
Do not reply to this email.
        """
        
        return body.strip()
    
    def _send_email(self, recipient, subject, body):
        """Send email using SMTP"""
        msg = MIMEMultipart()
        msg['From'] = self.config['sender_email']
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        if self.config.get('use_tls', True):
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
        else:
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
        
        # Login and send
        server.login(self.config['sender_email'], self.config['sender_password'])
        server.send_message(msg)
        server.quit()
    
    def test_email_configuration(self):
        """Test email configuration by sending a test email"""
        if not self.enabled:
            print("[EMAIL] Email notifications are disabled")
            return False
        
        try:
            subject = "USB DLP Detector - Test Email"
            body = """
This is a test email from USB DLP Detector.

If you received this email, your email configuration is working correctly.

Timestamp: {}
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            recipients = self.config.get('recipient_emails', [])
            for recipient in recipients:
                self._send_email(recipient, subject, body)
            
            print(f"[EMAIL] Test email sent successfully to {len(recipients)} recipient(s)")
            return True
            
        except Exception as e:
            print(f"[EMAIL] Test email failed: {e}")
            print("[EMAIL] Please check your SMTP configuration in config.py")
            return False
