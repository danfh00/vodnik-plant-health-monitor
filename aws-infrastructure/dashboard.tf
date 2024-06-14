
# ECR / TASK DEFINITION -> SERVICE

# ECR
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
          "value" : var.AWS_SECRET_ACCESS_KEY
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
          "value" : var.AWS_ACCESS_KEY
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

# Data 
data "aws_ecs_cluster" "c11-cluster" {
    cluster_name = "c11-ecs-cluster"
}

data "aws_vpc" "c11-vpc" {
    id = "vpc-04b15cce2398e57f7"
}
data "aws_db_subnet_group" "subnet-group"{
    name = "public_subnet_group_11"
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

