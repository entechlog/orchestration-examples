variable "datadog_api_key" {
  type    = string
  default = ""
}

# Prefect Datadog API key as a secret
resource "aws_secretsmanager_secret" "prefect_datadog_api_key" {
  name                    = "prefect-datadog-api-key"
  description             = "API Key for Prefect to access Datadog"
  recovery_window_in_days = 0

}

resource "aws_secretsmanager_secret_version" "prefect_datadog_api_key_version" {
  secret_id     = aws_secretsmanager_secret.prefect_datadog_api_key.id
  secret_string = var.datadog_api_key

}

# Task role with Datadog permissions for Prefect
resource "aws_iam_role" "prefect_datadog_task_execution_role" {
  name               = "prefect-datadog-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess", # For logging to CloudWatch
  ]
}

########################
# Secret Manager policy for Prefect
########################
data "aws_iam_policy_document" "prefect_read_datadog_api_key" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "ssm:GetParameters"
    ]
    resources = [
      aws_secretsmanager_secret.prefect_datadog_api_key.arn
    ]
  }
}

# Attach permissions for Secret Manager
resource "aws_iam_role_policy" "prefect_read_datadog_api_key" {
  name   = "prefect-read-datadog-api-key"
  role   = aws_iam_role.prefect_datadog_task_execution_role.name
  policy = data.aws_iam_policy_document.prefect_read_datadog_api_key.json
}

# Attach permissions for the Datadog agent for Prefect
resource "aws_iam_role_policy" "prefect_datadog_task_policy" {
  role = aws_iam_role.prefect_datadog_task_execution_role.id

  policy = data.aws_iam_policy_document.datadog_permissions.json
}

# ECS Task Definition for Datadog Agent used by Prefect
resource "aws_ecs_task_definition" "prefect_datadog_agent_task_definition" {
  family = "prefect-datadog-agent"
  container_definitions = jsonencode([
    {
      name  = "prefect-datadog-agent"
      image = "datadog/agent:latest"
      secrets = [
        {
          name      = "DD_API_KEY"
          valueFrom = aws_secretsmanager_secret.prefect_datadog_api_key.arn
        }
      ]
      environment = [
        {
          "name" : "DD_SITE",
          "value" : "us5.datadoghq.com"
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
        },
        {
          "name" : "DD_DOGSTATSD_NON_LOCAL_TRAFFIC",
          "value" : "true" // Allow DogStatsD to listen for metrics from all tasks
        },
        {
          "name" : "DD_AUTODISCOVERY",
          "value" : "true" // Enable Autodiscovery
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/prefect-datadog-agent"
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
  execution_role_arn       = aws_iam_role.prefect_datadog_task_execution_role.arn
  task_role_arn            = aws_iam_role.prefect_datadog_task_execution_role.arn
}

# ECS Service for Datadog Agent used by Prefect
resource "aws_ecs_service" "prefect_datadog_service" {
  name            = "prefect-datadog-agent"
  cluster         = module.prefect_ecs_cluster.prefect_worker_cluster_name
  task_definition = aws_ecs_task_definition.prefect_datadog_agent_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = module.prefect_vpc.private_subnet_id
    security_groups = [module.prefect_ecs_cluster.prefect_worker_security_group]
  }
}

# IAM Assume Role Policy for Prefect ECS Task Execution Role
data "aws_iam_policy_document" "ecs_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# IAM Policy for Prefect Datadog Agent permissions
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

# CloudWatch Log Group for Prefect Datadog Agent
resource "aws_cloudwatch_log_group" "prefect_datadog_agent_log_group" {
  name              = "/ecs/prefect-datadog-agent"
  retention_in_days = 30
}