resource "aws_security_group" "control_plane_sg" {
  vpc_id = aws_vpc.backend_project_vpc[0].id

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "SG for PoC Control Plane"
  }
}