provider "aws" {
    region = var.AWS_REGION
    access_key = var.ACCESS_KEY
    secret_key = var.SECRET_ACCESS_KEY
  
}

resource "aws_s3_bucket" "long-term-storage" {
    bucket = var.HISTORICAL_BUCKET_NAME
    force_destroy = true

}