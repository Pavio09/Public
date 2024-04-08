resource "aws_ecs_cluster" "fargate_ecs_cluster" {
  name = "${local.full_name_env_app}-fargate-ecs-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "fargate_cluster_provider" {
  cluster_name       = aws_ecs_cluster.fargate_ecs_cluster.name
  capacity_providers = ["FARGATE"]

  default_capacity_provider_strategy {
    base              = 0
    weight            = 1
    capacity_provider = "FARGATE"
  }
}

resource "aws_ecs_task_definition" "fargate_task_definition" {
  family                   = "${local.full_name_env_app}-fargate-task-definition"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution_job_role.arn
  task_role_arn            = aws_iam_role.ecs_task_execution_job_role.arn
  cpu                      = 1024
  memory                   = 3072

  container_definitions = jsonencode(
    [
      {
        "name" : "${local.full_name_env_app}",
        "image" : "${local.image_path}:${var.image_tag}",
        "essential" : true,
        "cpu" : 10,
        "memory" : 512,

        "portMappings" : [
          {
            name          = "${local.full_name_env_app}-fargate-8000-tcp"
            protocol      = "tcp"
            containerPort = 8000
            hostPort      = 8000
            appProtocol   = "http"
          }
        ],

        "healthCheck" : {
          command = [
            "CMD-SHELL",
            "curl -f http://0.0.0.0:8000/ || exit 1"
          ],
          interval = 30,
          timeout  = 5,
          retries  = 3
        },

        "logConfiguration" : {
          "logDriver" : "awslogs",
          "options" : {
            "awslogs-group" : "/aws//ecs/${local.full_name_env_app}",
            "awslogs-region" : "${var.region}",
            "awslogs-stream-prefix" : "ecs-fargate-app-log-stream"
          }
        }
      }
    ]
  )

  depends_on = [
    aws_ecs_cluster.fargate_ecs_cluster
  ]

}

resource "aws_ecs_service" "fargate_service" {
  count = var.create_vpc || var.create_load_balancer ? 1 : 0

  name            = "${local.full_name_env_app}-fargate-service"
  cluster         = aws_ecs_cluster.fargate_ecs_cluster.id
  task_definition = aws_ecs_task_definition.fargate_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  load_balancer {
    target_group_arn = aws_lb_target_group.fargate_targat_group_http[0].arn
    container_name   = local.full_name_env_app
    container_port   = 8000
  }

  network_configuration {
    subnets = [
      element(aws_subnet.public_subnets[*].id, count.index)
    ]
    assign_public_ip = true
    security_groups = [
      aws_security_group.ecs_fargate.id
    ]
  }

  depends_on = [
    aws_lb_target_group.fargate_targat_group_http[0],
    aws_ecs_task_definition.fargate_task_definition,
    aws_ecs_cluster.fargate_ecs_cluster
  ]
}
