locals {
  load_balancer_count = var.create_load_balancer && local.len_private_subnets >= length(var.availability_zone)
}

# Application Load Balancer
resource "aws_lb" "fargate_alb" {
  count = local.load_balancer_count ? length(var.availability_zone) : 0

  name               = "${local.full_name_env_app}-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.ab_load_balancer.id]
  subnets            = aws_subnet.public_subnets[*].id

  depends_on = [
    aws_security_group.ab_load_balancer
  ]
}

# Target group for ECS Fargate
resource "aws_lb_target_group" "fargate_targat_group_http" {
  count = var.create_vpc || var.create_load_balancer ? 1 : 0

  name        = "${local.full_name_env_app}-fargate-tg-8000"
  port        = "8000"
  protocol    = "HTTP"
  vpc_id      = aws_vpc.backend_project_vpc[0].id
  target_type = "ip"

  health_check {
    matcher  = "200"
    protocol = "HTTP"
  }
}

# Listener (redirects traffic from the load balancer to the target group)
resource "aws_lb_listener" "fargate_http_listener" {
  count = var.create_vpc || var.create_load_balancer ? 1 : 0

  load_balancer_arn = aws_lb.fargate_alb[0].arn
  port              = "80"
  protocol          = "HTTP"
  # ssl_policy        = "ELBSecurityPolicy-2016-08"
  # certificate_arn   = "" #TODO: to create in acm

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fargate_targat_group_http[0].arn
  }
}
