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
  description = "schedules the short term pipeline to run daily at 9am"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(* * * * ? *)"

  target {
    arn      = aws_lambda_function.pipeline_lambda.arn
    role_arn = aws_iam_role.pipeline_scheduler_role.arn
    
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
  name        = "vodnik-invoke-pipeline-lambda-policy"
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

# 2.2 Lambda Function
resource "aws_iam_role" "pipeline_lambda_role" {
  name = "vodnik-short-term-pipeline-role"
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

resource "aws_iam_policy" "pipeline_sns_policy" {
  name = "vodnik-short-term-pipeline-sns-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = "SNS:Publish",
      Resource = "arn:aws:sns:eu-west-2:129033205317:vodnik-you-got-mail"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "pipeline_sns_policy_attachment" {
  role       = aws_iam_role.pipeline_lambda_role.name
  policy_arn = aws_iam_policy.pipeline_sns_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_pipeline_rds_access" {
  role       = aws_iam_role.pipeline_lambda_role.name
  policy_arn = aws_iam_policy.lambda_rds_access_policy.arn
}

resource "aws_lambda_function" "pipeline_lambda" {
    function_name = "vodnik-short-term-pipeline"
    role = aws_iam_role.pipeline_lambda_role.arn
    package_type = "Image"
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/vodnik-pipeline:latest"
    architectures = ["x86_64"]
    timeout = 45
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
  name        = "vodnik-invoke-migration-policy"
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
  description = "Policy to allow lambda to leverage s3 bucket"
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

# 4 Dashboard Service
resource "aws_ecr_repository" "dashboard-repo" {
  name                 = "c11-vodnik-plant-dashboard"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = false
  }
}
#  Task definition
data "aws_iam_role" "execution-role" {
    name = "ecsTaskExecutionRole"
}
resource "aws_ecs_task_definition" "c11-vodnik-dashboard" {
  family                = "c11-vodnik-dashboard"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  execution_role_arn = data.aws_iam_role.execution-role.arn
  cpu = 1024
  memory = 2048
  container_definitions = jsonencode([
    {
      name         = "c11-vodnik-dashboard"
      image        = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-vodnik-plant-dashboard:latest"
      essential    = true
      portMappings = [
        {
          containerPort = 8501
          hostPort      = 8501
        }
      ],
      environment : [
        {
          "name" : "SECRET_ACCESS_KEY",
          "value" : var.SECRET_ACCESS_KEY
        },
        {
          "name" : "DB_PORT",
          "value" : "1433"
        },
        {
          "name" : "DB_USER",
          "value" : var.DB_USER
        },
        {
          "name" : "ACCESS_KEY",
          "value" : var.ACCESS_KEY
        },
        {
          "name" : "DB_NAME",
          "value" : var.DB_NAME
        },
        {
          "name" : "DB_HOST",
          "value" : var.DB_HOST
        },
        {
          "name" : "DB_PASSWORD",
          "value" : var.DB_PASSWORD
        }
      ]
      logConfiguration = {
                logDriver = "awslogs"
                options = {
                    "awslogs-create-group" = "true"
                    "awslogs-group" = "/ecs/c11-vodnik-dashboard"
                    "awslogs-region" = "eu-west-2"
                    "awslogs-stream-prefix" = "ecs"
                    }
        }
    },
  ])
}
# ECS SERVICE
# Data: Cluster
data "aws_ecs_cluster" "c11-cluster" {
    cluster_name = "c11-ecs-cluster"
}
# Data: VPC
data "aws_vpc" "c11-vpc" {
    id = "vpc-04b15cce2398e57f7"
}
# Dashboard security group
resource "aws_security_group" "c11-vodnik-dashboard-security_group" {
  name        = "c11-vodnik-dashboard-sg"
  vpc_id      = data.aws_vpc.c11-vpc.id
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 8501
    protocol    = "tcp"
    to_port     = 8501
  }
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 80
    protocol    = "tcp"
    to_port     = 80
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_ecs_service" "c11-vodnik-dashboard-service" {
  name = "c11-vodnik-dashboard-service"
  cluster = data.aws_ecs_cluster.c11-cluster.id
  task_definition = aws_ecs_task_definition.c11-vodnik-dashboard.arn
  desired_count = 1
  launch_type = "FARGATE"
  network_configuration {
    subnets = ["subnet-07de213eeae1f6307", "subnet-0e6c6a8f959dae31a", "subnet-08781450402b81aa2"]
    security_groups = [aws_security_group.c11-vodnik-dashboard-security_group.id]
    assign_public_ip = true
  }
}