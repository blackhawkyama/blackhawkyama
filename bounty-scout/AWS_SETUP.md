# AWS Setup Guide — BountyScout Lambda Deployment

This guide walks you through setting up BountyScout to run autonomously on AWS Lambda, sending you daily bug bounty program digests.

**Total setup time: ~30 minutes**  
**Monthly cost: $0.00-3.00** (well within free tier)

---

## Prerequisites

- AWS Account (free tier)
- (Optional) HackerOne API key, Bugcrowd API key

---

## Step 1: Create IAM Role for Lambda

1. Go to **AWS Console** → **IAM** → **Roles** → **Create Role**
2. Select **AWS Service** → **Lambda** → **Next**
3. Add permissions:
   - **AmazonSESFullAccess** (for sending emails)
   - **AmazonS3FullAccess** (for storing digests)
4. Name: `BountyScoutLambdaRole`
5. Create role

**Copy the Role ARN** (looks like: `arn:aws:iam::123456789:role/BountyScoutLambdaRole`)

---

## Step 2: Set Up SES (Email)

1. Go to **AWS Console** → **Simple Email Service (SES)**
2. **Verify Email Address:**
   - Click "Verified Identities" → "Create Identity"
   - Select "Email address"
   - Enter your email
   - Click verify link in email
3. Note the "From" email (e.g., `your-email@gmail.com`)

*(If in sandbox mode, you need to verify recipient email too)*

---

## Step 3: Create S3 Bucket (optional, for digest history)

1. Go to **AWS Console** → **S3** → **Create Bucket**
2. Name: `blackhawkyama-bounty-digests` (or similar)
3. Keep defaults, create
4. **Note the bucket name**

---

## Step 4: Create Lambda Function

1. Go to **AWS Console** → **Lambda** → **Create Function**
2. **Function name:** `BountyScout`
3. **Runtime:** Python 3.11
4. **Execution role:** Use existing role → Select `BountyScoutLambdaRole`
5. **Create**

---

## Step 5: Add Code to Lambda

1. In the Lambda editor, open `lambda_function.py`
2. Replace with this (or use deployment package approach below):

```python
# lambda_function.py
import sys
import os

# Add package to path (if deployed as zip)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from bounty_scout.lambda_handler import lambda_handler

# AWS will call this
def handler(event, context):
    return lambda_handler(event, context)
```

3. **Save**

---

## Step 6: Set Environment Variables

In Lambda → **Configuration** → **Environment variables**, add:

| Key | Value | Notes |
|-----|-------|-------|
| `NOTIFY_EMAIL` | your-email@gmail.com | Email to receive digests |
| `SES_FROM_EMAIL` | your-email@gmail.com | Verified SES email |
| `S3_BUCKET` | blackhawkyama-bounty-digests | Bucket name (optional) |
| `DIGEST_FORMAT` | markdown | or 'json' |
| `TOP_N` | 5 | Number of programs per digest |
| `HACKERONE_API_KEY` | (if you have it) | Optional |
| `BUGCROWD_API_KEY` | (if you have it) | Optional |

**Save**

---

## Step 7: Increase Lambda Timeout

1. Lambda → **Configuration** → **General Configuration**
2. **Timeout:** 60 seconds (default is 3s, not enough for scraping)
3. **Memory:** 512 MB (default)
4. **Save**

---

## Step 8: Deploy Code (Zip Method)

If you want to deploy from your machine:

```bash
# Install dependencies
pip install -r bounty-scout/requirements.txt -t ./lib

# Copy code
cp -r bounty-scout ./lib/

# Create zip
zip -r lambda_deployment.zip lambda_function.py lib/

# Upload to Lambda
aws lambda update-function-code \
  --function-name BountyScout \
  --zip-file fileb://lambda_deployment.zip
```

Alternatively, use **Lambda console** → **Upload from** → **.zip file** and upload `lambda_deployment.zip`.

---

## Step 9: Create EventBridge Schedule (Trigger)

1. Go to **AWS Console** → **EventBridge** → **Rules** → **Create Rule**
2. **Name:** `BountyScoutDaily`
3. **Rule Type:** Schedule
4. **Schedule Pattern:** `cron(0 8 * * ? *)` (8 AM UTC daily)
   - Or: `cron(0 8 ? * MON *)` (Weekly on Monday)
5. **Target:** Lambda → Select `BountyScout` function
6. **Create**

---

## Step 10: Test the Function

1. Lambda console → **Test**
2. Create test event (can be empty `{}`)
3. Click **Test**
4. Check:
   - **Execution result:** Should return `statusCode: 200`
   - **CloudWatch Logs:** Should show `Digest sent to your-email@gmail.com`
   - **Email:** Check inbox for digest

---

## Troubleshooting

### "No permissions to perform SES:SendEmail"
- Verify SES identity (step 2) and check role has `AmazonSESFullAccess`

### "No programs found"
- Add HackerOne/Bugcrowd API keys for full data
- Without them, public scraping is limited

### "Timeout" (Lambda runs > 60s)
- Increase timeout in Lambda config
- Or disable S3 storage (remove S3_BUCKET env var)

### Lambda won't run
- Check IAM role ARN is correct
- Check environment variables are set
- Check Lambda timeout >= 60 seconds

---

## Customization

### Change Frequency
Edit EventBridge rule schedule:
- `cron(0 */6 * * ? *)` — Every 6 hours
- `cron(0 9 ? * MON,WED,FRI *)` — M/W/F at 9 AM

### Adjust Program Filtering
Edit environment variables:
- `TOP_N` — more/fewer programs
- Add `MIN_SKILL_MATCH=0.7` — only high-confidence matches
- Add `MAX_SATURATION=0.6` — skip saturated programs

### Add Slack Notifications
Modify `lambda_handler.py` to call Slack webhook instead of (or in addition to) email.

---

## Testing Locally

```bash
# Install
pip install -e bounty-scout/

# Test
python -c "from bounty_scout.lambda_handler import local_handler; local_handler()"
```

(Requires `.env` file with env variables)

---

## Cost Breakdown (Monthly)

- Lambda: Free (1M invocations free)
- SES: Free (62k emails free)
- S3: ~$0.05 (negligible for digests)
- **Total: ~$0.00-1.00/month**

---

## Next Steps

1. After first run, check email for digest
2. Review top programs and skill/saturation scores
3. If programs look good, start testing
4. Periodically update `ProgramScorer.DEFAULT_SKILLS` as you learn new techniques

Done! BountyScout now runs daily and sends you only high-ROI targets. 🚁
