terraform {
  required_version = ">= 1.6.0"

  backend "s3" {
    bucket       = "dougdaly-terraform-state"
    key          = "entitlements/dev/terraform.tfstate"
    region       = "us-west-2"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}