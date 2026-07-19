"""
AWS Lambda entry point for BountyScout.
Upload this as part of lambda_deployment.zip.
"""

import sys
import os
import json

# Add lib to path for deployed packages
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from bounty_scout.lambda_handler import lambda_handler as scout_handler


def handler(event, context):
    """Lambda handler that delegates to BountyScout."""
    return scout_handler(event, context)


# For local testing
if __name__ == "__main__":
    result = handler({}, {})
    print(json.dumps(result, indent=2))
