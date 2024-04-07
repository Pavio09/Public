variable "environment" {
  type = string
}

variable "application" {
  type    = string
  default = "EKS"
}

variable "project_name" {
  type    = string
  default = "PoC"
}

variable "vpc_cidr_block" {
  type = string
}

variable "public_subnet_ips" {
  type    = list(string)
  default = []
}

variable "private_subnet_ips" {
  type    = list(string)
  default = []
}

variable "availability_zone" {
  type    = list(string)
  default = []
}

variable "region" {
  type    = string
  default = "eu-west-1"
}