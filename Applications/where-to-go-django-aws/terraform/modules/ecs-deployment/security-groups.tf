# ALB Security Group (Traffic Internet -> ALB)
resource "aws_security_group" "ab_load_balancer" {
  name        = "${local.full_name_env_app}-alb-sg"
  description = "Controls access to the ALB"
  vpc_id      = aws_vpc.backend_project_vpc[0].id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ECS Fargate Security group (traffic ALB -> ECS Fargate Tasks)
resource "aws_security_group" "ecs_fargate" {
  name        = "${local.full_name_env_app}-fargate-sg"
  description = "Allows inbound access from the ALB only"
  vpc_id      = aws_vpc.backend_project_vpc[0].id

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.ab_load_balancer.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
