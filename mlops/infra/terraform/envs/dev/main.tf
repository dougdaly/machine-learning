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
  project_name = "digital-twin-resilience"
  env          = "dev"

  common_tags = {
    Project     = local.project_name
    Environment = local.env
    ManagedBy   = "terraform"
  }
}

module "s3" {
  source = "../../modules/s3"

  project_name = local.project_name
  env          = local.env
  tags         = local.common_tags
}

module "iam" {
  source = "../../modules/iam"

  project_name      = local.project_name
  env               = local.env
  raw_bucket_arn    = module.s3.raw_bucket_arn
  output_bucket_arn = module.s3.output_bucket_arn
  tags              = local.common_tags
}

module "sagemaker_pipeline" {
  source = "../../modules/sagemaker_pipeline"

  project_name               = local.project_name
  env                        = local.env
  pipeline_role_arn          = module.iam.sagemaker_execution_role_arn
  pipeline_definition_path   = "${path.module}/../../../pipelines/digital_twin_resilience/pipeline_definition.json"
  raw_bucket_name            = module.s3.raw_bucket_name
  output_bucket_name         = module.s3.output_bucket_name
  model_bucket_name          = module.s3.model_bucket_name
  tags                       = local.common_tags
}
