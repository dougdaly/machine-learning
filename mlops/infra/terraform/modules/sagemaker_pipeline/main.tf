resource "aws_sagemaker_pipeline" "this" {
  pipeline_name         = "${var.project_name}-${var.env}-pipeline"
  pipeline_display_name = "${var.project_name}-${var.env}"
  role_arn              = var.pipeline_role_arn

  pipeline_definition = templatefile(var.pipeline_definition_path, {
    pipeline_name      = "${var.project_name}-${var.env}-pipeline"
    raw_bucket_name    = var.raw_bucket_name
    output_bucket_name = var.output_bucket_name
    model_bucket_name  = var.model_bucket_name
  })

  tags = [
    for k, v in var.tags : {
      key   = k
      value = v
    }
  ]
}
