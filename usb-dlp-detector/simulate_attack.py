import os
import shutil
import time
import psutil

def simulate_attack():
    print("Starting Insider Data Exfiltration Simulation...\n")
    
    # 1. Look for an active USB drive dynamically
    usb_mount = None
    for p in psutil.disk_partitions():
        # Heuristic: removable drives or FAT32/exFAT types are typically USBs
        if 'removable' in p.opts.lower() or p.fstype in ['FAT32', 'exFAT']:
            usb_mount = p.mountpoint
            break
            
    if not usb_mount:
        print("ERROR: No USB Drive detected on the system!")
        print("Please plug in a USB thumb drive first so the DLP system can monitor it.")
        print("The attack simulation needs a real USB target to trigger the Watchdog and USB Monitoring tools.")
        return
        
    print(f"Targeting connected USB drive: {usb_mount}\n")
    
    try:
        # 1. HONEYPOT TRIGGER
        print("-> Step 1/3: Triggering Critical Alert (Copying Honeypot File)")
        with open("salary_2025.xlsx", "w") as f:
            f.write("mock spreadsheet data")
        shutil.copy("salary_2025.xlsx", os.path.join(usb_mount, "salary_2025.xlsx"))
        os.remove("salary_2025.xlsx")
        time.sleep(2)
        
        # 2. BEHAVIOR ANOMALY (Bulk Transfer)
        print("-> Step 2/3: Triggering Bulk Transfer & ML Anomaly")
        for i in range(25):
            name = f"dummy_confidential_{i}.txt"
            with open(name, "w") as f: f.write("normal mock data " * 10)
            shutil.copy(name, os.path.join(usb_mount, name))
            os.remove(name)
        time.sleep(2)
        
        # 3. SENSITIVE CONTENT SCAN TRIGGER
        print("-> Step 3/3: Triggering Sensitivity Scan")
        with open("passwords.txt", "w") as f:
            f.write("production db password is: secret_p@ssw0rd")
        shutil.copy("passwords.txt", os.path.join(usb_mount, "passwords.txt"))
        os.remove("passwords.txt")
        time.sleep(1)
        
        print("\nSimulation Complete! Check the Dashboard timelines & alerts.")
    except Exception as e:
        print(f"Simulation interrupted! Error: {e}")

if __name__ == "__main__":
    simulate_attack()
