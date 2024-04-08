terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

#TODO: add dynamodb_table

provider "aws" {
  region = "eu-west-1"

  default_tags {
    tags = {
      "application" = var.application
      "environment" = var.environment
      "terraform"   = "true"
    }
  }
}
