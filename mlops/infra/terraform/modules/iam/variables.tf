variable "project_name" {
  type = string
}

variable "env" {
  type = string
}

variable "raw_bucket_arn" {
  type = string
}

variable "output_bucket_arn" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
