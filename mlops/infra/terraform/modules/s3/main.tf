resource "aws_s3_bucket" "raw" {
  bucket = "${var.project_name}-${var.env}-raw"

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.env}-raw"
  })
}

resource "aws_s3_bucket" "output" {
  bucket = "${var.project_name}-${var.env}-output"

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.env}-output"
  })
}

resource "aws_s3_bucket" "model" {
  bucket = "${var.project_name}-${var.env}-model"

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.env}-model"
  })
}
