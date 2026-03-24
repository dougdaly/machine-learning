output "raw_bucket_name" {
  value = aws_s3_bucket.raw.bucket
}

output "raw_bucket_arn" {
  value = aws_s3_bucket.raw.arn
}

output "output_bucket_name" {
  value = aws_s3_bucket.output.bucket
}

output "output_bucket_arn" {
  value = aws_s3_bucket.output.arn
}

output "model_bucket_name" {
  value = aws_s3_bucket.model.bucket
}

output "model_bucket_arn" {
  value = aws_s3_bucket.model.arn
}
