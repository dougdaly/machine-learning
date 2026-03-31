# SageMaker Pipeline Feasibility PoC

## Description of directory tree elements

**.github/workflows/**  

This is CI/CD only. It is not ML logic. GitHub Actions can authenticate to AWS via OIDC instead of long-lived secrets, which is the cleaner enterprise pattern.

- **terraform-plan.yml**: runs fmt/validate/plan on PRs
- **terraform-apply.yml**: applies approved infra changes to dev, maybe later prod

**infra/terraform/**  

This is infrastructure only.

- **envs/dev/**: environment-specific wiring
- **modules/s3/**: buckets for raw, processed, model artifacts, evaluation outputs
- **modules/iam/**: execution roles and policies
- **modules/sagemaker_pipeline/**: Terraform resource for the SageMaker Pipeline

 Terraform has an aws_sagemaker_pipeline resource, so using Terraform for the pipeline object itself is a legitimate pattern, not a workaround.



**pipelines/digital_twin_resilience/**  

This is the ML workflow definition.

- **pipeline.py**: defines the SageMaker Pipeline DAG
- **config.py**: pipeline parameters and defaults
- **steps/processing/processor.py**: builds datasets or synthetic inputs
- **steps/training/train.py**: trains a trivial baseline model first
- **steps/evaluation/evaluate.py**: computes metrics and emits a JSON report
- **utils/**: shared helpers

 SageMaker Pipelines is a DAG of interconnected steps, and AWS explicitly supports Processing and Training steps in the pipeline definition.

**data/synthetic/**

This is discovery-sprint fuel.

- generate fake telemetry
- define a graph-ish structure if needed
- keep it tiny and boring

**tests/**

- **test_pipeline_compile.py**: proves the pipeline definition compiles
- **test_smoke_synthetic.py**: one tiny end-to-end synthetic run

