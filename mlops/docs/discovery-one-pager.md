Discovery Sprint: SageMaker Pipeline Feasibility PoC

Objective

Build a minimal batch SageMaker Pipeline on synthetic telemetry data to validate that the team can define, deploy, and execute a repeatable ML workflow in AWS using the intended GitHub Actions + Terraform delivery path.

Why this exists

The project’s end-state architecture is not fully defined yet, and real telemetry data access is still pending. A synthetic-data pipeline reduces execution risk now by validating the orchestration path before model design and production data contracts are finalized.

What this PoC will prove

We can define a SageMaker Pipeline with multiple dependent steps. SageMaker Pipelines is AWS’s DAG-based orchestration layer for ML workflows.

We can run Processing, Training, and Evaluation stages end to end. AWS documents these as standard pipeline step types.

We can deploy the supporting infrastructure and pipeline resource through Terraform. Terraform supports a SageMaker Pipeline resource.

We can use GitHub Actions as the CI/CD entry point into AWS with OIDC-based authentication.

We can pass artifacts and metrics between steps through S3-backed workflow outputs, and SageMaker supports step-to-step data dependencies and property files for outputs.

What this PoC will not prove

That a GNN is the right modeling choice

That the graph structure is correct

That the eventual telemetry schema is sufficient

That anomaly labels or thresholds are production-ready

That real-time serving is needed or justified

Proposed scope

Three-step batch pipeline:

Processing

generate or load synthetic telemetry

create train/validation/test outputs

write artifacts to S3

Training

train a trivial baseline model

save model artifact and training metrics

Evaluation

score holdout data

write evaluation metrics JSON and summary report

Deliverables

Terraform module or environment config for pipeline deployment

GitHub Actions workflow for Terraform plan/apply

SageMaker Pipeline definition

Synthetic data generator

Minimal processing/training/evaluation scripts

One run showing successful deployment and pipeline execution

Short readout: what worked, what was painful, what needs real-data decisions

Success criteria

Pipeline deploys through the intended infra path

Pipeline executes end to end in SageMaker

Artifacts move correctly between steps

Evaluation output is written and inspectable

The implementation is simple enough to swap synthetic inputs for real telemetry later

Follow-on work after discovery

Replace synthetic data with real telemetry

lock down graph definition

add baseline comparisons

determine whether GNN complexity is justified

decide whether Model Registry / approval gates are needed in the next phase
