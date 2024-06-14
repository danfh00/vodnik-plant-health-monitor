provider "aws" {
    region = var.AWS_REGION
    access_key = var.ACCESS_KEY
    secret_key = var.SECRET_ACCESS_KEY
  
}

# 1 Long-term bucket storage for historical plant readings

resource "aws_s3_bucket" "long_term_storage" {
    bucket = "vodnik-historical-plant-readings"
    force_destroy = true
  
}
# -----------------------------------

# 3 Long-term data migration

# 3.1 Eventbridge Scheduler

resource "aws_scheduler_schedule" "migration_scheduler" {
  name       = "vodnik-long-term-migration-scheduler"
  description = "schedules a data migration to long term s3 bucket storage"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 9 * * ? *)"

  target {
    arn      = aws_lambda_function.migration_lambda.arn
    role_arn = aws_iam_role.migration_scheduler_role.arn
    
  }
}

resource "aws_iam_role" "migration_scheduler_role" {
  name = "vodnik-long-term-migration-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "scheduler.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }]
  })
}

resource "aws_iam_policy" "scheduler_execute_migration_policy" {
  name        = "StartExecutionPolicy"
  description = "Policy to allow scheduler to invoke migration lambda function"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "lambda:InvokeFunction",
        Resource = aws_lambda_function.migration_lambda.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "scheduler_migration_lambda_invoke_policy" {
  role       = aws_iam_role.migration_scheduler_role.name
  policy_arn = aws_iam_policy.scheduler_execute_migration_policy.arn
}


# 3.2 Lambda Function
resource "aws_iam_role" "migration_lambda_role" {
  name = "vodnik-long-term-migration-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda_s3_access_policy" {
  name        = "vodnik-lambda-s3-access-policy"
  description = "Policy to allow scheduler to invoke state machines"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:GetObject","s3:GetObjectAcl", "s3:PutObject","s3:PutObjectAcl","s3:ListBucket","kms:GenerateDataKey"],
        Resource = format("%s/*",aws_s3_bucket.long_term_storage.arn)
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  role       = aws_iam_role.migration_lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_access_policy.arn
}


resource "aws_iam_policy" "lambda_rds_access_policy" {
  name        = "vodnik-lambda-rds-access-policy"
  description = "Policy to allow lambda to leverage database"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["rds:DescribeDBInstances", "rds:Connect","rds:DeleteRecords", "rds:ExecuteStatement"],
        Resource = "arn:aws:rds:eu-west-2:129033205317:db:plants"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_rds_access" {
  role       = aws_iam_role.migration_lambda_role.name
  policy_arn = aws_iam_policy.lambda_rds_access_policy.arn
}

resource "aws_lambda_function" "migration_lambda" {
    function_name = "vodnik-long-term-migration"
    role = aws_iam_role.migration_lambda_role.arn
    package_type = "Image"
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/vodnik-long-term-data-migration:latest"
    architectures = ["x86_64"]
    timeout = 120
    environment {
      variables = {
        DB_HOST = var.DB_HOST
        DB_NAME = var.DB_NAME
        DB_PASSWORD = var.DB_PASSWORD
        DB_USER = var.DB_USER
        STORAGE_BUCKET_NAME = var.STORAGE_BUCKET_NAME
      }
    }
    
}

# ---------------------------------------------

