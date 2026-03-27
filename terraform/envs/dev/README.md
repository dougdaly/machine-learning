# Local Terraform config

For local runs, create:

`terraform.tfvars`

using:

`terraform.tfvars.example`

Required local value:
- `sagemaker_execution_role_arn`

Example flow:

```bash
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars with your local/personal ARN
terraform init
terraform plan




## 3. Optionally also support env vars

```bash
export TF_VAR_sagemaker_execution_role_arn="arn:aws:iam::123456789012:role/SageMakerExecutionRole-mlops"
