resource "aws_cloudwatch_log_group" "fargate_log_group" {
  name              = "/aws//ecs/${local.full_name_env_app}"
  retention_in_days = var.log_retention_in_days
}
