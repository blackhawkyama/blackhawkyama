# 🎯 Bug Bounty Program Tracker

> Structured hunting for maximum earnings. Track scope, findings, submissions, and bounties.

---

## 📋 Program Overview

| Field | Value |
|-------|-------|
| **Platform** | Bugcrowd |
| **Program** | [Program Name] |
| **Status** | Active |
| **Start Date** | 2026-07-05 |
| **Target Scope** | [URL/domain] |
| **Total Target Bounty** | $[amount] |
| **Earnings So Far** | $0 |

---

## 🎯 Scope & Rules

### In Scope
- [ ] Web application vulnerabilities
- [ ] API endpoints
- [ ] Authentication/authorization flaws
- [ ] Data exposure
- [ ] Business logic bypass

### Bounty Tiers
| Severity | Bounty Range | Example |
|----------|--------------|---------|
| **Critical** | $5,000+ | RCE, full account takeover, data breach |
| **High** | $1,000–$4,999| IDOR, privilege escalation, auth bypass |
| **Medium** | $300–$999 | XSS, CSRF, SQL injection |
| **Low** | $100–$299 | Info disclosure, weak headers |

### Out of Scope
- [ ] Social engineering / phishing
- [ ] Denial of Service (DoS)
- [ ] Physical security
- [ ] Third-party services

---

## 🔍 Methodology & Workflow

### Phase 1: Recon
- [ ] Subdomain enumeration (subfinder, assetfinder, crt.sh)
- [ ] WAF detection (wafw00f)
- [ ] Port scanning (nmap)
- [ ] Technology stack identification (Wappalyzer)
- [ ] Screenshot & content analysis

### Phase 2: Vulnerability Assessment
- [ ] Burp Suite active/passive scans
- [ ] Manual authentication testing
- [ ] API endpoint mapping & testing
- [ ] GraphQL introspection (if applicable)
- [ ] IDOR/BOLA testing
- [ ] Access control matrix

### Phase 3: Exploitation
- [ ] Reproduce findings
- [ ] Document proof of concept (PoC)
- [ ] Assess real-world impact
- [ ] Verify scope compliance

### Phase 4: Submission
- [ ] Write clear, reproducible report
- [ ] Provide step-by-step PoC
- [ ] Screenshot/video walkthrough
- [ ] Submit to Bugcrowd
- [ ] Track submission date & status

---

## 📊 Findings Tracker

### Active Findings

| ID | Type | Severity | Status | Target | PoC Ready | Submitted | Bounty |
|----|------|----------|--------|--------|-----------|-----------|--------|
| #001 | [type] | Critical | In Progress | [url] | [ ] | [ ] | TBD |
| #002 | [type] | High | Recon | [url] | [ ] | [ ] | TBD |

### Submission History

| Finding | Severity | Submitted | Status | Bounty | Notes |
|---------|----------|-----------|--------|--------|-------|
| - | - | - | - | - | - |

---

## 🛠️ Tools & Resources

**Enumeration**
```bash
subfinder -d [domain] -all
assetfinder [domain]
crt.sh -- query
masscan -p1-65535 [ip]
nmap -sV -p- [ip]
```

**Web Application Testing**
- Burp Suite Pro (Repeater, Intruder, Decoder)
- Ffuf (directory fuzzing)
- SQLmap (SQL injection)
- OWASP ZAP

**GraphQL Testing** (if applicable)
- GraphQL introspection (if enabled)
- Harvest operations from traffic
- Test batching & IDOR abuse

**API Testing**
- Postman / Insomnia
- Burp API testing extension
- Custom Python scripts (requests, httpx)

---

## 📈 Progress & Earnings

### Monthly Breakdown
| Month | Findings | Submissions | Accepted | Bounty Earned |
|-------|----------|-------------|----------|---------------|
| July 2026 | 0 | 0 | 0 | $0 |

### Lifetime Stats
- **Total Findings:** 0
- **Total Submissions:** 0
- **Accepted Rate:** 0%
- **Lifetime Earnings:** $0

---

## 🎬 Session Notes

### Current Session (2026-07-05)
- [ ] Set up reconnaissance
- [ ] Identify testing targets
- [ ] Begin vulnerability scanning
- [ ] Document findings

---

## 🔗 Quick Links
- [Bugcrowd Program](https://bugcrowd.com)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [HackerOne Disclosure Guidelines](https://www.hackerone.com/disclosure-guidelines)

---

## ⚖️ Remember
- ✅ Stay in scope
- ✅ Test only authorized systems
- ✅ Document everything
- ✅ Clear, reproducible PoCs = higher acceptance
- ✅ Respect embargo & disclosure timelines
- ✅ Coordinated disclosure = reputation + future programs
