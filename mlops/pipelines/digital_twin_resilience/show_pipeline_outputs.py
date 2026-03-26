import argparse
import json
import os

import boto3
from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def list_objects(s3, bucket: str, prefix: str):
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

    objects = []
    for page in pages:
        for obj in page.get("Contents", []):
            objects.append(obj["Key"])
    return objects


def try_print_json_object(s3, bucket: str, key: str):
    if not key.endswith(".json"):
        return

    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read().decode("utf-8")
    print(f"\n=== Contents of {key} ===")
    try:
        parsed = json.loads(body)
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        print(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Show SageMaker pipeline output artifacts in S3.")
    parser.add_argument(
        "--execution-id",
        type=str,
        required=True,
        help="Pipeline execution ID (not full ARN)",
    )
    parser.add_argument(
        "--pipeline-name",
        type=str,
        default=os.environ.get("PIPELINE_NAME"),
        help="Pipeline name",
    )
    args = parser.parse_args()

    if not args.pipeline_name:
        raise ValueError("Missing pipeline name. Set PIPELINE_NAME or pass --pipeline-name.")

    bucket = get_required_env("OUTPUT_BUCKET")
    region = os.environ.get("AWS_REGION", "us-west-2")

    s3 = boto3.client("s3", region_name=region)

    prefix = f"{args.pipeline_name}/{args.execution_id}/"
    print(f"Looking in s3://{bucket}/{prefix}")

    objects = list_objects(s3, bucket, prefix)

    if not objects:
        print("No output objects found.")
        return

    print("\n=== Output Objects ===")
    for key in objects:
        print(key)

    interesting = [k for k in objects if k.endswith("metrics.json") or k.endswith(".json")]
    for key in interesting[:5]:
        try_print_json_object(s3, bucket, key)


if __name__ == "__main__":
    main()
