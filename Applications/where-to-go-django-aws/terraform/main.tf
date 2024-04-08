module "basic_deployment" {
  source = "./modules/basic-deployment"

  #General variables
  project_name = var.project_name
  environment  = var.environment
  application  = var.application

  #ECR
  image_tag_mutability = "MUTABLE"
  scan_on_push         = true
  image_name           = var.application

}

module "ecs_deployment" {
  source = "./modules/ecs-deployment"

  #General variables
  region       = var.region
  environment  = var.environment
  project_name = var.project_name
  application  = var.application

  #VPC
  create_vpc             = true
  cidr                   = var.vpc_cidr_block
  create_igw             = true
  create_nat_gw          = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true
  map_public_ip          = true

  private_subnets   = var.private_subnet_ips
  public_subnets    = var.public_subnet_ips
  availability_zone = var.availability_zone

  #Cloudwatch
  log_retention_in_days = 7

  #ALB
  create_load_balancer = true #Application LB

  #ECS
  image_tag = var.image_tag
}

