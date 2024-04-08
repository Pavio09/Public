data "aws_iam_policy_document" "ecs_task_execution_assume_role_policy" {
  statement {
    sid = "AssumeRole"

    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ecs_task_execution_policy_document" {
  statement {
    sid = "ECS"

    actions = [
      "ecs:CreateCluster",
      "ecs:DeleteCluster",
      "ecs:runTask",
      "ecs:DescribeTasks"
    ]

    resources = [
      aws_ecs_cluster.fargate_ecs_cluster.arn
    ]
  }

  statement {
    sid = "ECR"

    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = ["*"] #TODO: add aws_ecr_repository.ecr_repository.arn
  }

  statement {
    sid     = "passrole"
    actions = ["iam:PassRole"]
    condition {
      test     = "StringLike"
      variable = "iam:PassedToService"
      values   = ["ecs-tasks.amazonaws.com"]
    }

    resources = ["*"]
  }
}

resource "aws_iam_policy" "ecs_task_execution_access_policy" {
  name   = "${local.full_name_env_app}-ecs-fargate-task-execution-policy"
  path   = "/"
  policy = data.aws_iam_policy_document.ecs_task_execution_policy_document.json

  depends_on = [
    data.aws_iam_policy_document.ecs_task_execution_policy_document
  ]
}

resource "aws_iam_role" "ecs_task_execution_job_role" {
  name               = "${local.full_name_env_app}-ecs-fargate-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_assume_role_policy.json

  depends_on = [
    data.aws_iam_policy_document.ecs_task_execution_assume_role_policy
  ]
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy_attachment" {
  role       = aws_iam_role.ecs_task_execution_job_role.name
  policy_arn = aws_iam_policy.ecs_task_execution_access_policy.arn

  depends_on = [
    aws_iam_role.ecs_task_execution_job_role,
    aws_iam_policy.ecs_task_execution_access_policy
  ]
}
