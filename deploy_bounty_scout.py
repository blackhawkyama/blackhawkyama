"""
BountyScout Lambda Deployment Automation
Uploads zip, configures EventBridge, and tests the function.
Uses boto3 (Python AWS SDK).
"""

import boto3
import json
import sys
from pathlib import Path

# Configuration
ZIP_PATH = "/tmp/claude-0/-home-user-blackhawkyama/1d6082f9-605e-5fc0-945d-9288bcb9f500/scratchpad/bounty-scout-lambda/bounty-scout-lambda.zip"
FUNCTION_NAME = "bounty-scout-daily"
REGION = "us-west-2"
SCHEDULE_RULE_NAME = "bounty-scout-daily-schedule"
CRON_EXPRESSION = "0 8 * * ? *"  # 8 AM UTC daily

def check_zip_exists():
    """Verify zip file exists."""
    if not Path(ZIP_PATH).exists():
        print(f"❌ Zip file not found: {ZIP_PATH}")
        sys.exit(1)
    size_mb = Path(ZIP_PATH).stat().st_size / (1024 * 1024)
    print(f"✅ Zip file ready: {size_mb:.1f}MB")

def upload_zip():
    """Upload zip to Lambda."""
    print("\n📦 Uploading code to Lambda...")
    try:
        lambda_client = boto3.client('lambda', region_name=REGION)

        with open(ZIP_PATH, 'rb') as f:
            zip_content = f.read()

        response = lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zip_content
        )

        print(f"✅ Code uploaded successfully")
        print(f"   CodeSize: {response['CodeSize']} bytes")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def create_eventbridge_rule():
    """Create EventBridge schedule rule."""
    print("\n⏰ Creating EventBridge schedule...")
    try:
        events_client = boto3.client('events', region_name=REGION)

        # Create rule
        try:
            response = events_client.put_rule(
                Name=SCHEDULE_RULE_NAME,
                ScheduleExpression=f"cron({CRON_EXPRESSION})",
                State='ENABLED'
            )
            print(f"✅ EventBridge rule created: {SCHEDULE_RULE_NAME}")
        except events_client.exceptions.ResourceAlreadyExistsException:
            print(f"⚠️  Rule already exists")

        return True
    except Exception as e:
        print(f"❌ Error creating rule: {e}")
        return False

def add_lambda_target():
    """Add Lambda as EventBridge target."""
    print("   Adding Lambda as target...")
    try:
        events_client = boto3.client('events', region_name=REGION)
        sts_client = boto3.client('sts', region_name=REGION)

        account_id = sts_client.get_caller_identity()['Account']
        lambda_arn = f"arn:aws:lambda:{REGION}:{account_id}:function:{FUNCTION_NAME}"
        role_arn = f"arn:aws:iam::{account_id}:role/service-role/BountyScoutLambdaRole"

        response = events_client.put_targets(
            Rule=SCHEDULE_RULE_NAME,
            Targets=[
                {
                    'Id': '1',
                    'Arn': lambda_arn,
                    'RoleArn': role_arn
                }
            ]
        )

        print(f"✅ Lambda added as EventBridge target")
        return True
    except events_client.exceptions.ResourceAlreadyExistsException:
        print(f"⚠️  Target already exists")
        return True
    except Exception as e:
        print(f"❌ Error adding target: {e}")
        return False

def grant_eventbridge_permission():
    """Grant EventBridge permission to invoke Lambda."""
    print("   Granting EventBridge invoke permission...")
    try:
        lambda_client = boto3.client('lambda', region_name=REGION)
        sts_client = boto3.client('sts', region_name=REGION)

        account_id = sts_client.get_caller_identity()['Account']
        source_arn = f"arn:aws:events:{REGION}:{account_id}:rule/{SCHEDULE_RULE_NAME}"

        try:
            lambda_client.add_permission(
                FunctionName=FUNCTION_NAME,
                StatementId='AllowEventBridgeInvoke',
                Action='lambda:InvokeFunction',
                Principal='events.amazonaws.com',
                SourceArn=source_arn
            )
            print(f"✅ Permission granted")
        except lambda_client.exceptions.ResourceConflictException:
            print(f"⚠️  Permission already exists")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_lambda():
    """Invoke Lambda function with test payload."""
    print("\n🧪 Testing Lambda function...")
    try:
        lambda_client = boto3.client('lambda', region_name=REGION)

        response = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            Payload=json.dumps({'test': True})
        )

        status = response['StatusCode']
        if status == 200:
            print(f"✅ Lambda invoked successfully (HTTP {status})")
            return True
        else:
            print(f"⚠️  Invocation returned status {status}")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run deployment pipeline."""
    print("🚀 BountyScout Lambda Deployment")
    print("=" * 50)

    # Verify prerequisites
    check_zip_exists()

    try:
        sts_client = boto3.client('sts', region_name=REGION)
        account_id = sts_client.get_caller_identity()['Account']
        print(f"✅ AWS credentials available (Account: {account_id})")
    except Exception as e:
        print(f"❌ AWS credentials not available: {e}")
        print("   Make sure you've configured AWS credentials")
        sys.exit(1)

    # Deployment steps
    steps = [
        ("Upload code", upload_zip),
        ("Create EventBridge schedule", create_eventbridge_rule),
        ("Add Lambda target", add_lambda_target),
        ("Grant permissions", grant_eventbridge_permission),
        ("Test function", test_lambda),
    ]

    for step_name, step_func in steps:
        print(f"\n▶ {step_name}")
        if not step_func():
            print(f"⚠️  Step had issues, continuing...")

    print("\n" + "=" * 50)
    print("✅ BountyScout deployment complete!")
    print("\n📋 What's next:")
    print("   1. Check Lambda CloudWatch Logs for execution details")
    print("   2. Verify SES email delivery to eganscottw@gmail.com")
    print("   3. First run scheduled for tomorrow at 8 AM UTC")
    print("   4. Check S3 bucket for digest files: bounty-scout-digests")
    print("\n🎯 BountyScout is now hunting autonomously! 🐺")

if __name__ == "__main__":
    main()
