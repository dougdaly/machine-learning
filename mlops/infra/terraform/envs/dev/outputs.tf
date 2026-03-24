output "raw_bucket_name" {
  value = module.s3.raw_bucket_name
}

output "output_bucket_name" {
  value = module.s3.output_bucket_name
}

output "model_bucket_name" {
  value = module.s3.model_bucket_name
}

output "sagemaker_execution_role_arn" {
  value = module.iam.sagemaker_execution_role_arn
}

output "pipeline_name" {
  value = module.sagemaker_pipeline.pipeline_name
}
