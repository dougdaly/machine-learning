import argparse
import os
from typing import List, Dict

import boto3
from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def build_parameters(
    input_data_uri: str | None,
    request_config_uri: str | None,
    processing_instance_type: str | None,
    training_instance_type: str | None,
    evaluation_instance_type: str | None,
) -> List[Dict[str, str]]:
    parameters: List[Dict[str, str]] = []

    if input_data_uri:
        parameters.append(
            {
                "Name": "InputDataUri",
                "Value": input_data_uri,
            }
        )

    if request_config_uri:
        parameters.append(
            {
                "Name": "RequestConfigUri",
                "Value": request_config_uri,
            }
        )

    if processing_instance_type:
        parameters.append(
            {
                "Name": "ProcessingInstanceType",
                "Value": processing_instance_type,
            }
        )

    if training_instance_type:
        parameters.append(
            {
                "Name": "TrainingInstanceType",
                "Value": training_instance_type,
            }
        )

    if evaluation_instance_type:
        parameters.append(
            {
                "Name": "EvaluationInstanceType",
                "Value": evaluation_instance_type,
            }
        )

    return parameters


def main() -> None:
    parser = argparse.ArgumentParser(description="Start a SageMaker pipeline execution.")
    parser.add_argument(
        "--pipeline-name",
        type=str,
        default=os.environ.get("PIPELINE_NAME"),
        help="SageMaker pipeline name",
    )
    parser.add_argument(
        "--input-data-uri",
        type=str,
        default=None,
        help="Optional override for InputDataUri parameter",
    )
    parser.add_argument(
        "--request-config-uri",
        type=str,
        default=None,
        help="Optional override for RequestConfigUri parameter",
    )
    parser.add_argument(
        "--processing-instance-type",
        type=str,
        default=None,
        help="Optional override for ProcessingInstanceType",
    )
    parser.add_argument(
        "--training-instance-type",
        type=str,
        default=None,
        help="Optional override for TrainingInstanceType",
    )
    parser.add_argument(
        "--evaluation-instance-type",
        type=str,
        default=None,
        help="Optional override for EvaluationInstanceType",
    )

    args = parser.parse_args()

    if not args.pipeline_name:
        raise ValueError("Missing pipeline name. Set PIPELINE_NAME or pass --pipeline-name.")

    region = os.environ.get("AWS_REGION", "us-west-2")
    sm = boto3.client("sagemaker", region_name=region)

    parameters = build_parameters(
        input_data_uri=args.input_data_uri,
        request_config_uri=args.request_config_uri,
        processing_instance_type=args.processing_instance_type,
        training_instance_type=args.training_instance_type,
        evaluation_instance_type=args.evaluation_instance_type,
    )

    print(f"Starting pipeline: {args.pipeline_name}")
    if parameters:
        print("With parameter overrides:")
        for p in parameters:
            print(f"  {p['Name']} = {p['Value']}")
    else:
        print("Using pipeline default parameter values.")

    response = sm.start_pipeline_execution(
        PipelineName=args.pipeline_name,
        PipelineParameters=parameters,
    )

    print("Started pipeline execution.")
    print(f"PipelineExecutionArn: {response['PipelineExecutionArn']}")


if __name__ == "__main__":
    main()
