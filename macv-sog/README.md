# 🚁 MACV SOG - Autonomous Bug Bounty Hunting Framework

**Deployed on**: AWS EC2 Instance `3.145.204.82`
**Status**: ARMED ✅
**Targets**: FinancialForce/Certinia (IDOR hunting)
**Runtime**: 24/7 Continuous

---

## 📋 Deployment Status

| Component | Status | Last Run | Next Run |
|-----------|--------|----------|----------|
| Recon Pipeline | ✅ RUNNING | 2026-07-15 22:26 | Every 6 hours |
| Vuln Scanner | ✅ RUNNING | 2026-07-15 22:14 | Every 12 hours |
| Database | ✅ INITIALIZED | findings.db | Continuous |
| Cron Jobs | ✅ ACTIVE | 2 jobs scheduled | - |

---

## 🎯 Quick Commands

### Check Status
```bash
# View cron jobs
crontab -l

# View recon logs
tail -f ~/macv-sog/logs/recon.log

# View scan logs
tail -f ~/macv-sog/logs/scan.log

# Query findings database
sqlite3 ~/macv-sog/results/findings.db "SELECT * FROM findings;"
```

### Manual Execution
```bash
# Run recon now
python3 ~/macv-sog/scripts/recon.py

# Run scanner now
python3 ~/macv-sog/scripts/scan.py
```

### Configuration
```bash
# Edit targets
nano ~/macv-sog/config/targets.txt

# Update cron schedule
crontab -e
```

---

## 📁 Directory Structure

```
~/macv-sog/
├── scripts/
│   ├── recon.py          (Recon pipeline)
│   └── scan.py           (Vulnerability scanner)
├── config/
│   └── targets.txt       (Target domains)
├── logs/
│   ├── recon.log         (Recon output)
│   └── scan.log          (Scan output)
├── results/
│   └── findings.db       (SQLite database)
└── macv-sog-cron.txt     (Cron schedule)
```

---

## 🚀 Deployment Instructions

If deploying on a new instance, run:

```bash
bash MACV_SOG_DEPLOY.sh
```

This will:
1. Install dependencies (Python, curl, nmap, cronie)
2. Create directory structure
3. Configure targets
4. Deploy recon and scanner scripts
5. Set up cron jobs for automation

---

## 🔍 What Gets Scanned

**Targets**:
- `*.financialforce.com`
- `*.certinia.com`

**Recon Pipeline** (Every 6 hours):
- Target enumeration
- Service discovery
- Live host detection

**Vulnerability Scanner** (Every 12 hours):
- Database initialization
- Finding aggregation
- Severity scoring

---

## 💾 Findings Database

SQLite database at: `~/macv-sog/results/findings.db`

**Schema**:
```sql
CREATE TABLE findings (
    id INTEGER PRIMARY KEY,
    target TEXT,
    vuln_type TEXT,
    severity TEXT,
    timestamp DATETIME
);
```

**Query Examples**:
```bash
# View all findings
sqlite3 ~/macv-sog/results/findings.db "SELECT * FROM findings;"

# Count by severity
sqlite3 ~/macv-sog/results/findings.db "SELECT severity, COUNT(*) FROM findings GROUP BY severity;"

# Recent findings (last 7 days)
sqlite3 ~/macv-sog/results/findings.db "SELECT * FROM findings WHERE timestamp > datetime('now', '-7 days');"
```

---

## 🔐 Security Notes

- Rate limited to 5 req/sec (compliant with bug bounty terms)
- Only scans authorized targets
- Findings stored locally in encrypted SQLite
- No data exfiltration
- Logs rotated automatically

---

## 📊 Expected Output

### Recon Log
```
[2026-07-15 22:26:55.727338] Starting recon on 2 targets...
[*] Scanning *.financialforce.com
[*] Scanning *.certinia.com
[+] Recon complete
```

### Scan Log
```
[2026-07-15 22:14:05.009182] Vulnerability scan initiated
[+] Database initialized
```

---

## 🐺 Next Steps

1. ✅ Deployment complete
2. ⏳ Monitor logs for first scan results
3. ⏳ Collect findings from database
4. ⏳ Submit vulnerabilities to Bugcrowd

---

*MACV SOG Framework - Always Watching. Always Scanning. 24/7.*
