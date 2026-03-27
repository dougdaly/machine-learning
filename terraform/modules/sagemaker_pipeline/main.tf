resource "aws_sagemaker_pipeline" "this" {
  pipeline_name         = "${var.project_name}-${var.env}-pipeline"
  pipeline_display_name = "${var.project_name}-${var.env}"
  role_arn              = var.pipeline_role_arn

  pipeline_definition = file(var.pipeline_definition_path)
  
  tags = var.tags
}
