import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import boto3
import sagemaker
from sagemaker.inputs import TrainingInput
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.workflow.parameters import ParameterString
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
import logging
from config import (
    PIPELINE_MODE,
    PROCESSING_INSTANCE_TYPE_DEFAULT,
    TRAINING_INSTANCE_TYPE_DEFAULT,
    EVALUATION_INSTANCE_TYPE_DEFAULT,
)

logging.getLogger("sagemaker.workflow.utilities").setLevel(logging.ERROR)

def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value

def resolve_pipeline_mode() -> str:
    mode = os.environ.get("PIPELINE_MODE", "stub").strip().lower()
    if mode not in {"stub", "full"}:
        raise ValueError(f"Unsupported PIPELINE_MODE: {mode}")
    return mode

def get_pipeline(
    *,
    region: str,
    role_arn: str,
    input_bucket: str,
    output_bucket: str,
    pipeline_name: str,
) -> Pipeline:
    boto_session = boto3.Session(region_name=region)
    sm_client = boto_session.client("sagemaker")

    sagemaker_session = PipelineSession(
        boto_session=boto_session,
        sagemaker_client=sm_client,
        default_bucket=output_bucket,
    )

    base_dir = Path(__file__).resolve().parent
    pipeline_mode = resolve_pipeline_mode()

    input_data_uri = ParameterString(
        name="InputDataUri",
        default_value=f"s3://{input_bucket}/synthetic/raw/",
    )

    requestConfigUri = ParameterString(
        name="RequestConfigUri",
        default_value=f"s3://{input_bucket}/requests/request.json",
    )

    processing_instance_type = ParameterString(
        name="ProcessingInstanceType",
        default_value=PROCESSING_INSTANCE_TYPE_DEFAULT,
    )

    training_instance_type = ParameterString(
        name="TrainingInstanceType",
        default_value=TRAINING_INSTANCE_TYPE_DEFAULT,
    )

    evaluation_instance_type = ParameterString(
        name="EvaluationInstanceType",
        default_value=EVALUATION_INSTANCE_TYPE_DEFAULT,
    )

    processing_processor = ScriptProcessor(
        image_uri=sagemaker.image_uris.retrieve(
            framework="sklearn",
            region=region,
            version="1.2-1",
            instance_type="ml.t3.medium",
        ),
        command=["python3"],
        role=role_arn,
        instance_count=1,
        instance_type=processing_instance_type,
        sagemaker_session=sagemaker_session,
    )

    step_process = ProcessingStep(
        name="ProcessSyntheticTelemetry",
        processor=processing_processor,
        inputs=[
            ProcessingInput(
                source=input_data_uri,
                destination="/opt/ml/processing/input",
            ),
            ProcessingInput(
                source=requestConfigUri,
                destination="/opt/ml/processing/config",
            ),
        ],
        outputs=[
            ProcessingOutput(
                output_name="train",
                source="/opt/ml/processing/output/train",
            ),
            ProcessingOutput(
                output_name="validation",
                source="/opt/ml/processing/output/validation",
            ),
            ProcessingOutput(
                output_name="test",
                source="/opt/ml/processing/output/test",
            ),
        ],
        code=str(base_dir / "steps" / "processing" / "processor.py"),
    )

    estimator = SKLearn(
        entry_point="train.py",
        source_dir=str(base_dir / "steps" / "training"),
        role=role_arn,
        instance_count=1,
        instance_type=training_instance_type,
        framework_version="1.2-1",
        py_version="py3",
        sagemaker_session=sagemaker_session,
        output_path=f"s3://{output_bucket}/models/",
    )

    if pipeline_mode == "full":
        estimator = SKLearn(
            entry_point="train.py",
            source_dir=str(base_dir / "steps" / "training"),
            role=role_arn,
            instance_count=1,
            instance_type=training_instance_type,
            framework_version="1.2-1",
            py_version="py3",
            sagemaker_session=sagemaker_session,
            output_path=f"s3://{output_bucket}/models/",
        )

        step_train = TrainingStep(
            name="TrainBaselineModel",
            estimator=estimator,
            inputs={
                "train": TrainingInput(
                    s3_data=step_process.properties.ProcessingOutputConfig.Outputs[
                        "train"
                    ].S3Output.S3Uri,
                    content_type="text/csv",
                ),
                "validation": TrainingInput(
                    s3_data=step_process.properties.ProcessingOutputConfig.Outputs[
                        "validation"
                    ].S3Output.S3Uri,
                    content_type="text/csv",
                ),
            },
        )

        model_input_s3_uri = step_train.properties.ModelArtifacts.S3ModelArtifacts

    else:
        training_processor = ScriptProcessor(
            image_uri=sagemaker.image_uris.retrieve(
                framework="sklearn",
                region=region,
                version="1.2-1",
                instance_type="ml.t3.medium",
            ),
            command=["python3"],
            role=role_arn,
            instance_count=1,
            instance_type=training_instance_type,
            sagemaker_session=sagemaker_session,
        )

        step_train = ProcessingStep(
            name="TrainBaselineModel",
            processor=training_processor,
            inputs=[
                ProcessingInput(
                    source=step_process.properties.ProcessingOutputConfig.Outputs[
                        "train"
                    ].S3Output.S3Uri,
                    destination="/opt/ml/processing/train",
                ),
                ProcessingInput(
                    source=step_process.properties.ProcessingOutputConfig.Outputs[
                        "validation"
                    ].S3Output.S3Uri,
                    destination="/opt/ml/processing/validation",
                ),
            ],
            outputs=[
                ProcessingOutput(
                    output_name="model",
                    source="/opt/ml/processing/model",
                )
            ],
            code=str(base_dir / "steps" / "training" / "train.py"),
        )

        model_input_s3_uri = step_train.properties.ProcessingOutputConfig.Outputs[
            "model"
        ].S3Output.S3Uri

    evaluation_processor = ScriptProcessor(
        image_uri=sagemaker.image_uris.retrieve(
            framework="sklearn",
            region=region,
            version="1.2-1",
            instance_type="ml.m5.large",
        ),
        command=["python3"],
        role=role_arn,
        instance_count=1,
        instance_type=evaluation_instance_type,
        sagemaker_session=sagemaker_session,
    )

    step_evaluate = ProcessingStep(
        name="EvaluateModel",
        processor=evaluation_processor,
        inputs=[
            ProcessingInput(
                source=model_input_s3_uri,
                destination="/opt/ml/processing/model",
            ),
            ProcessingInput(
                source=step_process.properties.ProcessingOutputConfig.Outputs[
                    "test"
                ].S3Output.S3Uri,
                destination="/opt/ml/processing/test",
            ),
        ],
        outputs=[
            ProcessingOutput(
                output_name="evaluation",
                source="/opt/ml/processing/evaluation",
            )
        ],
        code=str(base_dir / "steps" / "evaluation" / "evaluate.py"),
    )

    return Pipeline(
        name=pipeline_name,
        parameters=[
            input_data_uri,
            requestConfigUri,
            processing_instance_type,
            training_instance_type,
            evaluation_instance_type,
        ],
        steps=[
            step_process,
            step_train,
            step_evaluate,
        ],
        sagemaker_session=sagemaker_session,
    )


if __name__ == "__main__":
    AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
    SAGEMAKER_ROLE_ARN = get_required_env("SAGEMAKER_ROLE_ARN")
    INPUT_BUCKET = get_required_env("INPUT_BUCKET")
    OUTPUT_BUCKET = get_required_env("OUTPUT_BUCKET")
    PIPELINE_NAME = os.environ.get(
        "PIPELINE_NAME",
        "digital-twin-resilience-dev-pipeline",
    )

    print("Using config:")
    print(f"AWS_REGION={AWS_REGION}")
    print(f"SAGEMAKER_ROLE_ARN={SAGEMAKER_ROLE_ARN}")
    print(f"INPUT_BUCKET={INPUT_BUCKET}")
    print(f"OUTPUT_BUCKET={OUTPUT_BUCKET}")
    print(f"PIPELINE_NAME={PIPELINE_NAME}")

    pipeline = get_pipeline(
        region=AWS_REGION,
        role_arn=SAGEMAKER_ROLE_ARN,
        input_bucket=INPUT_BUCKET,
        output_bucket=OUTPUT_BUCKET,
        pipeline_name=PIPELINE_NAME,
    )

    definition = pipeline.definition()
    out_path = Path(__file__).resolve().parent / "pipeline_definition.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(json.loads(definition), f, indent=2, sort_keys=False)
        f.write("\n")

    print(f"Wrote pipeline definition to {out_path}")