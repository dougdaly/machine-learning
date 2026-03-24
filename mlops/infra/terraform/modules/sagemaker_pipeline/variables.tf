variable "project_name" {
  type = string
}

variable "env" {
  type = string
}

variable "pipeline_role_arn" {
  type = string
}

variable "pipeline_definition_path" {
  type = string
}

variable "raw_bucket_name" {
  type = string
}

variable "output_bucket_name" {
  type = string
}

variable "model_bucket_name" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
