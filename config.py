import boto3
import json
import os
import logging

logger = logging.getLogger(__name__)

def get_secret(secret_name):
    """Fetch secret values from AWS Systems Manager (SSM) Parameter Store."""
    session = boto3.session.Session()
    ssm = session.client("ssm", region_name=os.getenv("AWS_REGION", "us-east-2"))

    try:
        response = ssm.get_parameter(Name=secret_name, WithDecryption=True)
        return json.loads(response["Parameter"]["Value"])
    except Exception as e:
        logger.error(f"Error fetching secret {secret_name} from SSM: {str(e)}")
        return {}

# ✅ Load Secrets
secrets = get_secret("RealtyEnrichSecrets")

# ✅ Environment Variables
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY") or secrets.get("STRIPE_SECRET_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or secrets.get("JWT_SECRET_KEY")
SCRAPEAK_API_KEY = os.getenv("SCRAPEAK_API_KEY") or secrets.get("SCRAPEAK_API_KEY")
GOOGLE_CX_ID = os.getenv("GOOGLE_CX_ID") or secrets.get("GOOGLE_CX_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or secrets.get("GOOGLE_API_KEY")

# ✅ AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
DYNAMODB_TABLE = "RealtyEnrichUsers"
