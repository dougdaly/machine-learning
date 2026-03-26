import argparse
import os

import boto3
from dotenv import load_dotenv


load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="Show CloudWatch logs for a SageMaker processing job.")
    parser.add_argument(
        "--processing-job-name",
        type=str,
        required=True,
        help="SageMaker processing job name",
    )
    args = parser.parse_args()

    region = os.environ.get("AWS_REGION", "us-west-2")
    logs = boto3.client("logs", region_name=region)

    log_group = "/aws/sagemaker/ProcessingJobs"
    prefix = args.processing_job_name

    streams = logs.describe_log_streams(
        logGroupName=log_group,
        logStreamNamePrefix=prefix,
    ).get("logStreams", [])
    streams = sorted(
        streams,
        key=lambda s: s.get("lastEventTimestamp", 0),
        reverse=True,
    )
    if not streams:
        print(f"No log streams found in {log_group} for prefix: {prefix}")
        return

    stream_name = streams[0]["logStreamName"]
    print(f"Using log stream: {stream_name}\n")

    next_token = None
    seen_token = None

    while True:
        kwargs = {
            "logGroupName": log_group,
            "logStreamName": stream_name,
            "startFromHead": True,
        }
        if next_token:
            kwargs["nextToken"] = next_token

        response = logs.get_log_events(**kwargs)
        events = response.get("events", [])

        for event in events:
            print(event["message"])

        seen_token = next_token
        next_token = response.get("nextForwardToken")

        if not next_token or next_token == seen_token:
            break


if __name__ == "__main__":
    main()
