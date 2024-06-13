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

# 2 Short-Term Pipeline

# 2.1 EventBridge Scheduler
resource "aws_scheduler_schedule" "pipeline_scheduler" {
  name       = "vodnik-short-term-pipeline-scheduler"
  group_name = default
  description = "schedules the short term pipeline to run daily at 9am"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 9 * * ? *)"

  target {
    arn      = aws_lambda_function.pipeline_lambda.arn
    role_arn = aws_iam_role.will_reporting_scheduler_role.arn
    
  }
}

resource "aws_iam_role" "pipeline_scheduler_role" {
  name = "vodnik-short-term-pipeline-scheduler-role"

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

resource "aws_iam_policy" "scheduler_execute_pipeline_policy" {
  name        = "StartExecutionPolicy"
  description = "Policy to allow scheduler to invoke pipeline lambda function"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "lambda:InvokeFunction",
        Resource = aws_lambda_function.pipeline_lambda.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "scheduler_pipeline_lambda_invoke_policy" {
  role       = aws_iam_role.pipeline_scheduler_role.name
  policy_arn = aws_iam_policy.scheduler_execute_pipeline_policy.arn
}

# -------------------------------------------
# 2.2 Lambda Function
resource "aws_iam_role" "pipeline_lambda_role" {
  name = "c11-will-tf-lambda-role"
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

resource "aws_lambda_function" "pipeline_lambda" {
    function_name = "vodnik-short-term-pipeline"
    role = aws_iam_role.pipeline_lambda_role.arn
    package_type = "Image"
    image_uri = ""
    architectures = ["x86_64"]
    timeout = 20
    environment {
      variables = {
        DB_HOST = var.DB_HOST
        DB_NAME = var.DB_NAME
        DB_PASSWORD = var.DB_PASSWORD
        DB_PORT = var.DB_PORT
        DB_SCHEMA = var.DB_SCHEMA
        DB_USER = var.DB_USER
      }
    }
}


# -------------------------------------------





