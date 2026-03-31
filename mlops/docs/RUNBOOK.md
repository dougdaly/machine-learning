# RUNBOOK.md

## Purpose

This runbook explains the current operational understanding of the `mlops/` workflow for the Digital Twin Resilience Model. It is intended to answer practical questions such as:

- Where does the workflow start?
- What is deployment versus execution?
- Which files matter first?
- How do I start a pipeline run?
- How do I check status?

This document uses only information established in the current working session. It is intentionally conservative where details have not yet been verified.

---

## 1. High-level mental model

The current workflow is split into three distinct concerns:

1. **Deployment**
   - GitHub Actions and Terraform generate and deploy the SageMaker pipeline definition and related infrastructure.

2. **Execution**
   - A separate script deliberately starts a SageMaker pipeline execution.

3. **Verification**
   - A separate script asks SageMaker for execution and step-level status.

Important distinction:

- **Deploying the pipeline** is not the same as **running the pipeline**.
- Current understanding is that GitHub Actions handle deployment-related work, but do not themselves start pipeline execution.

---

## 2. Key repo areas

### `.github/workflows/`
Deployment-oriented GitHub Actions workflows.

Relevant files:
- `terraform-plan.yml`
- `terraform-apply.yml`

Current understanding:
- These workflows generate the SageMaker pipeline definition.
- They run Terraform plan/apply logic.
- They provision or update the SageMaker pipeline resource and related infrastructure.
- They do **not** appear to start pipeline execution.
- They do **not** appear to run Python tests based on the workflow files reviewed so far.

### `terraform/`
Infrastructure code.

Relevant areas:
- `terraform/envs/dev/`
- `terraform/modules/s3/`
- `terraform/modules/iam/`
- `terraform/modules/sagemaker_pipeline/`

Current understanding:
- This area manages infrastructure and SageMaker pipeline registration/update.
- This is not where processing, training, or evaluation business logic lives.

### `mlops/pipelines/digital_twin_resilience/`
Core pipeline orchestration area.

Relevant files:
- `pipeline.py`
- `start_pipeline.py`
- `check_pipeline_execution.py`
- `steps/processing/processor.py`
- `steps/training/train.py`
- `steps/evaluation/evaluate.py`

Current understanding:
- `pipeline.py` defines the SageMaker pipeline and generates `pipeline_definition.json`
- `start_pipeline.py` starts a SageMaker pipeline execution
- `check_pipeline_execution.py` checks pipeline execution status
- step scripts contain the logic run by SageMaker during execution

### `data/synthetic/`
Synthetic input support for the current stub workflow.

### `tests/`
Test area exists, but CI wiring has not been confirmed from the workflows reviewed so far.

---

## 3. What happens in GitHub Actions

### `terraform-plan.yml`
Triggered on pull request and manually.

Current understanding:
- checks out code
- sets up Python
- sets up Terraform
- configures AWS credentials
- installs pipeline dependencies
- runs `pipeline.py` to generate the SageMaker pipeline definition
- runs `terraform fmt -check`
- runs `terraform init`
- runs `terraform validate`
- runs `terraform plan`
- uploads the `tfplan` artifact

What it does **not** appear to do:
- start the pipeline
- run Python tests
- run processing/training/evaluation jobs

### `terraform-apply.yml`
Triggered on push to `main` and manually.

Current understanding:
- checks out code
- sets up Python
- sets up Terraform
- configures AWS credentials
- installs pipeline dependencies
- runs `pipeline.py` to generate the SageMaker pipeline definition
- runs `terraform init`
- optionally inspects Terraform state
- runs `terraform apply`

What it does **not** appear to do:
- start the pipeline
- run Python tests
- inspect model outputs

---

## 4. Where the pipeline definition comes from

### `pipeline.py`
Current understanding:
- defines the SageMaker pipeline DAG
- generates `pipeline_definition.json`

This file is part of the deployment/definition side of the workflow.

Important distinction:
- generating `pipeline_definition.json` does **not** start the pipeline
- pretty-printing the JSON does **not** change runtime behavior
- this file defines what the pipeline is, not whether it is currently running

---

## 5. Where pipeline execution starts

### `start_pipeline.py`
This is the current execution entry point.

Current understanding:
- accepts a pipeline name
- optionally accepts parameter overrides such as:
  - `InputDataUri`
  - `RequestConfigUri`
  - `ProcessingInstanceType`
  - `TrainingInstanceType`
  - `EvaluationInstanceType`
- creates a SageMaker client using `boto3`
- calls SageMaker `start_pipeline_execution(...)`

Operational meaning:
- this script starts an execution of a pipeline that is already registered in SageMaker
- it does **not** define the pipeline
- it does **not** deploy infrastructure

### Important distinction
- `pipeline.py` = define the workflow
- Terraform / GitHub Actions = deploy/update the workflow in AWS
- `start_pipeline.py` = run the workflow now

---

## 6. Which scripts the current pipeline executes

From the generated `pipeline_definition.json`, the current pipeline executes these step scripts:

- `processor.py`
- `train.py`
- `evaluate.py`

More specifically, the generated step definitions show container entrypoints for:

- `ProcessSyntheticTelemetry` -> `processor.py`
- `TrainBaselineModel` -> `train.py`
- `EvaluateModel` -> `evaluate.py`

Current understanding of step roles:

### `steps/processing/processor.py`
- generates synthetic data
- populates train / validation / test outputs in S3

### `steps/training/train.py`
- trains a trivial baseline model from synthetic data

### `steps/evaluation/evaluate.py`
- computes evaluation output / trivial metric from the model

Note:
- current understanding is based on the pipeline definition and session review
- step implementation details should still be confirmed by reading the files directly

---

## 7. How status is checked

### `check_pipeline_execution.py`
This is the current status-check entry point.

Current understanding:
- accepts a required `--execution-arn`
- calls SageMaker `describe_pipeline_execution(...)`
- prints overall execution information such as:
  - pipeline ARN
  - execution ARN
  - status
  - creation time
  - last modified time
  - failure reason if present
- calls `list_pipeline_execution_steps(...)`
- prints step-level information such as:
  - step name
  - step status
  - start time
  - end time
  - failure reason if present
  - related processing/training/transform job ARNs when available

Operational meaning:
- this script does not run the pipeline
- it queries SageMaker for the status of an already-started execution

---

## 8. Practical operating flow

Current best understanding of the flow:

### A. Deployment flow
1. Update code in repo
2. GitHub Actions runs `terraform-plan.yml` on PRs
3. `pipeline.py` generates the pipeline definition
4. Terraform validates and plans infra changes
5. After merge, `terraform-apply.yml` runs
6. `pipeline.py` generates the pipeline definition again
7. Terraform applies infra changes and updates the SageMaker pipeline resource

### B. Execution flow
1. Use `start_pipeline.py`
2. Provide pipeline name and optional parameter overrides
3. SageMaker starts a pipeline execution
4. SageMaker runs the defined steps in the registered pipeline

### C. Verification flow
1. Capture the returned `PipelineExecutionArn`
2. Use `check_pipeline_execution.py --execution-arn <arn>`
3. Inspect overall status and step-level status

---

## 9. Where to start if asking "where does the demo start?"

Current practical answer:

### If the question is:
**"Where is the workflow defined?"**
Start with:
- `mlops/pipelines/digital_twin_resilience/pipeline.py`

### If the question is:
**"Where is execution triggered?"**
Start with:
- `mlops/pipelines/digital_twin_resilience/start_pipeline.py`

### If the question is:
**"How do I see what happened?"**
Start with:
- `mlops/pipelines/digital_twin_resilience/check_pipeline_execution.py`

### If the question is:
**"What code does the running pipeline execute?"**
Start with:
- `steps/processing/processor.py`
- `steps/training/train.py`
- `steps/evaluation/evaluate.py`

### If the question is:
**"What deploys the pipeline and infra?"**
Start with:
- `.github/workflows/terraform-plan.yml`
- `.github/workflows/terraform-apply.yml`
- `terraform/`

---

## 10. Current known gaps

The following items are still unresolved or not yet documented in detail:

- exact input data contract
- service graph schema
- first prediction target
- definition of useful model output
- success criteria for REV1
- whether the first serious baseline should be graph-based or simpler
- whether repo tests are currently wired into CI outside the workflow files reviewed so far
- deeper details of `parse_request.py`, `request_schema.py`, and `create_pipeline.py`

---

## 11. Recommended next files to inspect

To deepen current understanding, the next files likely worth examining are:

- `parse_request.py`
- `request_schema.py`
- `create_pipeline.py`
- `steps/processing/processor.py`
- `steps/training/train.py`
- `steps/evaluation/evaluate.py`

---

## 12. Maintenance note

This runbook is intended to capture the current operational understanding of the project.

It should be updated when any of the following change:
- deployment flow
- execution flow
- status-check flow
- main entry-point files
- step behavior
- CI/test integration