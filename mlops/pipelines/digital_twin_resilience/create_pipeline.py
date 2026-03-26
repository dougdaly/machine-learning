import os
from dotenv import load_dotenv

from pipeline import get_pipeline


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


if __name__ == "__main__":
    region = os.environ.get("AWS_REGION", "us-west-2")
    role_arn = get_required_env("SAGEMAKER_ROLE_ARN")
    input_bucket = get_required_env("INPUT_BUCKET")
    output_bucket = get_required_env("OUTPUT_BUCKET")
    pipeline_name = get_required_env("PIPELINE_NAME")

    pipeline = get_pipeline(
        region=region,
        role_arn=role_arn,
        input_bucket=input_bucket,
        output_bucket=output_bucket,
        pipeline_name=pipeline_name,
    )

    response = pipeline.upsert(role_arn=role_arn)
    print("Pipeline created/updated.")
    print(response)
