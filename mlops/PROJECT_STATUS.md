# PROJECT_STATUS.md

## 1. Project snapshot

- **Project name:** Digital Twin Resilience Model
- **Project goal:** Develop a digital twin of a major streaming platform to simulate system failure, impact radius, and response time.
- **Current objective:** Build toward simulation of the entitlements service using a graph-oriented approach on AWS.
- **Current phase:** Repo and pipeline mechanics clarified. GitHub Actions and Terraform deploy the SageMaker pipeline definition and related infrastructure; pipeline execution is started separately and currently runs a stub synthetic-data workflow.

- **Current status:**

### Deployment
Based on GitHub Actions, `terraform-plan.yml` and `terraform-apply.yml`:
- generate the SageMaker pipeline definition
- provision or update the SageMaker Pipeline resource
- validate Terraform / infra changes

`digital_twin_resilience/pipeline.py`
- defines the SageMaker pipeline
- generates `pipeline_definition.json`

### Execution
`start_pipeline.py`
- starts a specific SageMaker pipeline execution
- allows parameter overrides
- triggers the registered pipeline in AWS

The generated pipeline definition shows three steps:
- `processor.py`
- `train.py`
- `evaluate.py`

`processor.py`
- generates synthetic data
- populates train / validation / test outputs in S3

`train.py`
- builds a trivial baseline model from synthetic data

`evaluate.py`
- computes an evaluation output / trivial metric from the model

### Verification
`check_pipeline_execution.py`
- asks SageMaker for overall pipeline execution status
- lists step-level statuses and related job metadata

### Important distinction
- Deploying the pipeline is separate from executing it.
- Current GitHub Actions deploy and update the pipeline definition and infrastructure.
- Pipeline execution is started deliberately via `start_pipeline.py`.

- **Immediate next step:** Define the minimum set of starter docs and begin filling them in, starting with continuity and framing docs.
- **Biggest current blockers / gaps:**
  - Input data contract is not yet defined
  - Service graph schema is not yet defined
  - Prediction target is not yet defined
  - Definition of "good" model output is not yet defined
  - It is not yet decided whether the first baseline should be graph ML or something simpler

---

## 2. Working understanding of the repo

This section is not a replacement for `repo_skeleton.yml`. It is a quick orientation note describing how the repo is currently understood.

### Repo orientation

- `.github/workflows/`
  - GitHub Actions workflows for Terraform plan/apply and deployment-oriented automation
  - current understanding: deploys pipeline definition and infra, but does not execute the pipeline or run Python tests

- `terraform/`
  - infrastructure code for AWS resources and SageMaker pipeline registration
  - `envs/dev/` contains environment-specific wiring
  - `modules/` contains reusable pieces such as S3, IAM, and SageMaker pipeline setup

- `mlops/pipelines/digital_twin_resilience/`
  - core pipeline orchestration area
  - `pipeline.py` defines the SageMaker pipeline and generates `pipeline_definition.json`
  - `start_pipeline.py` starts a pipeline execution
  - `check_pipeline_execution.py` checks execution status
  - `steps/processing/`, `steps/training/`, and `steps/evaluation/` contain the step logic executed by SageMaker

- `data/synthetic/`
  - synthetic data support for the current stub workflow

- `tests/`
  - test area exists, but CI usage has not yet been confirmed in this document

- `README.md`
  - high-level explanation of repo purpose and structure

### Current understanding
- Deployment and execution are separate concerns
- GitHub Actions currently appear focused on deployment and Terraform validation
- Pipeline execution is started deliberately, not automatically from Terraform apply
- The current pipeline appears to be a stub synthetic processing/training/evaluation flow

### Key files for current understanding

The following files are currently the most relevant for understanding pipeline definition, execution, and verification:

- `pipeline.py`
- `start_pipeline.py`
- `check_pipeline_execution.py`
- `steps/processing/processor.py`
- `steps/training/train.py`
- `steps/evaluation/evaluate.py`

Additional files such as `parse_request.py`, `request_schema.py`, and `create_pipeline.py` are likely important next, but have not yet been examined in detail in this document.

---

## 3. Current working decisions

- Deployment and execution are separate concerns.
- GitHub Actions currently handle pipeline-definition generation and Terraform plan/apply.
- Current GitHub Actions do not appear to start pipeline execution or run Python tests.
- `pipeline.py` generates the SageMaker pipeline definition and writes `pipeline_definition.json`.
- `start_pipeline.py` deliberately starts a SageMaker pipeline execution.
- `check_pipeline_execution.py` checks overall execution status and step-level status through SageMaker APIs.
- The current registered pipeline executes three step scripts: `processor.py`, `train.py`, and `evaluate.py`.
- Early work should focus on framing, contracts, scope, and evaluation before sophisticated model choices.

---

## 4. Open questions

### Core problem / model questions
- What exact decision is the system supposed to support first?
- What is the narrow REV1 scope?
- What is the first prediction target?
- What would count as a useful model output?
- What is the simplest credible baseline for REV1: graph-based, heuristic, tabular, or other?

### Data / entity questions
- What are the core entities?
- What node and edge types belong in the first service graph?
- What data sources are expected to be available?
- What minimum fields are required to support the first end-to-end run?
- What synthetic substitutes are acceptable early on?

### Evaluation questions
- How will success be measured for REV1?
- What does "decision-useful" mean in practice?
- What outputs should `evaluate.py` emit?
- What evidence would justify continuing to the next phase?

### Repo / process questions
- Which starter doc should be written next?
- What should be treated as current truth vs placeholder?
- What is the first code file that should be tightened?

---

## 5. Recommended starter docs from this session

These were identified as the most useful starter docs.

### A. Problem framing doc
Should answer:
- What problem are we solving?
- Who is the decision-maker?
- What is REV1 trying to prove?
- What is explicitly out of scope?

### B. Feasibility questions / hypotheses doc
Should answer:
- What are the major unknowns?
- What do we believe right now?
- What evidence would support or weaken each hypothesis?

### C. REV1 scope and success criteria doc
Should answer:
- What are we building now?
- What are we not building?
- What must be demonstrated?
- What would count as failure or a stop condition?

### D. Data and entity contract doc
Should answer:
- What are the main entities?
- How do they relate?
- What data do we expect?
- What quality risks exist?

### E. Repo/runbook doc
Should answer:
- How is the repo organized?
- How does the flow run?
- What is implemented vs placeholder?
- How should someone orient themselves quickly?

### Note
This `PROJECT_STATUS.md` is not a replacement for those docs. It is the continuity layer that points to them and tracks what is missing.

---

## 6. Guidance agreed in this session

### What not to do
- Do not begin by locking in sophisticated model architecture
- Do not let the repo skeleton create false confidence
- Do not use a polished solution architecture doc as the first anchor
- Do not hide unresolved questions under implementation detail

### What to do first
- Clarify the project/problem framing
- Make the major unknowns explicit
- Define REV1 scope and success criteria
- Build continuity documentation that preserves momentum
- Use this file to keep current status, decisions, open questions, and next actions visible

---

## 7. Next actions

- [ ] Create a first draft of the problem framing doc
- [ ] Create a first draft of the feasibility questions / hypotheses doc
- [ ] Create a first draft of the REV1 scope and success criteria doc
- [ ] Identify the most important data/entity questions for the first pass
- [ ] Decide which current repo file should be examined first for concrete changes

---

## 8. Change log

### Session-created initial version
- Created the first session-only continuity draft of `PROJECT_STATUS.md`
- Purpose: establish a resumable project memory file and expose missing information clearly
- Constraint: uses only information discussed in this session