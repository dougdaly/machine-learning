import json
import os
from datetime import datetime, UTC

import boto3

s3 = boto3.client("s3")

OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]


def step1_add_flag(payload: dict) -> dict:
    payload["step1"] = "completed"
    return payload


def step2_count_keys(payload: dict) -> dict:
    payload["step2_key_count"] = len(payload.keys())
    return payload


def step3_add_timestamp(payload: dict) -> dict:
    payload["processed_at_utc"] = datetime.now(UTC).isoformat()
    return payload


def lambda_handler(event, context):
    """
    Expected event:
    {
      "bucket": "input-bucket-name",
      "key": "input/sample.json"
    }
    """
    input_bucket = event["bucket"]
    input_key = event["key"]

    response = s3.get_object(Bucket=input_bucket, Key=input_key)
    raw = response["Body"].read().decode("utf-8")
    payload = json.loads(raw)

    payload = step1_add_flag(payload)
    payload = step2_count_keys(payload)
    payload = step3_add_timestamp(payload)

    output_key = f"processed/{input_key.rsplit('/', 1)[-1]}"
    s3.put_object(
        Bucket=OUTPUT_BUCKET,
        Key=output_key,
        Body=json.dumps(payload, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Processing complete",
                "input_bucket": input_bucket,
                "input_key": input_key,
                "output_bucket": OUTPUT_BUCKET,
                "output_key": output_key,
            }
        ),
    }
