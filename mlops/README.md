# AWS MLOps PoC

Small personal PoC showing a GitHub-to-AWS deployment flow for a trivial processing pipeline.

## Architecture

1. Code is pushed to GitHub
2. GitHub Actions assumes an AWS IAM role via OIDC
3. AWS SAM deploys infrastructure
4. Input JSON is stored in S3
5. Lambda reads input, runs 3 stub processing steps, writes output to another S3 bucket

## Stack

- GitHub Actions
- AWS IAM OIDC trust
- AWS SAM
- AWS Lambda
- Amazon S3

## Repo layout

- `src/` application code
- `infra/` AWS SAM template
- `sample_data/` demo input
- `tests/` unit tests

## Next upgrades

- Add automatic S3-triggered execution
- Replace Lambda with SageMaker Processing
- Add Step Functions orchestration
- Add test and lint stages in CI
