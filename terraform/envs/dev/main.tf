terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  project_name = var.project_name
  env          = var.env

  common_tags = {
    Project     = local.project_name
    Environment = local.env
    ManagedBy   = "terraform"
  }
}

module "sagemaker_pipeline" {
  source = "../../modules/sagemaker_pipeline"

  project_name             = local.project_name
  env                      = local.env
  pipeline_role_arn        = var.sagemaker_execution_role_arn
  pipeline_definition_path = "${path.module}/../../../mlops/pipelines/digital_twin_resilience/pipeline_definition.json"
  tags                     = local.common_tags
}
