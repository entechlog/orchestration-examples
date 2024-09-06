# Prefect Datadog API key as a secret
resource "aws_secretsmanager_secret" "prefect_datadog_api_key" {
  name        = "prefect-datadog-api-key-${var.name}"
  description = "API Key for Prefect to access Datadog"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_secretsmanager_secret_version" "prefect_datadog_api_key_version" {
  secret_id     = aws_secretsmanager_secret.prefect_datadog_api_key.id
  secret_string = var.datadog_api_key

  lifecycle {
    prevent_destroy = true
  }
}

# Task role with Datadog permissions
resource "aws_iam_role" "datadog_task_execution_role" {
  name               = "datadog-task-execution-role-${var.name}"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess", # For logging to CloudWatch
  ]
}

# Attach permissions for the Datadog agent
resource "aws_iam_role_policy" "datadog_task_policy" {
  role = aws_iam_role.datadog_task_execution_role.id

  policy = data.aws_iam_policy_document.datadog_permissions.json
}

# ECS Task Definition for Datadog Agent
resource "aws_ecs_task_definition" "datadog_agent_task_definition" {
  family                   = "datadog-agent-${var.name}"
  container_definitions    = jsonencode([
    {
      name  = "datadog-agent-${var.name}"
      image = "datadog/agent:latest"
      environment = [
        {
          name  = "DD_API_KEY"
          valueFrom = aws_secretsmanager_secret.prefect_datadog_api_key.arn
        },
        {
          name  = "ECS_FARGATE"
          value = "true"
        },
        {
          name  = "DD_APM_ENABLED"
          value = "true"
        },
        {
          name  = "DD_LOGS_ENABLED"
          value = "false"
        },
        {
          name  = "DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL"
          value = "false"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/datadog-agent-${var.name}"
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
  execution_role_arn       = aws_iam_role.datadog_task_execution_role.arn
  task_role_arn            = aws_iam_role.datadog_task_execution_role.arn
}

# ECS Service
resource "aws_ecs_service" "datadog_service" {
  name            = "datadog-agent-${var.name}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.datadog_agent_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnets
    security_groups = var.security_groups
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.datadog.arn
    container_name   = "datadog-agent-${var.name}"
    container_port   = 8125
  }
}

# IAM Assume Role Policy for ECS Task Execution Role
data "aws_iam_policy_document" "ecs_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# IAM Policy for Datadog Agent permissions
data "aws_iam_policy_document" "datadog_permissions" {
  statement {
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    actions   = ["ecs:DescribeTasks", "ecs:ListTasks", "ecs:DescribeTaskDefinition", "ecs:DescribeContainerInstances", "ecs:DescribeClusters"]
    resources = ["*"]
  }
}

# Target Group for Datadog metrics and monitoring
resource "aws_lb_target_group" "datadog" {
  name        = "datadog-target-group-${var.name}"
  port        = 8125
  protocol    = "UDP"
  vpc_id      = var.vpc_id
  target_type = "ip"
}

# CloudWatch Log Group for Datadog Agent
resource "aws_cloudwatch_log_group" "datadog_agent_log_group" {
  name              = "/ecs/datadog-agent-${var.name}"
  retention_in_days = 30
}
