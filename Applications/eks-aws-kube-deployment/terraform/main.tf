module "poc_deployment" {
  source = "./modules/poc-deployment"

  # General variables
  region       = var.region
  environment  = var.environment
  project_name = var.project_name
  application  = var.application

  # VPC
  create_vpc             = true
  cidr                   = var.vpc_cidr_block
  create_igw             = true
  create_nat_gw          = false
  single_nat_gateway     = false
  one_nat_gateway_per_az = false
  map_public_ip          = true

  private_subnets   = var.private_subnet_ips
  public_subnets    = var.public_subnet_ips
  availability_zone = var.availability_zone
}