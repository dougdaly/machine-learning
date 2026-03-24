import json
from pathlib import Path

import boto3
import sagemaker
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.workflow.parameters import ParameterString
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.workflow.pipeline_context import PipelineSession


def get_pipeline(
    region: str,
    role_arn: str,
    default_bucket: str,
    pipeline_name: str = "digital-twin-resilience-dev-pipeline",
) -> Pipeline:
    boto_session = boto3.Session(region_name=region)
    sm_client = boto_session.client("sagemaker")
    sagemaker_session = PipelineSession(
        boto_session=boto_session,
        sagemaker_client=sm_client,
        default_bucket=default_bucket,
    )

    input_data_uri = ParameterString(
        name="InputDataUri",
        default_value=f"s3://{default_bucket}/synthetic/raw/"
    )

    processing_instance_type = ParameterString(
        name="ProcessingInstanceType",
        default_value="ml.m5.large"
    )

    training_instance_type = ParameterString(
        name="TrainingInstanceType",
        default_value="ml.m5.large"
    )

    evaluation_instance_type = ParameterString(
        name="EvaluationInstanceType",
        default_value="ml.m5.large"
    )

    # Step 1: processing
    processing_processor = ScriptProcessor(
        image_uri=sagemaker.image_uris.retrieve(
            framework="sklearn",
            region=region,
            version="1.2-1",
            instance_type="ml.m5.large",
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
            )
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
        code=str(
            Path(__file__).parent / "steps" / "processing" / "processor.py"
        ),
    )

    # Step 2: training
    estimator = SKLearn(
        entry_point="train.py",
        source_dir=str(Path(__file__).parent / "steps" / "training"),
        role=role_arn,
        instance_count=1,
        instance_type=training_instance_type,
        framework_version="1.2-1",
        py_version="py3",
        sagemaker_session=sagemaker_session,
        output_path=f"s3://{default_bucket}/models/",
    )

    step_train = TrainingStep(
        name="TrainBaselineModel",
        estimator=estimator,
        inputs={
            "train": sagemaker.inputs.TrainingInput(
                s3_data=step_process.properties.ProcessingOutputConfig.Outputs[
                    "train"
                ].S3Output.S3Uri,
                content_type="text/csv",
            ),
            "validation": sagemaker.inputs.TrainingInput(
                s3_data=step_process.properties.ProcessingOutputConfig.Outputs[
                    "validation"
                ].S3Output.S3Uri,
                content_type="text/csv",
            ),
        },
    )

    # Step 3: evaluation
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
                source=step_train.properties.ModelArtifacts.S3ModelArtifacts,
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
        code=str(
            Path(__file__).parent / "steps" / "evaluation" / "evaluate.py"
        ),
    )

    return Pipeline(
        name=pipeline_name,
        parameters=[
            input_data_uri,
            processing_instance_type,
            training_instance_type,
            evaluation_instance_type,
        ],
        steps=[step_process, step_train, step_evaluate],
        sagemaker_session=sagemaker_session,
    )

if __name__ == "__main__":
    import os

    REGION = os.environ.get("AWS_REGION", "us-west-2")
    ROLE_ARN = os.environ.get("SAGEMAKER_ROLE_ARN", "REPLACE_ME")
    DEFAULT_BUCKET = os.environ.get("DEFAULT_BUCKET", "REPLACE_ME")
    PIPELINE_NAME = os.environ.get(
        "PIPELINE_NAME",
        "digital-twin-resilience-dev-pipeline",
    )

    pipeline = get_pipeline(
        region=REGION,
        role_arn=ROLE_ARN,
        default_bucket=DEFAULT_BUCKET,
        pipeline_name=PIPELINE_NAME,
    )

    definition = pipeline.definition()
    out_path = Path(__file__).parent / "pipeline_definition.json"
    out_path.write_text(definition)
    print(f"Wrote pipeline definition to {out_path}")
