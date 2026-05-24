class HoneypotMonitor:
    def __init__(self):
        # All entries must be lowercase for case-insensitive matching
        self.honeypot_files = ['salary_2025.xlsx', 'passwords.txt', 'customer_database.csv']

    def is_honeypot(self, file_name):
        return file_name.strip().lower() in [f.lower() for f in self.honeypot_files]
