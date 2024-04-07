variable "create_vpc" {
  type = bool
}

variable "subnet_names" {
  type    = list(string)
  default = ["0", "1", "2"]
}

variable "cidr" {
  type = string
}

variable "private_subnets" {
  type    = list(string)
  default = []
}

variable "public_subnets" {
  type    = list(string)
  default = []
}

variable "availability_zone" {
  type    = list(string)
  default = []
}

variable "log_retention_in_days" {
  type    = number
  default = 7
}

variable "environment" {
  type = string
}

variable "project_name" {
  type = string
}

variable "application" {
  type = string
}

variable "scan_on_push" {
  type    = bool
  default = true
}

variable "expiration_after_days" {
  type    = number
  default = 0
}

variable "region" {
  type = string
}

variable "create_igw" {
  type    = bool
  default = false
}

variable "create_load_balancer" {
  type    = bool
  default = false
}

variable "create_nat_gw" {
  type    = bool
  default = false
}

variable "single_nat_gateway" {
  type = bool
}

variable "one_nat_gateway_per_az" {
  type = bool
}

variable "map_public_ip" {
  type    = bool
  default = false
}

data "aws_caller_identity" "current" {}

locals {
  account_id        = data.aws_caller_identity.current.account_id
  full_name_env_app = "${var.environment}-${var.project_name}"
  image_path        = "${local.account_id}.dkr.ecr.${var.region}.amazonaws.com/${local.full_name_env_app}"
}

