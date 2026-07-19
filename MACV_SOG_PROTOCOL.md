# 🚁 MACV SOG PROTOCOL

> **Military Assistance Command, Vulnerability Operations - Special Operations Group**
> 
> *Autonomous 24/7 Security Testing Framework*

---

## 📖 Protocol Definition

**MACV SOG** = Launch autonomous security testing framework on AWS

**When you say:** "Launch MACV SOG"
**What happens:** 
- Automated recon pipeline starts
- Continuous vulnerability scanning begins
- IDOR/API testing executes on schedule
- Results aggregate to database
- Slack alerts fire on findings
- HTML reports generate daily
- **Zero manual intervention**

---

## 🎯 MACV SOG Status Codes

| Code | Status | Action |
|------|--------|--------|
| **MACV SOG ARMED** | ✅ Framework deployed, running | Monitor Slack/logs |
| **MACV SOG ACTIVE** | 🔴 Scan in progress | Let it run |
| **MACV SOG ALERT** | 🚨 Critical findings detected | Review Slack notifications |
| **MACV SOG STAND DOWN** | ⏹️ Framework paused | Stop cron jobs |
| **MACV SOG REARM** | 🔄 Restart framework | Deploy.sh again |

---

## 🚀 Quick Deploy (MACV SOG LAUNCH)

### One-Liner Deployment:

```bash
# Clone repo
git clone https://github.com/blackhawkyama/blackhawkyama.git
cd blackhawkyama

# Deploy MACV SOG
bash MACV_SOG_deploy.sh

# Status
echo "MACV SOG ARMED"
```

### What Gets Deployed:

```
MACV SOG Framework
├── Recon Service (24h interval)
├── Vuln Scanning (12h interval)
├── API Testing (6h interval)
├── Result Aggregator (continuous)
├── Slack Alerts (on findings)
└── HTML Reports (daily)
```

---

## 📊 MACV SOG Command Reference

### Deploy (First Time)

```bash
# Launch MACV SOG on AWS EC2
bash ~/bug-hunt/MACV_SOG_deploy.sh
```

### Monitor (Anytime)

```bash
# Check status
tail -f ~/bug-hunt/logs/scan.log

# Recent findings
sqlite3 ~/bug-hunt/results/findings.db "SELECT * FROM findings ORDER BY timestamp DESC LIMIT 10;"

# Database stats
sqlite3 ~/bug-hunt/results/findings.db "SELECT vuln_type, COUNT(*) FROM findings GROUP BY vuln_type;"
```

### Control

```bash
# MACV SOG STAND DOWN (pause all tasks)
crontab -e  # Comment out cron lines

# MACV SOG REARM (restart)
crontab MACV_SOG_cron.txt

# Clear old findings
sqlite3 ~/bug-hunt/results/findings.db "DELETE FROM findings WHERE status='closed' AND timestamp < datetime('now', '-30 days');"
```

---

## 🎯 MACV SOG Configuration

Edit: `~/bug-hunt/config.yaml`

```yaml
# Target domains/IPs
targets:
  - "your-target.com"
  - "api.your-target.com"

# Slack webhook for alerts
reporting:
  slack_webhook: "https://hooks.slack.com/services/YOUR/WEBHOOK"

# Scan intervals (hours)
scanning:
  recon_interval: 24
  vuln_scan_interval: 12
  api_test_interval: 6
  rate_limit: 5  # req/sec
```

---

## 📈 MACV SOG Output

**Slack Alerts** (on findings):
```
🔴 MACV SOG ALERT: 3 critical vulnerabilities detected
- IDOR on /api/v1/invoices
- SQLi on /search endpoint
- Auth bypass on /admin
```

**Database** (auto-aggregated):
```
findings.db
├── CRITICAL: 5
├── HIGH: 12
├── MEDIUM: 28
└── LOW: 47
```

**Reports** (daily HTML):
```
~/bug-hunt/reports/report.html
- All findings organized by severity
- Target grouped
- Timeline included
```

---

## 🔧 MACV SOG Components

### 1. Recon Service
- Discovers subdomains (subfinder)
- Port scanning (nmap)
- Service detection (nmap -sV)
- Live host probing (httpx)

### 2. Vulnerability Scanner
- Nuclei (template-based scanning)
- SQLMap (SQL injection)
- Custom API tests (IDOR, auth bypass)

### 3. Result Aggregator
- SQLite database
- Deduplication (no duplicate alerts)
- Severity scoring
- Status tracking

### 4. Reporting Engine
- Slack webhook integration
- HTML report generation
- JSON export (machine-readable)

### 5. Scheduler
- Cron-based timing
- Non-overlapping tasks
- Automatic retry on failure

---

## ⚙️ MACV SOG Specifications

| Spec | Value |
|------|-------|
| **Deployment Target** | AWS EC2 (t3.large recommended) |
| **Operating System** | Ubuntu 22.04 LTS |
| **Runtime** | 24/7 continuous |
| **Recon Cycle** | Every 24 hours |
| **Scan Cycle** | Every 12 hours |
| **API Test Cycle** | Every 6 hours |
| **Rate Limit** | 5 req/sec (enforced) |
| **Cost** | ~$100-150/month |
| **Manual Effort** | 0% (fully autonomous) |

---

## 🚨 MACV SOG Rules of Engagement

✅ **AUTHORIZED TARGETS ONLY**
- Own infrastructure
- Authorized bug bounty programs
- Penetration testing engagements
- Security research (with permission)

❌ **NEVER**
- Unauthorized access
- Targets outside scope
- Denial of Service
- Data exfiltration

---

## 📝 MACV SOG Protocol Initiation

**To launch MACV SOG, state:**

```
"Launch MACV SOG on [AWS Instance IP]"
or
"MACV SOG ARMED" (if already deployed)
or
"Status MACV SOG" (check current state)
```

**I will respond with:**
- Deployment status
- Finding summary
- Next actions

---

## 🐺 MACV SOG Status Dashboard

```
╔════════════════════════════════════╗
║     MACV SOG - STATUS REPORT       ║
╠════════════════════════════════════╣
║ Status:        ARMED ✅            ║
║ Last Recon:    2 hours ago         ║
║ Last Scan:     1 hour ago          ║
║ Critical:      2 findings          ║
║ High:          5 findings          ║
║ Next Scan:     in 11 hours         ║
╚════════════════════════════════════╝
```

---

## 🎯 Quick Reference

| Command | What It Does |
|---------|--------------|
| `Launch MACV SOG` | Deploy framework on AWS |
| `MACV SOG STATUS` | Check current state |
| `MACV SOG ALERT` | View latest critical findings |
| `MACV SOG REARM` | Restart all services |
| `MACV SOG STAND DOWN` | Pause operations |
| `MACV SOG CONFIG` | Update settings |

---

## 🚀 Getting Started

1. **Deploy MACV SOG** (first time only)
   ```bash
   bash MACV_SOG_deploy.sh
   ```

2. **Configure targets** in `config.yaml`

3. **Set Slack webhook** for alerts

4. **Monitor** via logs and Slack

5. **Done.** MACV SOG runs 24/7 autonomously.

---

## 🐺 Remember

**MACV SOG = Fire and Forget Security Testing**

Set it up once, monitor findings, collect bounties.

**Protocol established.** Ready to launch? 🚁

---

*MACV SOG - Always Watching. Always Scanning. 24/7.*
