"""
AWS Lambda handler for BountyScout.
Runs on schedule (daily/weekly via EventBridge).
Sends digest via email (SES) or posts to GitHub/Slack.
"""

import os
import json
import logging
import boto3
from .bounty_scout import BountyScout

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
ses_client = boto3.client("ses")
s3_client = boto3.client("s3")


def lambda_handler(event, context):
    """
    Main Lambda entry point.
    Environment variables:
    - HACKERONE_API_KEY: Optional HackerOne API key
    - BUGCROWD_API_KEY: Optional Bugcrowd API key
    - NOTIFY_EMAIL: Email to send digest to
    - S3_BUCKET: S3 bucket for storing digests
    - DIGEST_FORMAT: 'markdown' or 'json'
    - TOP_N: Number of programs to include (default 5)
    """

    try:
        # Load config
        h1_key = os.getenv("HACKERONE_API_KEY")
        bc_key = os.getenv("BUGCROWD_API_KEY")
        notify_email = os.getenv("NOTIFY_EMAIL")
        s3_bucket = os.getenv("S3_BUCKET")
        digest_format = os.getenv("DIGEST_FORMAT", "markdown")
        top_n = int(os.getenv("TOP_N", 5))

        if not notify_email:
            logger.error("NOTIFY_EMAIL not set")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "NOTIFY_EMAIL required"}),
            }

        logger.info("Starting BountyScout Lambda run")

        # Run scan
        scout = BountyScout(h1_api_key=h1_key, bc_api_key=bc_key)
        output = scout.run_full_scan(
            period="daily",
            top_n=top_n,
            output_format=digest_format,
        )

        # Store in S3 (optional)
        if s3_bucket:
            try:
                from datetime import datetime
                timestamp = datetime.utcnow().isoformat()
                key = f"digests/{timestamp}.{digest_format}"
                s3_client.put_object(
                    Bucket=s3_bucket,
                    Key=key,
                    Body=output.encode("utf-8"),
                    ContentType="application/json" if digest_format == "json" else "text/markdown",
                )
                logger.info(f"Digest stored in S3: s3://{s3_bucket}/{key}")
            except Exception as e:
                logger.warning(f"Failed to store in S3: {e}")

        # Send email
        try:
            send_digest_email(notify_email, output, digest_format)
            logger.info(f"Digest sent to {notify_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"Email send failed: {e}"}),
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "BountyScout scan complete",
                "digest_sent_to": notify_email,
            }),
        }

    except Exception as e:
        logger.exception(f"Lambda error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


def send_digest_email(recipient: str, digest_content: str, format: str) -> None:
    """Send digest via SES."""

    subject = "🐺 BountyScout Daily Digest"

    if format == "json":
        body_text = "Your BountyScout digest is attached as JSON."
        body_html = f"<pre>{json.dumps(json.loads(digest_content), indent=2)}</pre>"
    else:
        body_text = digest_content
        body_html = f"<html><body><pre>{digest_content}</pre></body></html>"

    ses_client.send_email(
        Source=os.getenv("SES_FROM_EMAIL", "noreply@blackhawkyama.dev"),
        Destination={"ToAddresses": [recipient]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Text": {"Data": body_text, "Charset": "UTF-8"},
                "Html": {"Data": body_html, "Charset": "UTF-8"},
            },
        },
    )


def local_handler(event=None, context=None):
    """
    Local testing handler (runs without Lambda).
    Usage: python -c "from bounty_scout.lambda_handler import local_handler; local_handler()"
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()  # Load from .env

    result = lambda_handler(event or {}, context or {})
    print(json.dumps(result, indent=2))
    return result
