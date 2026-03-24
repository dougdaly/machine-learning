# SageMaker Pipeline Feasibility PoC
## Description of directory tree elements

<b> .github/workflows/ </b></br>
This is CI/CD only. It is not ML logic. GitHub Actions can authenticate to AWS via OIDC instead of long-lived secrets, which is the cleaner enterprise pattern.
<ul>
<li><b>terraform-plan.yml</b>: runs fmt/validate/plan on PRs</li>
<li><b>terraform-apply.yml</b>: applies approved infra changes to dev, maybe later prod</li>
</ul>

<b>infra/terraform/</b></br>
This is infrastructure only.
<ul>
<li><b>envs/dev/</b>: environment-specific wiring</li>
<li><b>modules/s3/</b>: buckets for raw, processed, model artifacts, evaluation outputs</li>
<li><b>modules/iam/</b>: execution roles and policies</li>
<li><b>modules/sagemaker_pipeline/</b>: Terraform resource for the SageMaker Pipeline</li>
</ul>
Terraform has an aws_sagemaker_pipeline resource, so using Terraform for the pipeline object itself is a legitimate pattern, not a workaround.

<b>pipelines/digital_twin_resilience/</b></br>
This is the ML workflow definition.
<ul>
<li><b>pipeline.py</b>: defines the SageMaker Pipeline DAG</li>
<li><b>config.py</b>: pipeline parameters and defaults</li>
<li><b>steps/processing/processor.py</b>: builds datasets or synthetic inputs</li>
<li><b>steps/training/train.py</b>: trains a trivial baseline model first</li>
<li><b>steps/evaluation/evaluate.py</b>: computes metrics and emits a JSON report</li>
<li><b>utils/</b>: shared helpers</li>
</ul>
SageMaker Pipelines is a DAG of interconnected steps, and AWS explicitly supports Processing and Training steps in the pipeline definition.

<b>data/synthetic/</b>

This is discovery-sprint fuel.
<ul>
<li>generate fake telemetry</li>
<li>define a graph-ish structure if needed</li>
<li>keep it tiny and boring</li>
</ul>

<b>tests/</b>
<ul>
<li><b>test_pipeline_compile.py</b>: proves the pipeline definition compiles</li>
<li><b>test_smoke_synthetic.py</b>: one tiny end-to-end synthetic run</li>
</ul>