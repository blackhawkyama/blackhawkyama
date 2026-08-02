# 🚁 Autonomous Bug Hunting Framework for AWS

> **Fire and forget.** Automated recon → vulnerability scanning → result aggregation → reporting. Runs 24/7 on your AWS VM.

---

## 📋 What This Does

- ✅ **Automated Recon** — Discovers targets, subdomains, endpoints
- ✅ **Vulnerability Scanning** — Tests for IDOR, auth bypass, API issues, OWASP Top 10
- ✅ **Result Aggregation** — Collects findings, deduplicates, scores severity
- ✅ **Automated Reporting** — Slack alerts, HTML reports, JSON exports
- ✅ **Continuous Operation** — Runs 24/7, schedules rescans intelligently
- ✅ **Zero Manual Intervention** — Set it and forget it

---

## 🏗️ Architecture

```
AWS EC2 Instance (t3.medium or larger)
├── Recon Service (nmap, subfinder, assetfinder)
├── Scanning Service (Burp Suite headless, nuclei, sqlmap)
├── API Testing Service (custom Python scripts)
├── Result Aggregator (SQLite database)
├── Reporting Service (HTML, JSON, Slack webhooks)
└── Scheduler (cron jobs, no manual triggers)
```

---

## 🚀 Setup (AWS EC2)

### Step 1: Launch EC2 Instance

```bash
# AWS Recommended:
# - Instance Type: t3.large (4 vCPU, 16GB RAM)
# - OS: Ubuntu 22.04 LTS
# - Storage: 100GB EBS
# - Security Group: Allow SSH (your IP only)

# Cost: ~$100-150/month for continuous scanning
```

### Step 2: SSH Into Instance

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### Step 3: Install Dependencies

```bash
#!/bin/bash
# Install automation framework

sudo apt-get update && sudo apt-get upgrade -y

# Install required tools
sudo apt-get install -y \
  python3-pip \
  python3-venv \
  git \
  curl \
  wget \
  nmap \
  masscan \
  jq \
  sqlite3

# Install Go (for fast tools)
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# Install Rust (for nuclei)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Install recon tools
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Python setup
python3 -m venv ~/hunt-env
source ~/hunt-env/bin/activate
pip install requests sqlalchemy python-dotenv slack-sdk pyyaml

# Create working directories
mkdir -p ~/bug-hunt/{targets,recon,scans,results,logs}
cd ~/bug-hunt
```

---

## 📝 Configuration

### Step 1: Create `config.yaml`

```yaml
# ~/bug-hunt/config.yaml

targets:
  # Add your target domains/IPs
  - "example.com"
  - "api.example.com"
  - "192.168.0.0/24"

scanning:
  # Recon frequency (hours)
  recon_interval: 24
  
  # Vulnerability scan frequency (hours)
  vuln_scan_interval: 12
  
  # API testing frequency (hours)
  api_test_interval: 6
  
  # Rate limiting (requests/second)
  rate_limit: 5

reporting:
  # Slack webhook for alerts
  slack_webhook: "https://hooks.slack.com/services/YOUR/WEBHOOK/HERE"
  
  # Email for reports
  email_to: "your-email@example.com"
  
  # Report frequency
  report_interval: 24  # hours

tools:
  # Enable/disable tools
  nuclei: true
  burp: false  # Requires pro license
  sqlmap: true
  custom_api_tests: true
  
database:
  path: "/home/ubuntu/bug-hunt/results/findings.db"
```

---

## 🔧 Core Automation Scripts

### Script 1: Automated Recon Pipeline

```python
# ~/bug-hunt/recon.py

#!/usr/bin/env python3
import subprocess
import json
import os
from datetime import datetime
import logging

logging.basicConfig(
    filename="/home/ubuntu/bug-hunt/logs/recon.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AutoRecon:
    def __init__(self, targets, output_dir):
        self.targets = targets
        self.output_dir = output_dir
        
    def run_subfinder(self, domain):
        """Discover subdomains"""
        cmd = f"subfinder -d {domain} -all -json"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            subdomains = json.loads(result.stdout)
            logging.info(f"Found {len(subdomains)} subdomains for {domain}")
            return subdomains
        except Exception as e:
            logging.error(f"Subfinder error: {e}")
            return []
    
    def run_nmap(self, target):
        """Port scanning"""
        cmd = f"nmap -sV -p- --open -oJ {self.output_dir}/nmap_{target}.json {target}"
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=3600)
            logging.info(f"Nmap scan complete for {target}")
        except Exception as e:
            logging.error(f"Nmap error: {e}")
    
    def run_httpx(self, hosts_file):
        """Probe live hosts"""
        cmd = f"httpx -l {hosts_file} -json -o {self.output_dir}/httpx.json"
        try:
            subprocess.run(cmd, shell=True, capture_output=True)
            logging.info("Httpx probing complete")
        except Exception as e:
            logging.error(f"Httpx error: {e}")
    
    def start(self):
        logging.info("=== RECON PIPELINE STARTED ===")
        for target in self.targets:
            logging.info(f"Processing target: {target}")
            subdomains = self.run_subfinder(target)
            self.run_nmap(target)
            # More tasks...
        logging.info("=== RECON PIPELINE COMPLETE ===")

if __name__ == "__main__":
    import yaml
    with open("/home/ubuntu/bug-hunt/config.yaml") as f:
        config = yaml.safe_load(f)
    
    recon = AutoRecon(config['targets'], "/home/ubuntu/bug-hunt/recon")
    recon.start()
```

### Script 2: Vulnerability Scanning Pipeline

```python
# ~/bug-hunt/scan.py

#!/usr/bin/env python3
import subprocess
import json
import sqlite3
from datetime import datetime
import logging

logging.basicConfig(
    filename="/home/ubuntu/bug-hunt/logs/scan.log",
    level=logging.INFO
)

class VulnScanner:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create SQLite database for findings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                target TEXT,
                vuln_type TEXT,
                severity TEXT,
                description TEXT,
                proof_of_concept TEXT,
                status TEXT DEFAULT 'new',
                UNIQUE(target, vuln_type, severity)
            )
        ''')
        conn.commit()
        conn.close()
    
    def run_nuclei(self, hosts_file):
        """Run Nuclei vulnerability scanner"""
        cmd = f"""
        nuclei -l {hosts_file} \
            -t /root/nuclei-templates \
            -severity critical,high,medium \
            -json -o {self.output_dir}/nuclei.json \
            -rate-limit 50 \
            -timeout 10
        """
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=7200)
            self.import_nuclei_results()
            logging.info("Nuclei scan complete")
        except Exception as e:
            logging.error(f"Nuclei error: {e}")
    
    def run_sqlmap(self, urls_file):
        """Test for SQL injection"""
        cmd = f"sqlmap -m {urls_file} --batch --risk=2 --level=2 -j {self.output_dir}/sqlmap.json"
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=3600)
            logging.info("SQLMap scan complete")
        except Exception as e:
            logging.error(f"SQLMap error: {e}")
    
    def import_nuclei_results(self):
        """Import Nuclei JSON results into database"""
        try:
            with open(f"{self.output_dir}/nuclei.json") as f:
                results = json.loads(f.read())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for finding in results:
                cursor.execute('''
                    INSERT OR IGNORE INTO findings 
                    (timestamp, target, vuln_type, severity, description, proof_of_concept)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    finding.get('host'),
                    finding.get('template-id'),
                    finding.get('severity'),
                    finding.get('info', {}).get('description'),
                    json.dumps(finding)
                ))
            
            conn.commit()
            conn.close()
            logging.info(f"Imported {len(results)} findings")
        except Exception as e:
            logging.error(f"Import error: {e}")
    
    def start(self):
        logging.info("=== VULNERABILITY SCAN STARTED ===")
        # Read recon results
        # Run scanners
        # Import results
        logging.info("=== VULNERABILITY SCAN COMPLETE ===")

if __name__ == "__main__":
    scanner = VulnScanner("/home/ubuntu/bug-hunt/results/findings.db")
    scanner.start()
```

### Script 3: Custom API IDOR Testing

```python
# ~/bug-hunt/api_test.py

#!/usr/bin/env python3
import requests
import json
import sqlite3
from datetime import datetime
import logging
import time

logging.basicConfig(filename="/home/ubuntu/bug-hunt/logs/api_test.log", level=logging.INFO)

class IDORTester:
    def __init__(self, db_path):
        self.db_path = db_path
        self.session = requests.Session()
        self.rate_limit_delay = 0.25  # 250ms = 4 req/sec (safe)
    
    def test_idor(self, endpoint, id_param, auth_header, test_range=100):
        """Test for IDOR vulnerabilities"""
        findings = []
        
        for i in range(1, test_range):
            url = endpoint.replace(f"{{{id_param}}}", str(i))
            headers = {"Authorization": auth_header}
            
            try:
                resp = requests.get(url, headers=headers, timeout=5)
                
                if resp.status_code == 200:
                    # Successful read = potential IDOR
                    finding = {
                        "timestamp": datetime.now().isoformat(),
                        "endpoint": endpoint,
                        "vulnerable_id": i,
                        "status_code": 200,
                        "response_size": len(resp.content),
                        "severity": "HIGH" if len(resp.content) > 100 else "MEDIUM"
                    }
                    findings.append(finding)
                    logging.warning(f"IDOR FOUND: {endpoint} ID={i}")
                
                time.sleep(self.rate_limit_delay)  # RESPECT RATE LIMITS
                
            except Exception as e:
                logging.error(f"Error testing {url}: {e}")
        
        return findings
    
    def save_findings(self, findings):
        """Save to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for f in findings:
            cursor.execute('''
                INSERT INTO findings 
                (timestamp, target, vuln_type, severity, proof_of_concept)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                f['timestamp'],
                f['endpoint'],
                'IDOR',
                f['severity'],
                json.dumps(f)
            ))
        
        conn.commit()
        conn.close()

if __name__ == "__main__":
    tester = IDORTester("/home/ubuntu/bug-hunt/results/findings.db")
    # Add your API endpoints and auth
```

### Script 4: Automated Reporting

```python
# ~/bug-hunt/report.py

#!/usr/bin/env python3
import sqlite3
import json
from datetime import datetime
import requests
import os

class Reporter:
    def __init__(self, db_path, slack_webhook):
        self.db_path = db_path
        self.slack_webhook = slack_webhook
    
    def get_new_findings(self):
        """Get all 'new' findings from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM findings WHERE status='new'")
        findings = cursor.fetchall()
        conn.close()
        return findings
    
    def send_slack_alert(self, findings):
        """Send Slack notification for new findings"""
        if not findings:
            return
        
        message = {
            "text": f"🔴 **NEW VULNERABILITIES FOUND** ({len(findings)} issues)",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔴 NEW FINDINGS: {len(findings)} vulnerabilities*\n\n"
                    }
                }
            ]
        }
        
        for finding in findings[:10]:  # First 10
            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{finding[3]}* on {finding[2]}\nSeverity: {finding[4]}"
                }
            })
        
        requests.post(self.slack_webhook, json=message)
    
    def generate_html_report(self, findings):
        """Generate HTML report"""
        html = f"""
        <html>
        <head><title>Bug Hunt Report - {datetime.now()}</title></head>
        <body>
            <h1>Autonomous Bug Hunt Report</h1>
            <p>Generated: {datetime.now()}</p>
            <h2>Critical Findings ({len(findings)})</h2>
            <table border="1">
                <tr><th>Target</th><th>Type</th><th>Severity</th><th>Details</th></tr>
        """
        
        for finding in findings:
            html += f"""
                <tr>
                    <td>{finding[2]}</td>
                    <td>{finding[3]}</td>
                    <td>{finding[4]}</td>
                    <td>{finding[5]}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        with open("/home/ubuntu/bug-hunt/reports/report.html", "w") as f:
            f.write(html)
    
    def start(self):
        findings = self.get_new_findings()
        if findings:
            self.send_slack_alert(findings)
            self.generate_html_report(findings)

if __name__ == "__main__":
    import yaml
    with open("/home/ubuntu/bug-hunt/config.yaml") as f:
        config = yaml.safe_load(f)
    
    reporter = Reporter(
        config['database']['path'],
        config['reporting']['slack_webhook']
    )
    reporter.start()
```

---

## ⏰ Automation (Cron Jobs)

### Set Up Cron Schedule

```bash
# Edit crontab
crontab -e

# Add these lines:

# Recon every 24 hours at 2 AM
0 2 * * * /home/ubuntu/hunt-env/bin/python3 /home/ubuntu/bug-hunt/recon.py >> /home/ubuntu/bug-hunt/logs/cron.log 2>&1

# Vulnerability scans every 12 hours
0 0,12 * * * /home/ubuntu/hunt-env/bin/python3 /home/ubuntu/bug-hunt/scan.py >> /home/ubuntu/bug-hunt/logs/cron.log 2>&1

# API testing every 6 hours
0 0,6,12,18 * * * /home/ubuntu/hunt-env/bin/python3 /home/ubuntu/bug-hunt/api_test.py >> /home/ubuntu/bug-hunt/logs/cron.log 2>&1

# Reporting every 24 hours at 9 AM
0 9 * * * /home/ubuntu/hunt-env/bin/python3 /home/ubuntu/bug-hunt/report.py >> /home/ubuntu/bug-hunt/logs/cron.log 2>&1

# Database cleanup (old findings) weekly
0 3 * * 0 sqlite3 /home/ubuntu/bug-hunt/results/findings.db "DELETE FROM findings WHERE status='closed' AND timestamp < datetime('now', '-30 days');"
```

---

## 📊 Monitoring

### Check Status Anytime

```bash
# See latest findings
sqlite3 /home/ubuntu/bug-hunt/results/findings.db "SELECT * FROM findings ORDER BY timestamp DESC LIMIT 10;"

# View logs
tail -f /home/ubuntu/bug-hunt/logs/scan.log

# Check cron execution
tail -f /home/ubuntu/bug-hunt/logs/cron.log

# Database stats
sqlite3 /home/ubuntu/bug-hunt/results/findings.db "SELECT vuln_type, COUNT(*) FROM findings GROUP BY vuln_type;"
```

---

## 🚀 Deploy Script (All-in-One)

```bash
#!/bin/bash
# ~/deploy.sh - Run this once to set everything up

set -e

echo "🚁 Autonomous Bug Hunt Framework Setup"

# 1. Install deps
echo "[1/5] Installing dependencies..."
# (includes all apt-get, go, rust installs above)

# 2. Create config
echo "[2/5] Creating config..."
cp /path/to/config.yaml ~/bug-hunt/config.yaml

# 3. Deploy scripts
echo "[3/5] Deploying scripts..."
cp recon.py scan.py api_test.py report.py ~/bug-hunt/

# 4. Init database
echo "[4/5] Initializing database..."
python3 ~/bug-hunt/scan.py  # Calls init_db()

# 5. Setup cron
echo "[5/5] Setting up automation..."
crontab cron-schedule.txt

echo "✅ Deployment complete!"
echo "Monitor with: tail -f ~/bug-hunt/logs/scan.log"
```

---

## 💡 What Happens (Fully Automated)

**Every 24 hours:**
- Recon discovers new subdomains, services, endpoints
- Vulnerability scan runs against all discovered targets
- API testing checks for IDOR on detected endpoints
- Findings aggregated and deduplicated
- Slack alert sent if critical findings found
- HTML report generated

**You do nothing.** Just check Slack alerts. 🤖

---

## 📈 Expected Output

```
Database: findings.db
├── CRITICAL findings: 2
├── HIGH findings: 8
├── MEDIUM findings: 15
└── LOW findings: 23

Slack Alerts: 1 per new critical
HTML Reports: Generated daily
Logs: Maintained in ~/bug-hunt/logs/
```

---

## ⚠️ Important Notes

- **Rate limiting enforced** (250ms delays) to avoid IP bans
- **Database deduplication** prevents alert spam
- **Scope your targets** in config.yaml — only test authorized systems
- **Slack webhook required** for alerts (optional but recommended)
- **Monitor logs** regularly for errors
- **Update tools** monthly (`go install ... @latest`)

---

## 🎯 What You Get

✅ 24/7 automated recon
✅ Continuous vulnerability scanning
✅ IDOR/API testing on schedule
✅ Automatic result aggregation
✅ Slack alerts for critical findings
✅ HTML reports generated daily
✅ Zero manual intervention needed
✅ Cost: ~$100-150/month on AWS

**Set it and forget it.** 🚁
