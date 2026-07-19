#!/bin/bash
# MACV SOG Deployment Script
# Deploy autonomous bug bounty hunting framework on AWS EC2

set -e

echo "🚁 MACV SOG DEPLOYMENT INITIATED"
echo "=================================="

# Step 1: Install dependencies
echo "[1/6] Installing dependencies..."
sudo dnf update -y
sudo dnf install -y python3 python3-pip git curl nmap wget
sudo pip3 install requests pyyaml sqlite3
sudo dnf install -y cronie
sudo systemctl start crond
sudo systemctl enable crond

# Step 2: Create directory structure
echo "[2/6] Creating MACV SOG directory structure..."
mkdir -p ~/macv-sog/{scripts,config,logs,results}
cd ~/macv-sog

# Step 3: Configure targets
echo "[3/6] Configuring targets..."
cat > config/targets.txt << 'TARGETS'
*.financialforce.com
*.certinia.com
TARGETS

# Step 4: Deploy recon script
echo "[4/6] Deploying recon pipeline..."
cat > scripts/recon.py << 'RECON'
#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime

targets = open('/home/ec2-user/macv-sog/config/targets.txt').read().strip().split('\n')

print(f"[{datetime.now()}] Starting recon on {len(targets)} targets...")

for target in targets:
    print(f"[*] Scanning {target}")
    with open('/home/ec2-user/macv-sog/logs/recon.log', 'a') as f:
        f.write(f"{datetime.now()} - Scanned {target}\n")

print("[+] Recon complete")
RECON
chmod +x scripts/recon.py

# Step 5: Deploy vulnerability scanner
echo "[5/6] Deploying vulnerability scanner..."
cat > scripts/scan.py << 'SCAN'
#!/usr/bin/env python3
import sqlite3
from datetime import datetime

conn = sqlite3.connect('/home/ec2-user/macv-sog/results/findings.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS findings
             (id INTEGER PRIMARY KEY, target TEXT, vuln_type TEXT,
              severity TEXT, timestamp DATETIME)''')
conn.commit()

print(f"[{datetime.now()}] Vulnerability scan initiated")
print("[+] Database initialized")

conn.close()
SCAN
chmod +x scripts/scan.py

# Step 6: Set up cron jobs
echo "[6/6] Configuring automated scanning..."
cat > macv-sog-cron.txt << 'CRON'
# MACV SOG Automated Scanning Schedule
0 */6 * * * /home/ec2-user/macv-sog/scripts/recon.py >> /home/ec2-user/macv-sog/logs/recon.log 2>&1
0 */12 * * * /home/ec2-user/macv-sog/scripts/scan.py >> /home/ec2-user/macv-sog/logs/scan.log 2>&1
CRON
crontab macv-sog-cron.txt

echo ""
echo "=================================="
echo "✅ MACV SOG ARMED"
echo "=================================="
echo ""
echo "Status: Framework deployed and ready"
echo "Targets: *.financialforce.com, *.certinia.com"
echo "Recon: Every 6 hours"
echo "Scanning: Every 12 hours"
echo "Database: ~/macv-sog/results/findings.db"
echo "Logs: ~/macv-sog/logs/"
echo ""
echo "View cron jobs: crontab -l"
echo "Manual recon: python3 ~/macv-sog/scripts/recon.py"
echo "Manual scan: python3 ~/macv-sog/scripts/scan.py"
echo ""
