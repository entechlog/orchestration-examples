# Datadog API key as a secret
resource "aws_secretsmanager_secret" "datadog_api_key" {
  name        = "datadog_api_key"
  description = "API Key for Datadog"
}

resource "aws_secretsmanager_secret_version" "datadog_api_key_version" {
  secret_id     = aws_secretsmanager_secret.datadog_api_key.id
  secret_string = var.datadog_api_key
}

# Task role with Datadog permissions
resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "ecsTaskExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess", # For logging to CloudWatch
  ]
}

# Attach permissions for the Datadog agent
resource "aws_iam_role_policy" "ecs_task_policy" {
  role = aws_iam_role.ecs_task_execution_role.id

  policy = data.aws_iam_policy_document.datadog_permissions.json
}

# ECS Task Definition for Datadog Agent
resource "aws_ecs_task_definition" "datadog_agent" {
  family                   = "datadog-agent-task"
  container_definitions    = jsonencode([
    {
      name  = "datadog-agent"
      image = "datadog/agent:latest"
      environment = [
        {
          name  = "DD_API_KEY"
          valueFrom = aws_secretsmanager_secret.datadog_api_key.arn
        },
        {
          name  = "ECS_FARGATE"
          value = "true"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/datadog-agent"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_execution_role.arn
}

# ECS Service
resource "aws_ecs_service" "datadog_service" {
  name            = "datadog-agent"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.datadog_agent.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnets
    security_groups = var.security_groups
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.datadog.arn
    container_name   = "datadog-agent"
    container_port   = 8125
  }
}

