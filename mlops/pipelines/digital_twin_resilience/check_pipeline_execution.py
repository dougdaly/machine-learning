import argparse
import os
from datetime import datetime

import boto3
from dotenv import load_dotenv


load_dotenv()


def format_dt(value):
    if not value:
        return "N/A"
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check SageMaker pipeline execution status.")
    parser.add_argument(
        "--execution-arn",
        type=str,
        required=True,
        help="Pipeline execution ARN",
    )
    args = parser.parse_args()

    region = os.environ.get("AWS_REGION", "us-west-2")
    sm = boto3.client("sagemaker", region_name=region)

    execution = sm.describe_pipeline_execution(
        PipelineExecutionArn=args.execution_arn
    )

    print("\n=== Pipeline Execution Summary ===")
    print(f"Pipeline ARN: {execution.get('PipelineArn', 'N/A')}")
    print(f"Execution ARN: {execution.get('PipelineExecutionArn', 'N/A')}")
    print(f"Status: {execution.get('PipelineExecutionStatus', 'N/A')}")
    print(f"Created: {format_dt(execution.get('CreationTime'))}")
    print(f"Last Modified: {format_dt(execution.get('LastModifiedTime'))}")

    failure_reason = execution.get("FailureReason")
    if failure_reason:
        print(f"Failure Reason: {failure_reason}")

    print("\n=== Step Statuses ===")
    steps = sm.list_pipeline_execution_steps(
        PipelineExecutionArn=args.execution_arn
    ).get("PipelineExecutionSteps", [])

    if not steps:
        print("No steps found.")
        return

    for step in steps:
        metadata = step.get("Metadata", {})
        print(f"\nStep: {step.get('StepName', 'N/A')}")
        print(f"  Status: {step.get('StepStatus', 'N/A')}")
        print(f"  Start: {format_dt(step.get('StartTime'))}")
        print(f"  End: {format_dt(step.get('EndTime'))}")

        if step.get("FailureReason"):
            print(f"  Failure Reason: {step['FailureReason']}")

        if "ProcessingJob" in metadata:
            print(f"  Processing Job: {metadata['ProcessingJob'].get('Arn', 'N/A')}")
        if "TrainingJob" in metadata:
            print(f"  Training Job: {metadata['TrainingJob'].get('Arn', 'N/A')}")
        if "TransformJob" in metadata:
            print(f"  Transform Job: {metadata['TransformJob'].get('Arn', 'N/A')}")


if __name__ == "__main__":
    main()
