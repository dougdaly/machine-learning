# SageMaker Pipeline Feasibility PoC

## Description of directory tree elements

**.github/workflows/**

Deployment-oriented automation.

- **terraform-plan.yml**: generates the SageMaker pipeline definition, runs Terraform fmt/validate/plan on PRs
- **terraform-apply.yml**: generates the SageMaker pipeline definition and applies approved infra changes to dev

Current understanding: these workflows deploy/update infrastructure and the SageMaker pipeline definition, but do not themselves start pipeline execution or run Python tests.

**terraform/**

Infrastructure only.

- **envs/dev/**: environment-specific wiring
- **modules/s3/**: buckets for raw, processed, model artifacts, and evaluation outputs
- **modules/iam/**: execution roles and policies
- **modules/sagemaker_pipeline/**: Terraform resource for the SageMaker Pipeline

Terraform is used to provision/update the SageMaker pipeline resource in AWS.

**mlops/pipelines/digital_twin_resilience/**

Core pipeline orchestration and step logic.

- **pipeline.py**: defines the SageMaker Pipeline DAG and generates `pipeline_definition.json`
- **start_pipeline.py**: starts a SageMaker pipeline execution, with optional parameter overrides
- **check_pipeline_execution.py**: checks overall pipeline execution status and step-level status
- **config.py**: pipeline parameters and defaults
- **steps/processing/processor.py**: generates synthetic data and writes train/validation/test outputs
- **steps/training/train.py**: trains a trivial baseline model
- **steps/evaluation/evaluate.py**: computes evaluation output / trivial metrics
- **utils/**: shared helpers

The current generated pipeline executes three main step scripts:
- `processor.py`
- `train.py`
- `evaluate.py`

**data/synthetic/**

Synthetic input support for the current stub workflow.

- generate fake telemetry
- define a small graph-like structure if needed
- support feasibility-stage testing without real production data

**tests/**

Test area for compile/smoke validation.

- **test_pipeline_compile.py**: intended to validate pipeline compilation
- **test_smoke_synthetic.py**: intended to validate a tiny synthetic end-to-end flow

Current understanding: these tests exist in the repo, but are not currently shown as part of the GitHub Actions workflows reviewed so far.