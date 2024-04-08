environment         = "dev"
vpc_cidr_block      = "10.0.0.0/16"
availability_zone   = ["eu-west-1a", "eu-west-1b"]
private_subnet_ips  = ["10.0.4.0/24", "10.0.5.0/24"]
public_subnet_ips   = ["10.0.1.0/24", "10.0.2.0/24"]
image_tag = "0.1.12"