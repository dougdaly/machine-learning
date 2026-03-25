import os
import json
import boto3
from dotenv import load_dotenv

# Checks the connection to AWS bedrock and verifies a basic run can happen

load_dotenv()

region = os.environ.get("AWS_REGION", "us-west-2")
model_id = os.environ.get("BEDROCK_MODEL_ID")

if not model_id:
    raise ValueError("Missing BEDROCK_MODEL_ID in .env")

client = boto3.client("bedrock-runtime", region_name=region)

response = client.converse(
    modelId=model_id,
    messages=[
        {
            "role": "user",
            "content": [
                {"text": "Say hello in five words."}
            ],
        }
    ],
)

print(json.dumps(response, indent=2, default=str))
