variable "aws_region" {
  type        = string
  description = "AWS region for deployment"
  default     = "us-west-2"
}

variable "project_name" {
  type        = string
  description = "Project name"
  default     = "digital-twin-resilience"
}

variable "env" {
  type        = string
  description = "Environment name"
  default     = "dev"
}

variable "sagemaker_execution_role_arn" {
  type        = string
  description = "SageMaker execution role ARN used by the pipeline"
}
